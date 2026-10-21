"""
Mapping Agent: structural + semantic mapping, table-aware AND
batch-aware. Two mechanisms (see app/tools/mapping/omop_target_schema.py
for the full rationale):

  1. ROW-LEVEL DOMAIN ROUTING, for the 5 clinical event tables
     (condition_occurrence, drug_exposure, measurement,
     procedure_occurrence, observation): search_concept() resolves a
     concept_id whose domain_id tells us which table a SOURCE ROW
     belongs in. Driven by the `standard` declared in this batch's
     metadata.yaml.

  2. TARGET-FIRST FIELD RESOLUTION, for ALL 9 in-scope tables: for
     EVERY field a table actually has (introspected from the real,
     already-instantiated OMOP DDL - never a hand-picked subset), the
     LLM proposes which source (table, field) fills it, working across
     every table discovered in the batch. Vocabulary-bound fields (e.g.
     gender_concept_id, condition_type_concept_id - declared in
     app/config/reference/omop_vocabulary_fields.yaml, a human-provided
     file, never agent-generated) are resolved AUTOMATICALLY from their
     paired plain field once the LLM finds it - no extra LLM call, no
     per-batch declaration.

Uses the SAME batch_metadata the Profiling Agent read for this exact
batch (passed via state), and the SAME profiling facts (sample values)
Profiling already computed.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from app.agents.base import BaseAgent
from app.prompts.structural_target_mapping_prompt import (
    STRUCTURAL_PLAIN_FIELD_RETRY_PROMPT,
    STRUCTURAL_TARGET_MAPPING_PROMPT,
    STRUCTURAL_TARGET_MAPPING_RETRY_PROMPT,
)
from app.schemas.agent_result import AgentResult, AgentStatus
from app.schemas.mapping_record import MappingRecord
from app.schemas.structural_target_mapping import StructuralTargetMapping
from app.tools.common.io_utils import run_dir
from app.tools.common.llm_utils import parse_json_response
from app.tools.data.fhir_code_systems import (
    build_system_code_keys,
    derive_fhir_declarations,
    load_fhir_reference,
    parse_from_system,
    split_system_code_key,
    standard_for_system,
)
from app.tools.data.fhir_fixed_mappings import derive_fhir_fixed_mappings
from app.tools.data.metadata_loader import get_declared_fields_for_table, source_root_path
from app.tools.mapping.omop_schema_introspection import get_table_columns
from app.tools.mapping.omop_target_schema import (
    IN_SCOPE_TABLES,
    TABLE_FIELD_TEMPLATES,
    find_paired_source_value_field,
    get_vocabulary_fields,
    resolve_target,
)
from app.tools.mapping.local_vocab_resolver import (
    apply_local_vocab_join,
    resolve_local_vocab_join,
    search_concept_exact_only,
)
from app.tools.mapping.fixed_value_mappings import (
    get_concept_domain,
    get_fixed_mapping_spec,
    get_fixed_mapping_spec_by_source,
    load_fixed_mapping_table,
    resolve_fixed_value,
)
from app.tools.mapping.mapping_cache import ensure_mapping_cache_table
from app.tools.mapping.mapping_snapshot import (
    ReplayPlan,
    compute_value_drift,
    get_vocabulary_version,
    load_snapshot,
)
from app.tools.mapping.semantic.semantic_mapper import map_concept, resolve_concept_pair
from app.tools.mapping.structural.structural_mapper import build_structural_mapping
from app.tools.staging.staging_writer import write_initial_staging

# Domains already handled by mechanism 1 (domain-driven semantic mapping,
# resolved via the batch's declared `standard`) - these are OMOP DOMAINS,
# not valid vocabulary_id values, so they must never be queried directly
# via the generic vocab-field pairing mechanism (that mechanism is for
# genuinely fixed/closed vocabularies like Gender, Race, Ethnicity).
EVENT_DOMAINS_HANDLED_BY_MECHANISM_1 = {"Condition", "Drug", "Measurement", "Procedure", "Observation"}

# A vocab-field resolution (e.g. visit_concept_id) is retried with a
# DIFFERENT source column when its paired source_value field's initial
# choice produces a 0% match rate against the vocabulary - a strong
# signal the chosen column, despite looking plausible by name/samples,
# doesn't actually hold the right kind of value (confirmed in
# production: visit_source_value <- encounters.CODE, a specific
# clinical reason code, gave 0% against the Visit vocabulary).
# 2 = one initial attempt + one retry - a single targeted correction,
# never an open-ended search loop.
MAX_VOCAB_FIELD_RESOLUTION_ATTEMPTS = 2

# Used only by a fixed-mapping's optional "force_target_table" - the
# domain that CORRESPONDS to each of this project's 5 domain-driven
# target tables, needed to call resolve_target() with the FORCED table
# in mind rather than a concept's own actual domain. A declared
# business rule (e.g. the official MIT-LCP/mimic-omop ETL's documented
# "datetimeevents always -> OBSERVATION", confirmed in its own README)
# can override routing-by-domain entirely for a specific fixed-mapped
# field this way.
_TARGET_TABLE_TO_DOMAIN = {
    "condition_occurrence": "Condition",
    "drug_exposure": "Drug",
    "procedure_occurrence": "Procedure",
    "measurement": "Measurement",
    "observation": "Observation",
}


class MappingAgent(BaseAgent):
    name = "mapping_agent"
    stage = "mapping"

    # Set by run() when a mapping snapshot is replayed (see
    # app/tools/mapping/mapping_snapshot.py); None in a normal run.
    _replay: ReplayPlan | None = None

    def __init__(self, llm=None):
        super().__init__(llm)
        # Decisions recorded while resolving the target fields, exported in
        # the output so that a validated run can be saved as a snapshot.
        self._plain_scopes: list[dict] = []
        self._vocab_sources: list[dict] = []

    def _build_replay_plan(
        self, state: dict[str, Any], tables: dict[str, Any], batch_cfg: dict, source_name: str,
        source_folder: Path | None,
    ) -> ReplayPlan | None:
        """A plan when the run was started with a mapping snapshot to replay
        (state["mapping_replay"] = {"name": ..., "on_mismatch": ...}); None
        otherwise. Raises MappingReplayError for a snapshot that cannot be
        used at all (another source, another CDM version)."""
        cfg = state.get("mapping_replay")
        if not cfg:
            return None
        return ReplayPlan(
            load_snapshot(source_name, cfg["name"]),
            tables=tables, batch_cfg=batch_cfg, source_name=source_name, source_folder=source_folder,
            on_mismatch=cfg.get("on_mismatch", "fallback"),
            cdm_version=os.getenv("CDM_VERSION", "5.4"),
            vocabulary_version=get_vocabulary_version(),
        )

    def run(self, state: dict[str, Any]) -> AgentResult:
        ensure_mapping_cache_table()

        source_name = state["source_name"]
        batch_cfg = state["batch_metadata"]
        tables = state["_raw_tables"]
        execution_id = state["execution_id"]
        source_folder = source_root_path(source_name)

        # A FHIR batch is self-describing: every code travels with the URI
        # of its coding system. The coded fields of the clinical events are
        # therefore derived from the data instead of being declared by hand;
        # a declaration written in metadata.yaml always takes precedence.
        fhir_code_systems: dict[str, str] = {}
        fhir_derived_declarations: list[dict] = []
        fhir_derived_fixed_mappings: list[dict] = []
        if batch_cfg.get("format") == "fhir":
            fhir_reference = load_fhir_reference()
            fhir_code_systems = fhir_reference["code_systems"]
            batch_cfg, fhir_derived_declarations = derive_fhir_declarations(tables, batch_cfg, fhir_reference)
            # The value sets FHIR itself defines (race and ethnicity categories,
            # class of an encounter) have a curated mapping shared by every
            # FHIR source, added here unless the batch declares its own.
            batch_cfg, fhir_derived_fixed_mappings = derive_fhir_fixed_mappings(tables, batch_cfg)

        self._replay = self._build_replay_plan(state, tables, batch_cfg, source_name, source_folder)

        profiling_per_table = state.get("profiling_output", {}).get("per_table", {})
        tables_summary = self._build_tables_summary(tables, profiling_per_table)

        # --- Mechanism 1: row-level domain routing + staging (every table) --
        per_table_output: dict[str, Any] = {}
        all_mapping_records: list[MappingRecord] = []
        local_joins_used: dict[str, dict] = {}
        local_vocab_join_failures: dict[str, str] = {}
        from_system_failures: dict[str, str] = {}
        enriched_tables: dict[str, Any] = {}

        for table_name, df in tables.items():
            business_columns = [c for c in df.columns if not c.startswith("_")]
            structural_mapping = build_structural_mapping(business_columns)

            declared_fields = get_declared_fields_for_table(batch_cfg, table_name)
            table_mapping_records: list[MappingRecord] = []
            enriched_df = df.copy()

            # Case-insensitive column matching - the same robustness
            # principle as table-name matching (see metadata_loader.py):
            # a declared field name's case (however metadata.yaml
            # happens to spell it) must not determine whether it's
            # found, since real source exports vary in convention.
            column_lookup = {c.lower(): c for c in df.columns}

            for field in declared_fields:
                standard = field.get("standard")
                declared_field_name = field["name"]
                field_name = column_lookup.get(declared_field_name.lower())
                if not standard or standard == "none" or field_name is None:
                    continue

                search_source = df[field_name]  # default: raw field values are searched directly
                effective_standard = standard
                use_exact_only = False

                # `from_system:<column>`: the vocabulary is not fixed for the
                # whole column but decided for each value by the coding system
                # found next to it, so a column can mix several vocabularies.
                # The values to resolve become (system, code) pairs.
                system_field_name = parse_from_system(standard)
                if system_field_name is not None:
                    system_column = column_lookup.get(system_field_name.lower())
                    if system_column is None:
                        from_system_failures[f"{table_name}.{field_name}"] = (
                            f"System column '{system_field_name}' not found in this table"
                        )
                        continue
                    search_source = build_system_code_keys(df[system_column], df[field_name])

                # A human-curated fixed mapping, keyed by this SOURCE
                # table/field (not a target - unlike a vocab-field such
                # as race_concept_id, a local vocab field's target table
                # isn't known until AFTER routing by domain), takes
                # ABSOLUTE PRIORITY over the join+search pipeline below,
                # checked per-value inside the resolution loop further
                # down. Loaded once here, reused for every value.
                fixed_spec = get_fixed_mapping_spec_by_source(batch_cfg or {}, table_name, field_name)
                fixed_table = None
                if fixed_spec and source_folder is not None:
                    fixed_table = load_fixed_mapping_table(source_folder, fixed_spec)

                if standard == "local":
                    # Explicitly flagged in metadata.yaml as an internal
                    # reference, not a real code (e.g. MIMIC-III's
                    # ITEMID) - resolve the join to a dictionary table
                    # FIRST. This question is only ever asked for fields
                    # explicitly marked "local", never for a normally-
                    # declared coded field - no LLM call wasted on
                    # fields that plainly don't need it, and nothing
                    # here is specific to any one source: any batch
                    # whose metadata.yaml marks a field "local" gets the
                    # exact same treatment.
                    sample_values = df[field_name].dropna().unique()[:5].tolist()
                    join_spec = None
                    join_replayed = False
                    if self._replay is not None:
                        outcome, payload = self._replay.local_join(table_name, field_name)
                        if outcome == "failed":
                            local_vocab_join_failures[f"{table_name}.{field_name}"] = payload
                            continue
                        if outcome == "hit":
                            join_spec, join_replayed = payload, True
                    if join_spec is None:
                        join_spec = resolve_local_vocab_join(
                            self.llm, table_name, field_name, sample_values, tables_summary, source_name=source_name
                        )
                    if join_spec is None:
                        local_vocab_join_failures[f"{table_name}.{field_name}"] = (
                            "LLM could not propose a valid join (incomplete response or unresolvable reference)"
                        )
                        continue  # couldn't resolve this reference at all - skip, never guess
                    dictionary_df = tables.get(join_spec["join_table"])
                    if dictionary_df is None:
                        local_vocab_join_failures[f"{table_name}.{field_name}"] = (
                            f"Proposed dictionary table '{join_spec['join_table']}' not found in this batch"
                        )
                        continue
                    joined_values = apply_local_vocab_join(df, dictionary_df, join_spec)
                    if joined_values is None:
                        if join_replayed:
                            self._replay.join_rejected(
                                table_name, field_name, "failed the real-overlap check on this batch"
                            )
                        local_vocab_join_failures[f"{table_name}.{field_name}"] = (
                            f"Join to '{join_spec['join_table']}' via {join_spec['join_key_source']}/"
                            f"{join_spec['join_key_target']} failed the minimum real-overlap check "
                            f"(MIN_JOIN_OVERLAP) - proposed keys likely don't actually correspond"
                        )
                        continue  # join proposal failed real-overlap validation - rejected
                    search_source = joined_values
                    local_joins_used[f"{table_name}.{field_name}"] = join_spec
                    resolved_standards = join_spec.get("resolved_standards") or []
                    if join_spec["resolved_kind"] == "code" and resolved_standards:
                        effective_standard = resolved_standards[0]
                    elif resolved_standards:
                        # Free text (e.g. D_ITEMS.LABEL, "Heart Rate") -
                        # only an EXACT match is ever accepted, never
                        # substring or fuzzy. A full clinical phrase is
                        # far more likely to coincidentally resemble an
                        # unrelated concept via approximate matching
                        # than a short categorical value is - producing
                        # no match at all is better than a silently
                        # wrong one here. Multiple candidate vocabularies
                        # are tried in order (see search_concept_exact_only) -
                        # this is what lets a single field mix different
                        # kinds of values correctly (e.g. a drug/fluid
                        # administration table's items are usually
                        # drugs, but sometimes a measurement).
                        effective_standards = resolved_standards
                        use_exact_only = True
                    else:
                        # No plausible vocabulary was found for this
                        # free-text field (e.g. "INV#1 Dsg Change [MM]"
                        # is too source-specific to match any standard
                        # vocabulary by text search) - before giving up,
                        # check for a human-curated fixed mapping keyed
                        # by the RAW item identifier itself (not the
                        # joined label - confirmed necessary: several
                        # MIMIC event tables' items have NO text match
                        # anywhere, yet a curated mapping (verified
                        # against real OMOP concepts) DOES exist for
                        # many of them).
                        if fixed_table is not None:
                            # A declared business rule (e.g. the
                            # official MIT-LCP/mimic-omop ETL documents
                            # "datetimeevents always -> OBSERVATION",
                            # confirmed in its own README) can override
                            # routing-by-domain entirely for this field -
                            # reuses resolve_target() with the domain
                            # that CORRESPONDS to the forced table,
                            # rather than each concept's own actual
                            # domain, so every value lands in the same
                            # declared table regardless of what domain
                            # its own concept_id happens to belong to.
                            forced_table = fixed_spec.get("force_target_table")
                            forced_domain = _TARGET_TABLE_TO_DOMAIN.get(forced_table) if forced_table else None

                            raw_values = df[field_name].dropna().unique()
                            value_to_concept_id = {}
                            value_to_source_concept_id = {}
                            value_to_target_table = {}
                            for raw_value in raw_values:
                                candidate = resolve_fixed_value(str(raw_value), fixed_table, fixed_spec)
                                if candidate is None:
                                    continue  # this specific item isn't covered by the CSV
                                if forced_domain:
                                    domain = forced_domain
                                else:
                                    domain = get_concept_domain(candidate["concept_id"])
                                target = resolve_target(domain) if domain else None
                                value_to_concept_id[str(raw_value)] = candidate["concept_id"]
                                value_to_source_concept_id[str(raw_value)] = candidate.get("source_concept_id")
                                value_to_target_table[str(raw_value)] = target["table"] if target else None
                                table_mapping_records.append(MappingRecord(
                                    source=source_name, field=f"{table_name}.{field_name}",
                                    standard="fixed_mapping", source_value=str(raw_value),
                                    target_concept_id=candidate["concept_id"],
                                    source_concept_id=candidate.get("source_concept_id"),
                                    target_source_concept_field=target.get("source_concept_field") if target else None,
                                    target_table=target["table"] if target else None,
                                    target_concept_field=target["concept_field"] if target else None,
                                    target_source_value_field=target["source_value_field"] if target else None,
                                    confidence=1.0,
                                    reason="Resolved via human-curated fixed mapping (takes priority over automatic search)",
                                ))
                            if value_to_concept_id:
                                concept_column = f"{field_name}_concept_id"
                                source_concept_column = f"{field_name}_source_concept_id"
                                target_table_column = f"{field_name}_target_table"
                                enriched_df[concept_column] = df[field_name].astype(str).map(value_to_concept_id)
                                enriched_df[source_concept_column] = df[field_name].astype(str).map(value_to_source_concept_id)
                                enriched_df[target_table_column] = df[field_name].astype(str).map(value_to_target_table)
                        continue  # text with no plausible target vocabulary at all - nothing more to search

                distinct_values = search_source.dropna().unique()
                value_to_concept_id: dict[str, int | None] = {}
                value_to_source_concept_id: dict[str, int | None] = {}
                value_to_target_table: dict[str, str | None] = {}
                for value in distinct_values:
                    key = str(value)
                    lookup_value = key
                    value_standard = effective_standard
                    if system_field_name is not None:
                        system_uri, lookup_value = split_system_code_key(key)
                        value_standard = standard_for_system(system_uri, fhir_code_systems)
                        if value_standard is None:
                            # A coding system the framework cannot search: the
                            # value stays unresolved, with the reason on record,
                            # instead of being forced into a wrong vocabulary.
                            value_to_concept_id[key] = None
                            value_to_source_concept_id[key] = None
                            value_to_target_table[key] = None
                            table_mapping_records.append(MappingRecord(
                                source=source_name,
                                field=f"{table_name}.{field_name}",
                                standard="unknown_system",
                                source_value=lookup_value,
                                target_concept_id=None,
                                source_concept_id=None,
                                target_source_concept_field=None,
                                target_table=None,
                                target_concept_field=None,
                                target_source_value_field=None,
                                confidence=0.0,
                                reason=(
                                    f"Coding system '{system_uri}' is not known to the framework "
                                    f"(see fhir_code_systems.yaml) - value left unresolved."
                                ),
                            ))
                            continue
                    if use_exact_only:
                        # Free-text resolution (e.g. a local dictionary's
                        # LABEL column) - no source/standard distinction
                        # applies here (there is no separate "source
                        # vocabulary" for a plain description), and only
                        # an EXACT match is ever accepted.
                        exact_match = search_concept_exact_only(lookup_value, effective_standards)
                        resolved = {"source_concept": exact_match, "standard_concept": exact_match}
                    else:
                        resolved = resolve_concept_pair(lookup_value, value_standard)
                    source_concept = resolved["source_concept"]
                    standard_concept = resolved["standard_concept"]

                    # Route using the STANDARD concept's domain when
                    # available (the correct OMOP convention - routing
                    # decisions belong to the standard representation),
                    # falling back to the source concept's OWN domain
                    # only when it has no "Maps to" target at all, so a
                    # genuinely classification-only code still has a
                    # reasonable chance of landing in the right table
                    # rather than being dropped outright.
                    domain_for_routing = (
                        standard_concept.get("domain_id") if standard_concept
                        else (source_concept.get("domain_id") if source_concept else None)
                    )
                    target = resolve_target(domain_for_routing) if domain_for_routing else None

                    value_to_concept_id[key] = standard_concept["concept_id"] if standard_concept else None
                    value_to_source_concept_id[key] = source_concept["concept_id"] if source_concept else None
                    value_to_target_table[key] = target["table"] if target else None

                    if use_exact_only:
                        reason = (
                            f"Exact text match found in '{value_standard}'" if source_concept
                            else f"No EXACT match in '{value_standard}' - approximate matching is "
                                 f"deliberately disabled for free-text local vocabulary values."
                        )
                    elif source_concept is None:
                        reason = f"No candidate found in vocabulary '{value_standard}'"
                    elif standard_concept is None:
                        reason = (
                            f"Found source concept {source_concept['concept_id']} "
                            f"('{source_concept['concept_name']}') in '{value_standard}', but it has no "
                            f"'Maps to' Standard equivalent."
                        )
                    elif standard_concept is source_concept:
                        reason = f"'{value_standard}' is itself a Standard vocabulary - source and standard concept are the same."
                    else:
                        reason = (
                            f"Source concept {source_concept['concept_id']} in '{value_standard}' maps to "
                            f"Standard concept {standard_concept['concept_id']} via 'Maps to'."
                        )

                    table_mapping_records.append(MappingRecord(
                        source=source_name,
                        field=f"{table_name}.{field_name}",
                        standard=value_standard,
                        source_value=lookup_value,
                        target_concept_id=standard_concept["concept_id"] if standard_concept else None,
                        source_concept_id=source_concept["concept_id"] if source_concept else None,
                        target_source_concept_field=target.get("source_concept_field") if target else None,
                        target_table=target["table"] if target else None,
                        target_concept_field=target["concept_field"] if target else None,
                        target_source_value_field=target["source_value_field"] if target else None,
                        confidence=(
                            source_concept.get("_match_confidence", 0.0) if source_concept else 0.0
                        ),
                        reason=reason,
                    ))

                concept_column = f"{field_name}_concept_id"
                source_concept_column = f"{field_name}_source_concept_id"
                enriched_df[concept_column] = search_source.astype(str).map(value_to_concept_id)
                enriched_df[source_concept_column] = search_source.astype(str).map(value_to_source_concept_id)
                # Per-row target table, so the Loading Agent can group
                # rows of THIS source table by which OMOP table they
                # actually belong to (a same source table can produce
                # rows for different target tables depending on each
                # value's resolved domain).
                target_table_column = f"{field_name}_target_table"
                enriched_df[target_table_column] = search_source.astype(str).map(value_to_target_table)

            staging_table = write_initial_staging(f"{source_name}_{table_name}", enriched_df, execution_id)
            enriched_tables[table_name] = enriched_df

            all_mapping_records.extend(table_mapping_records)
            per_table_output[table_name] = {
                "staging_table": staging_table,
                "structural_mapping": structural_mapping,
                "semantic_mapping": [m.model_dump(mode="json") for m in table_mapping_records],
            }

        state["_enriched_tables"] = enriched_tables

        # --- Mechanism 2: target-first field resolution (all 9 tables) ------
        structural_targets, vocab_field_retry_log = self._resolve_all_target_fields(
            tables, enriched_tables, profiling_per_table,
            batch_cfg=batch_cfg, source_folder=source_folder,
        )

        output = {
            "per_table": per_table_output,
            "structural_target_mappings": [m.model_dump(mode="json") for m in structural_targets],
            "local_vocab_joins": local_joins_used,
            "local_vocab_join_failures": local_vocab_join_failures,
            "from_system_failures": from_system_failures,
            "fhir_derived_declarations": fhir_derived_declarations,
            "fhir_derived_fixed_mappings": fhir_derived_fixed_mappings,
            "vocab_field_retry_log": vocab_field_retry_log,
            # What a snapshot needs in order to replay the model's decisions.
            "plain_field_scopes": list(self._plain_scopes),
            "vocab_field_sources": list(self._vocab_sources),
        }
        replay_note = ""
        if self._replay is not None:
            self._replay.report["value_drift"] = compute_value_drift(self._replay.snapshot.get("mapping", {}), output)
            output["replay"] = self._replay.report
            replay_note = (
                f" Replayed snapshot '{self._replay.name}': {sum(self._replay.report['reused'].values())} "
                f"decision(s) reused, {len(self._replay.report['fallbacks'])} resolved the normal way."
            )

        result = AgentResult(
            execution_id=execution_id,
            agent_name=self.name,
            status=AgentStatus.SUCCESS,
            output=output,
            tools_used=[
                "build_structural_mapping", "write_initial_staging", "map_concept",
                "resolve_target", "get_table_columns", "find_paired_source_value_field",
            ],
            reasoning_summary=(
                f"Mapped {len(tables)} table(s) via domain routing; "
                f"{len(all_mapping_records)} semantic mappings attempted; "
                f"{len(structural_targets)} target field(s) resolved across "
                f"{len(IN_SCOPE_TABLES)} OMOP table(s)."
            ) + replay_note,
        )
        report = self._build_report(structural_targets, per_table_output)
        if self._replay is not None:
            report += "\n\n" + self._replay.markdown_section()
        result = self.persist(result, report_markdown=report)

        report_csv = self._build_report_csv(structural_targets, per_table_output)
        csv_path = run_dir(execution_id, self.stage) / "report.csv"
        csv_path.write_text(report_csv, encoding="utf-8")

        return result

    @staticmethod
    def _build_report_csv(structural_targets: list[StructuralTargetMapping], per_table_output: dict) -> str:
        """The same information as _build_report, as CSV instead of a
        markdown table - easier to load into pandas/Excel for
        systematic analysis (e.g. comparing against an external
        reference's own mapping spec) than parsing markdown tables.
        One combined CSV, with a `section` column distinguishing the
        two logical sections (structural field resolution vs semantic
        vocabulary mapping), since they have different natural columns."""
        import csv
        import io

        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow([
            "section", "status", "target_table", "target_field", "source_table", "source_field",
            "standard", "confidence", "matched", "unmatched", "reason",
        ])

        by_table: dict[str, list] = {}
        for m in structural_targets:
            by_table.setdefault(m.target_table, []).append(m)

        for target_table in sorted(by_table):
            by_field: dict[str, list] = {}
            for m in by_table[target_table]:
                by_field.setdefault(m.target_field, []).append(m)

            for target_field in sorted(by_field):
                records = by_field[target_field]
                if len(records) > 1 and all(r.source_value is not None for r in records):
                    matched = sum(1 for r in records if r.target_concept_id is not None)
                    unmatched = len(records) - matched
                    status = "OK" if matched > 0 else "FAIL"
                    writer.writerow([
                        "structural_field", status, target_table, target_field,
                        records[0].source_table or "", records[0].source_field or "",
                        "", "", matched, unmatched, f"{len(records)} valeurs distinctes",
                    ])
                    continue

                for m in records:
                    resolved = bool(m.source_table and m.source_field)
                    status = "OK" if resolved else "FAIL"
                    writer.writerow([
                        "structural_field", status, target_table, target_field,
                        m.source_table or "", m.source_field or "",
                        "", m.confidence if m.confidence is not None else "", "", "",
                        (m.reason or "").replace("\n", " "),
                    ])

        for source_table_name, info in sorted(per_table_output.items()):
            semantic = info.get("semantic_mapping", [])
            if not semantic:
                continue
            by_field: dict[str, list] = {}
            for entry in semantic:
                by_field.setdefault(entry["field"], []).append(entry)
            for field_name, entries in sorted(by_field.items()):
                matched = sum(1 for e in entries if e.get("target_concept_id") is not None)
                unmatched = len(entries) - matched
                standard = entries[0].get("standard", "")
                writer.writerow([
                    "semantic_mapping", "OK" if matched > 0 else "FAIL", "", "",
                    source_table_name, field_name, standard, "", matched, unmatched, "",
                ])

        return buffer.getvalue()

    @staticmethod
    def _build_report(structural_targets: list[StructuralTargetMapping], per_table_output: dict) -> str:
        """A clear table - not just JSON - showing exactly which source
        column fills each OMOP target column, with unresolved fields
        explicitly flagged (❌), so a failure like 'visit_start_date
        never got a source' is visible at a glance rather than buried
        in the mapping_output JSON."""
        lines = ["# Mapping Agent Report", "", "## Résolution des champs cibles (9 tables OMOP)", ""]
        lines.append("| Statut | Table cible | Champ cible | Table source | Champ source | Confiance | Raison |")
        lines.append("|---|---|---|---|---|---|---|")

        by_table: dict[str, list] = {}
        for m in structural_targets:
            by_table.setdefault(m.target_table, []).append(m)

        for target_table in sorted(by_table):
            by_field: dict[str, list] = {}
            for m in by_table[target_table]:
                by_field.setdefault(m.target_field, []).append(m)

            for target_field in sorted(by_field):
                records = by_field[target_field]
                if len(records) > 1 and all(r.source_value is not None for r in records):
                    # Vocabulary field resolved once PER DISTINCT VALUE
                    # (e.g. one row per unit/ethnicity/race category) -
                    # aggregated into a single summary row instead of
                    # listing every value, which made the report
                    # unreadable for fields with many distinct values.
                    matched = sum(1 for r in records if r.target_concept_id is not None)
                    unmatched = len(records) - matched
                    source_table = records[0].source_table or "—"
                    source_field = records[0].source_field or "—"
                    status = "✅" if matched > 0 else "❌"
                    lines.append(
                        f"| {status} | {target_table} | {target_field} | {source_table} | {source_field} "
                        f"| — | {matched} valeur(s) distincte(s) résolue(s), {unmatched} non résolue(s) sur {len(records)} |"
                    )
                    continue

                # A plain field can legitimately have MULTIPLE
                # resolutions - one per contributing source table (see
                # _find_contributing_source_tables) - e.g.
                # drug_exposure.person_id resolved independently for
                # immunizations, medications, AND procedures, since all
                # three route rows into drug_exposure. Show every one,
                # not just the first - silently hiding the others made
                # a working mechanism look broken.
                for m in records:
                    resolved = bool(m.source_table and m.source_field)
                    status = "✅" if resolved else "❌"
                    source_table = m.source_table or "—"
                    source_field = m.source_field or "—"
                    confidence = f"{m.confidence:.2f}" if m.confidence is not None else "—"
                    reason = (m.reason or "").replace("\n", " ")[:100]
                    lines.append(f"| {status} | {target_table} | {target_field} | {source_table} | {source_field} | {confidence} | {reason} |")

        lines += ["", "## Mapping sémantique par domaine (5 tables événement)", ""]
        lines.append("| Table source | Champ | Standard | Valeurs mappées | Valeurs non mappées |")
        lines.append("|---|---|---|---|---|")
        for source_table_name, info in sorted(per_table_output.items()):
            semantic = info.get("semantic_mapping", [])
            if not semantic:
                continue
            by_field: dict[str, list] = {}
            for entry in semantic:
                by_field.setdefault(entry["field"], []).append(entry)
            for field_name, entries in sorted(by_field.items()):
                matched = sum(1 for e in entries if e.get("target_concept_id") is not None)
                unmatched = len(entries) - matched
                standard = entries[0].get("standard", "—")
                lines.append(f"| {source_table_name} | {field_name} | {standard} | {matched} | {unmatched} |")

        unresolved_count = sum(1 for m in structural_targets if not (m.source_table and m.source_field))
        if unresolved_count:
            lines += ["", f"⚠️ **{unresolved_count} champ(s) cible(s) non résolu(s)** - voir les lignes ❌ ci-dessus pour la raison exacte donnée par le LLM."]

        return "\n".join(lines)

    def _resolve_all_target_fields(
        self, tables: dict[str, Any], enriched_tables: dict[str, Any], profiling_per_table: dict[str, Any],
        batch_cfg: dict | None = None, source_folder: Path | None = None,
    ) -> tuple[list[StructuralTargetMapping], dict]:
        """For every one of the 9 in-scope OMOP tables: get its REAL,
        complete field list (introspected, never hand-picked), split
        into vocabulary fields (resolved automatically once paired) and
        plain fields (resolved by the LLM), and combine. Returns
        (records, vocab_field_retry_log) - the latter documents every
        vocab-field resolution that needed a retry (see
        MAX_VOCAB_FIELD_RESOLUTION_ATTEMPTS), for full traceability of
        what was tried, what failed, and what finally worked.

        `tables` (raw, business columns only) feeds the LLM's summary;
        `enriched_tables` (with the `*_target_table` columns mechanism 1
        already attached) is used ONLY to find which source tables
        actually contribute rows to a given domain-driven target
        table - never sent to the LLM itself, to avoid polluting its
        prompt with internal bookkeeping columns."""
        tables_summary = self._build_tables_summary(tables, profiling_per_table)
        records: list[StructuralTargetMapping] = []
        vocab_field_retry_log: dict[str, dict] = {}
        plain_field_retry_log: dict[str, dict] = {}
        self._plain_scopes = []
        self._vocab_sources = []

        for target_table in IN_SCOPE_TABLES:
            try:
                columns_info = get_table_columns(target_table)
            except ValueError as exc:
                # OMOP DDL not instantiated / table missing - can't
                # resolve anything for this table, but don't crash the
                # whole batch over it.
                records.append(StructuralTargetMapping(
                    target_table=target_table, target_field="(all)",
                    reason=f"Could not introspect table: {exc}",
                ))
                continue

            all_fields = [c["column_name"] for c in columns_info]
            data_types = {c["column_name"]: c["data_type"] for c in columns_info}
            vocab_fields = get_vocabulary_fields(target_table)
            # Foreign keys into tables OUTSIDE our 9-table scope
            # (LOCATION, PROVIDER, CARE_SITE - never built) can NEVER be
            # validly resolved by ANY source value, no matter how
            # plausible it looks - a source UUID or an unrelated code
            # (e.g. a FIPS county code) is not a real foreign key just
            # because it's numeric-ish. Asking the LLM about these
            # invited exactly this: it explicitly reasoned "when a
            # dedicated location table is absent" and substituted FIPS
            # anyway, rather than correctly refusing. Excluded here so
            # the question is never even asked.
            out_of_scope_fk_fields = {"location_id", "provider_id", "care_site_id"}
            plain_fields = [f for f in all_fields if f not in vocab_fields and f not in out_of_scope_fk_fields]

            if target_table in TABLE_FIELD_TEMPLATES:
                # Domain-driven event table: MULTIPLE source tables can
                # independently contribute rows here (e.g. conditions.CODE
                # AND procedures.REASONCODE both route to
                # condition_occurrence) - each needs its OWN resolution
                # for fields like condition_start_date, since a single
                # batch-wide search would only ever find ONE source
                # table's date column, leaving every other contributing
                # table's rows with a null date despite a "correct"
                # mapping existing for a DIFFERENT table.
                contributing_sources = self._find_contributing_source_tables(enriched_tables, target_table)
                plain_resolutions = []
                for source_table_name in contributing_sources:
                    single_source_summary = {source_table_name: tables_summary.get(source_table_name, {})}
                    self._plain_scopes.append({"target_table": target_table, "source_table": source_table_name})
                    resolved, retry_log = self._resolve_plain_fields(
                        target_table, plain_fields, single_source_summary, data_types, scope_source=source_table_name
                    )
                    plain_resolutions.extend(resolved)
                    plain_field_retry_log.update(retry_log)
            else:
                self._plain_scopes.append({"target_table": target_table, "source_table": None})
                plain_resolutions, retry_log = self._resolve_plain_fields(
                    target_table, plain_fields, tables_summary, data_types
                )
                plain_field_retry_log.update(retry_log)
            records.extend(plain_resolutions)

            resolved_by_field = {r.target_field: r for r in plain_resolutions}
            for concept_field, vocabulary_domain in vocab_fields.items():
                if vocabulary_domain in EVENT_DOMAINS_HANDLED_BY_MECHANISM_1:
                    # condition_concept_id, drug_concept_id, etc. (and
                    # their _source_concept_id counterparts) are ALREADY
                    # resolved by mechanism 1's domain-driven routing,
                    # using the batch's declared `standard` (SNOMED/
                    # ICD10/...) - not by searching a vocabulary literally
                    # named "Condition"/"Drug"/etc. (those are OMOP
                    # DOMAINS, not valid vocabulary_id values; querying
                    # them would always fail). Re-attempting this here
                    # would be redundant AND wrong. See per_table's
                    # semantic_mapping for the real resolution.
                    records.append(StructuralTargetMapping(
                        target_table=target_table, target_field=concept_field,
                        reason="Handled by domain-driven semantic mapping (see per_table.semantic_mapping) - "
                               "not re-resolved here.",
                    ))
                    continue

                # A human-curated fixed mapping, declared in this
                # batch's metadata.yaml, takes ABSOLUTE PRIORITY over
                # the automatic LLM/vocabulary search - and, crucially,
                # NEVER depends on mechanism 2 having ALSO independently
                # resolved a paired source_value field. The spec already
                # declares its own source_table/source_field explicitly
                # - a human told us exactly where the raw values live,
                # so this must work even when the paired field was
                # never resolved at all (confirmed in production: race_
                # concept_id's own race_source_value pairing consistently
                # fails, which would otherwise block this fixed mapping
                # from ever being reached).
                fixed_spec = get_fixed_mapping_spec(batch_cfg or {}, target_table, concept_field)
                curated_source: tuple[str, str] | None = None   # set once the curated file has been applied
                uncovered_values: list[str] = []                # raw values that file does not cover
                if fixed_spec:
                    fixed_df = tables.get(fixed_spec["source_table"])
                    if fixed_df is not None and fixed_spec["source_field"] in fixed_df.columns:
                        fixed_table = None
                        if source_folder is not None:
                            fixed_table = load_fixed_mapping_table(source_folder, fixed_spec)
                        if fixed_table is not None:
                            curated_source = (fixed_spec["source_table"], fixed_spec["source_field"])
                            fixed_paired_field = find_paired_source_value_field(concept_field, all_fields)
                            fixed_paired_already_resolved = (
                                fixed_paired_field is not None
                                and resolved_by_field.get(fixed_paired_field) is not None
                                and resolved_by_field[fixed_paired_field].source_table
                            )
                            fixed_distinct_values = fixed_df[fixed_spec["source_field"]].dropna().unique()
                            any_uncovered = False
                            for value in fixed_distinct_values:
                                candidate = resolve_fixed_value(str(value), fixed_table, fixed_spec)
                                if candidate is None:
                                    any_uncovered = True
                                    uncovered_values.append(str(value))
                                    continue  # not covered by the CSV - let the normal path below handle it
                                records.append(StructuralTargetMapping(
                                    target_table=target_table, target_field=concept_field,
                                    source_table=fixed_spec["source_table"], source_field=fixed_spec["source_field"],
                                    source_value=str(value), target_concept_id=candidate["concept_id"],
                                    data_type=data_types.get(concept_field), confidence=1.0,
                                    reason="Resolved via human-curated fixed mapping (takes priority over automatic search)",
                                ))
                                # Also populate the paired source_value
                                # field (e.g. race_source_value) with the
                                # RAW TEXT itself - not the concept_id -
                                # since this field's only job is to
                                # preserve the original source value.
                                # Only done if mechanism 2 hasn't ALREADY
                                # resolved this field from elsewhere - a
                                # human's fixed mapping for the concept
                                # doesn't override an independently
                                # working source_value resolution.
                                if fixed_paired_field and not fixed_paired_already_resolved:
                                    records.append(StructuralTargetMapping(
                                        target_table=target_table, target_field=fixed_paired_field,
                                        source_table=fixed_spec["source_table"], source_field=fixed_spec["source_field"],
                                        source_value=str(value), target_concept_id=None,
                                        data_type=data_types.get(fixed_paired_field), confidence=1.0,
                                        reason="Raw source text preserved alongside a human-curated fixed mapping "
                                               "for the paired concept field",
                                    ))
                            if not any_uncovered:
                                # EVERY distinct value in the source was
                                # covered by the CSV - nothing left for
                                # the normal paired-field mechanism to
                                # do for this field at all. Skip it
                                # entirely, rather than relying on a
                                # post-hoc filter further down (which,
                                # even if correct, adds an unnecessary
                                # extra pass over the same data).
                                continue

                paired_field = find_paired_source_value_field(concept_field, all_fields)
                if paired_field is None:
                    records.append(StructuralTargetMapping(
                        target_table=target_table, target_field=concept_field,
                        data_type=data_types.get(concept_field),
                        reason="No paired source_value field for this table - "
                               "likely record provenance (needs a fixed ETL convention, not derivable from source data).",
                    ))
                    continue

                paired_resolution = resolved_by_field.get(paired_field)
                # Replay: the column this field was finally read from in the
                # snapshot's run (after any retry) wins over the plain
                # resolution of its paired source_value field.
                frozen_vocab_source = (
                    self._replay.vocab_source(target_table, concept_field) if self._replay is not None else None
                )
                if frozen_vocab_source is not None:
                    paired_resolution = StructuralTargetMapping(
                        target_table=target_table, target_field=paired_field,
                        source_table=frozen_vocab_source[0], source_field=frozen_vocab_source[1],
                        reason="Source column frozen from the replayed mapping snapshot.",
                    )
                if paired_resolution is None or not paired_resolution.source_table:
                    if not fixed_spec:  # only report this failure if no fixed mapping was even attempted
                        records.append(StructuralTargetMapping(
                            target_table=target_table, target_field=concept_field,
                            data_type=data_types.get(concept_field),
                            reason=f"Paired field '{paired_field}' was not resolved in this batch.",
                        ))
                    if curated_source is not None:
                        records.extend(self._unresolved_curated_records(
                            target_table, concept_field, fixed_spec, uncovered_values, data_types))
                    continue

                df = tables.get(paired_resolution.source_table)
                if df is None or paired_resolution.source_field not in df.columns:
                    continue

                # A curated mapping names the authoritative source column of
                # this field. If the automatic path would look in ANOTHER
                # column (the one the model chose for the paired source_value
                # field), its results would form a second group for the same
                # output column, and the Transformation Agent applies the
                # groups in turn: the later group would erase the curated one.
                # The raw values the curated file does not cover are
                # therefore left unresolved - and reported as such - instead
                # of being searched in the wrong column.
                if curated_source is not None and (
                    paired_resolution.source_table, paired_resolution.source_field
                ) != curated_source:
                    records.extend(self._unresolved_curated_records(
                        target_table, concept_field, fixed_spec, uncovered_values, data_types))
                    continue

                distinct_values = df[paired_resolution.source_field].dropna().unique()
                # Skip values already resolved via the fixed mapping above,
                # so they are never processed twice. (Defensive - the
                # early `continue` above already handles the common case
                # where EVERY value was covered; this also protects the
                # narrower case where the CSV covers only SOME values.)
                if fixed_spec:
                    already_covered = {
                        r.source_value for r in records
                        if r.target_table == target_table and r.target_field == concept_field
                    }
                    distinct_values = [v for v in distinct_values if str(v) not in already_covered]
                    if not distinct_values:
                        continue

                def _resolve_all(values):
                    resolved = []
                    for v in values:
                        c = map_concept(str(v), vocabulary_domain)
                        resolved.append((v, c))
                    return resolved

                attempt_log = []
                resolved_values = _resolve_all(distinct_values)
                match_rate = (
                    sum(1 for _, c in resolved_values if c is not None) / len(resolved_values)
                    if len(resolved_values) > 0 else 1.0  # no values at all isn't a resolution failure
                )
                attempt_log.append({
                    "source_table": paired_resolution.source_table, "source_field": paired_resolution.source_field,
                    "distinct_values": len(resolved_values), "match_rate": round(match_rate, 3),
                })

                retries_used = 0
                # The retry looks for a BETTER source column when the values of
                # the current one match nothing. A curated mapping has already
                # named the authoritative column of this field, so there is
                # nothing to look for: a retry would move the field to another
                # column and its unresolved results would erase the curated
                # ones (observed: the model proposed `encounters.CODE`, the
                # SNOMED type of the encounter, and every visit lost its
                # concept). The values the curated file does not cover stay
                # unresolved and visible in the report instead.
                while (
                    curated_source is None
                    and match_rate == 0.0 and len(resolved_values) > 0
                    and retries_used < MAX_VOCAB_FIELD_RESOLUTION_ATTEMPTS - 1
                ):
                    retries_used += 1
                    if self._replay is not None:
                        # The replayed column matches nothing on this batch:
                        # resolved the normal way (or the run stops, in
                        # strict mode).
                        self._replay.note_fallback(
                            "vocab_zero_match",
                            f"{target_table}.{concept_field}: {paired_resolution.source_table}."
                            f"{paired_resolution.source_field} matched no value of '{vocabulary_domain}'",
                        )
                    retry_prompt = STRUCTURAL_TARGET_MAPPING_RETRY_PROMPT.format(
                        target_table=target_table, vocabulary_domain=vocabulary_domain,
                        rejected_table=paired_resolution.source_table, rejected_field=paired_resolution.source_field,
                        tables_summary=json.dumps(tables_summary, indent=2, default=str),
                        target_field=paired_field,
                    )
                    response = self.llm.invoke(retry_prompt)
                    try:
                        retry_choice = parse_json_response(response.content)
                    except ValueError:
                        break
                    new_table, new_field = retry_choice.get("source_table"), retry_choice.get("source_field")
                    if not new_table or not new_field:
                        break  # LLM honestly found no better alternative - stop, don't guess further
                    new_df = tables.get(new_table)
                    if new_df is None or new_field not in new_df.columns:
                        break

                    paired_resolution = StructuralTargetMapping(
                        target_table=target_table, target_field=paired_field,
                        source_table=new_table, source_field=new_field,
                        confidence=retry_choice.get("confidence"), reason=retry_choice.get("reason", ""),
                    )
                    distinct_values = new_df[new_field].dropna().unique()
                    resolved_values = _resolve_all(distinct_values)
                    match_rate = (
                        sum(1 for _, c in resolved_values if c is not None) / len(resolved_values)
                        if len(resolved_values) > 0 else 1.0
                    )
                    attempt_log.append({
                        "source_table": new_table, "source_field": new_field,
                        "distinct_values": len(resolved_values), "match_rate": round(match_rate, 3),
                    })

                if len(attempt_log) > 1:
                    vocab_field_retry_log[f"{target_table}.{concept_field}"] = {
                        "attempts": attempt_log,
                        "final_outcome": "resolved" if match_rate > 0 else "all attempts failed",
                    }

                self._vocab_sources.append({
                    "target_table": target_table, "target_field": concept_field,
                    "source_table": paired_resolution.source_table, "source_field": paired_resolution.source_field,
                })
                for value, candidate in resolved_values:
                    records.append(StructuralTargetMapping(
                        target_table=target_table,
                        target_field=concept_field,
                        source_table=paired_resolution.source_table,
                        source_field=paired_resolution.source_field,
                        source_value=str(value),
                        target_concept_id=candidate["concept_id"] if candidate else None,
                        data_type=data_types.get(concept_field),
                        confidence=candidate.get("_match_confidence") if candidate else 0.0,
                        reason=(
                            "Resolved via human-curated fixed mapping (takes priority over automatic search)"
                            if candidate and candidate.get("_fixed_mapping")
                            else f"Resolved against fixed OMOP vocabulary '{vocabulary_domain}' "
                                 f"(paired with {paired_field})"
                            if candidate else f"No candidate found in vocabulary '{vocabulary_domain}'"
                        ),
                    ))
        vocab_field_retry_log["_plain_field_retries"] = plain_field_retry_log

        # Final safety net: deduplicate by (target_table, target_field,
        # source_value) - a human-curated fixed mapping ALWAYS wins over
        # an automatic resolution for the exact same value, no matter
        # which code path produced the conflicting automatic entry.
        # Added after repeatedly observing a value resolved correctly
        # via a fixed mapping ALSO end up with a second, failing
        # "No candidate found" record for the identical value (e.g.
        # "ambulatory" for visit_concept_id) - the precise code path
        # producing this second record was never conclusively
        # identified despite extensive tracing, so this deduplication
        # guards the OUTCOME directly rather than relying on preventing
        # the duplicate from ever being appended in the first place.
        best_by_key: dict[tuple, StructuralTargetMapping] = {}
        for r in records:
            if r.source_value is None:
                # Failure placeholders (no source_value at all) are
                # never deduplicated against each other - each one is
                # its own distinct, meaningful entry.
                best_by_key[id(r)] = r
                continue
            key = (r.target_table, r.target_field, r.source_value)
            existing = best_by_key.get(key)
            is_fixed = "human-curated" in (r.reason or "")
            existing_is_fixed = existing is not None and "human-curated" in (existing.reason or "")
            if existing is None or (is_fixed and not existing_is_fixed):
                best_by_key[key] = r
        records = list(best_by_key.values())

        return records, vocab_field_retry_log

    @staticmethod
    def _unresolved_curated_records(
        target_table: str, concept_field: str, fixed_spec: dict, values: list[str], data_types: dict[str, str],
    ) -> list[StructuralTargetMapping]:
        """One unresolved record per raw value that a curated mapping file
        does not cover, for the cases where the automatic search is not
        allowed to look for it. The value stays visible in the mapping report
        instead of silently disappearing, with the file to complete."""
        file_name = Path(str(fixed_spec["mapping_file"])).name
        return [
            StructuralTargetMapping(
                target_table=target_table, target_field=concept_field,
                source_table=fixed_spec["source_table"], source_field=fixed_spec["source_field"],
                source_value=str(value), target_concept_id=None,
                data_type=data_types.get(concept_field), confidence=0.0,
                reason=(
                    f"Value not covered by the curated mapping file '{file_name}' - left unresolved. "
                    f"Add a row to that file once the concept is confirmed."
                ),
            )
            for value in values
        ]

    @staticmethod
    def _find_contributing_source_tables(tables: dict[str, Any], target_table: str) -> list[str]:
        """Which source tables have at least one row routed to
        target_table, based on the per-row `<field>_target_table`
        columns already attached by the domain-driven mapping loop
        above. Used to resolve structural fields (dates, etc.)
        separately for EACH contributing table, rather than assuming
        only one table ever feeds a given OMOP event table."""
        contributing = []
        for table_name, df in tables.items():
            target_cols = [c for c in df.columns if c.endswith("_target_table")]
            if any((df[c] == target_table).any() for c in target_cols):
                contributing.append(table_name)
        return contributing

    def _resolve_plain_fields(
        self, target_table: str, plain_fields: list[str], tables_summary: dict, data_types: dict[str, str],
        scope_source: str | None = None,
    ) -> tuple[list[StructuralTargetMapping], dict]:
        """Plain fields come from the replayed snapshot when there is one,
        and from the model for whatever the snapshot does not cover (or for
        everything, in a normal run). `scope_source` is the single source
        table of an event table's resolution, None for the other tables."""
        if self._replay is None or not plain_fields:
            return self._resolve_plain_fields_via_llm(target_table, plain_fields, tables_summary, data_types)

        entries, uncovered = self._replay.plain_resolutions(target_table, plain_fields, scope_source)
        records = [
            StructuralTargetMapping(
                target_table=e["target_table"], target_field=e["target_field"],
                source_table=e["source_table"], source_field=e["source_field"],
                data_type=data_types.get(e["target_field"]),
                confidence=e.get("confidence"), reason=e.get("reason") or "",
            )
            for e in entries
        ]
        retry_log: dict = {}
        if uncovered:
            more, retry_log = self._resolve_plain_fields_via_llm(target_table, uncovered, tables_summary, data_types)
            records.extend(more)
        return records, retry_log

    def _resolve_plain_fields_via_llm(
        self, target_table: str, plain_fields: list[str], tables_summary: dict, data_types: dict[str, str]
    ) -> tuple[list[StructuralTargetMapping], dict]:
        if not plain_fields:
            return [], {}
        prompt = STRUCTURAL_TARGET_MAPPING_PROMPT.format(
            target_table=target_table,
            target_fields=json.dumps(plain_fields, indent=2),
            tables_summary=json.dumps(tables_summary, indent=2, default=str),
        )
        response = self.llm.invoke(prompt)
        try:
            parsed = parse_json_response(response.content)
        except ValueError:
            parsed = {"mappings": []}

        records = []
        resolved_fields = set()
        for m in parsed.get("mappings", []):
            if not m.get("source_table") or not m.get("source_field"):
                continue  # LLM explicitly found no match - don't record a guess
            resolved_fields.add(m.get("target_field", ""))
            records.append(StructuralTargetMapping(
                target_table=target_table,
                target_field=m.get("target_field", ""),
                source_table=m["source_table"],
                source_field=m["source_field"],
                data_type=data_types.get(m.get("target_field", "")),
                confidence=m.get("confidence"),
                reason=m.get("reason", ""),
            ))

        # Generic retry - applies to ANY plain field that found no
        # source at all on the first attempt, not a hardcoded list.
        # person_source_value gets exactly the same second look as
        # every other field: no "wrong column" to exclude here (unlike
        # the vocab-field retry), just an honest absence of an answer
        # that deserves one more careful look before being accepted.
        unresolved = [f for f in plain_fields if f not in resolved_fields]
        retry_log: dict = {}
        if unresolved:
            retry_prompt = STRUCTURAL_PLAIN_FIELD_RETRY_PROMPT.format(
                target_table=target_table,
                unresolved_fields=json.dumps(unresolved, indent=2),
                tables_summary=json.dumps(tables_summary, indent=2, default=str),
            )
            retry_response = self.llm.invoke(retry_prompt)
            try:
                retry_parsed = parse_json_response(retry_response.content)
            except ValueError:
                retry_parsed = {"mappings": []}

            retry_log[target_table] = {"unresolved_before_retry": unresolved, "resolved_by_retry": []}
            for m in retry_parsed.get("mappings", []):
                if not m.get("source_table") or not m.get("source_field"):
                    continue  # still no match after the second look - an honest, accepted outcome
                target_field = m.get("target_field", "")
                if target_field not in unresolved:
                    continue  # ignore anything outside what was actually asked for
                records.append(StructuralTargetMapping(
                    target_table=target_table,
                    target_field=target_field,
                    source_table=m["source_table"],
                    source_field=m["source_field"],
                    data_type=data_types.get(target_field),
                    confidence=m.get("confidence"),
                    reason=f"[Reprise] {m.get('reason', '')}",
                ))
                retry_log[target_table]["resolved_by_retry"].append(target_field)

        return records, retry_log

    @staticmethod
    def _build_tables_summary(tables: dict[str, Any], profiling_per_table: dict[str, Any]) -> dict:
        summary = {}
        for table_name, df in tables.items():
            table_profiling = profiling_per_table.get(table_name, {})
            profile = table_profiling.get("profile", {})

            # Profiling's OWN semantic reasoning about what each column
            # represents (e.g. "row_id: an internal sequential row
            # counter, not a meaningful clinical identifier") - without
            # this, Mapping only ever sees raw sample values and must
            # rediscover from scratch a meaning Profiling may have
            # already correctly worked out, on the exact same data.
            # Key names confirmed directly against
            # profiling_prompt.py's own requested JSON schema: "field"
            # and "likely_meaning" (NOT "name"/"interpretation" as an
            # earlier version of this code incorrectly guessed, which
            # silently transmitted nothing at all).
            interpretation_by_field: dict[str, str] = {}
            for field_info in table_profiling.get("llm_interpretation", {}).get("fields", []):
                field_name = field_info.get("field")
                interpretation = field_info.get("likely_meaning")
                discrepancy = field_info.get("standard_discrepancy")
                if field_name and interpretation:
                    text = interpretation
                    if discrepancy:
                        text += f" (Écart détecté par le Profiling : {discrepancy})"
                    interpretation_by_field[field_name] = text

            columns = {}
            for col in df.columns:
                if col.startswith("_"):
                    continue
                sample_values = profile.get(col, {}).get("sample_values")
                if sample_values is None:
                    sample_values = df[col].dropna().unique()[:3].tolist()
                entry: dict[str, Any] = {"sample_values": sample_values}
                if col in interpretation_by_field:
                    entry["profiling_interpretation"] = interpretation_by_field[col]
                columns[col] = entry
            summary[table_name] = columns
        return summary
