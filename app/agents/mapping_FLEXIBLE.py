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
from typing import Any

from app.agents.base import BaseAgent
from app.prompts.structural_target_mapping_prompt import (
    STRUCTURAL_TARGET_MAPPING_PROMPT,
    STRUCTURAL_TARGET_MAPPING_RETRY_PROMPT,
)
from app.schemas.agent_result import AgentResult, AgentStatus
from app.schemas.mapping_record import MappingRecord
from app.schemas.structural_target_mapping import StructuralTargetMapping
from app.tools.common.io_utils import run_dir
from app.tools.common.llm_utils import parse_json_response
from app.tools.data.metadata_loader import get_declared_fields_for_table
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
from app.tools.mapping.semantic.semantic_mapper import map_concept, resolve_concept_pair, resolve_ethnicity_rigid
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


class MappingAgent(BaseAgent):
    name = "mapping_agent"
    stage = "mapping"

    def run(self, state: dict[str, Any]) -> AgentResult:
        source_name = state["source_name"]
        batch_cfg = state["batch_metadata"]
        tables = state["_raw_tables"]
        execution_id = state["execution_id"]
        profiling_per_table = state.get("profiling_output", {}).get("per_table", {})
        tables_summary = self._build_tables_summary(tables, profiling_per_table)

        # --- Mechanism 1: row-level domain routing + staging (every table) --
        per_table_output: dict[str, Any] = {}
        all_mapping_records: list[MappingRecord] = []
        local_joins_used: dict[str, dict] = {}
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
                    join_spec = resolve_local_vocab_join(
                        self.llm, table_name, field_name, sample_values, tables_summary
                    )
                    if join_spec is None:
                        continue  # couldn't resolve this reference at all - skip, never guess
                    dictionary_df = tables.get(join_spec["join_table"])
                    if dictionary_df is None:
                        continue
                    joined_values = apply_local_vocab_join(df, dictionary_df, join_spec)
                    if joined_values is None:
                        continue  # join proposal failed real-overlap validation - rejected
                    search_source = joined_values
                    local_joins_used[f"{table_name}.{field_name}"] = join_spec
                    if join_spec["resolved_kind"] == "code" and join_spec.get("resolved_standard"):
                        effective_standard = join_spec["resolved_standard"]
                    elif join_spec.get("resolved_standard"):
                        # Free text (e.g. D_ITEMS.LABEL, "Heart Rate") -
                        # only an EXACT match is ever accepted, never
                        # substring or fuzzy. A full clinical phrase is
                        # far more likely to coincidentally resemble an
                        # unrelated concept via approximate matching
                        # than a short categorical value is - producing
                        # no match at all is better than a silently
                        # wrong one here.
                        effective_standard = join_spec["resolved_standard"]
                        use_exact_only = True
                    else:
                        continue  # text with no plausible target vocabulary at all - nothing to search

                distinct_values = search_source.dropna().unique()
                value_to_concept_id: dict[str, int | None] = {}
                value_to_source_concept_id: dict[str, int | None] = {}
                value_to_target_table: dict[str, str | None] = {}
                for value in distinct_values:
                    if use_exact_only:
                        # Free-text resolution (e.g. a local dictionary's
                        # LABEL column) - no source/standard distinction
                        # applies here (there is no separate "source
                        # vocabulary" for a plain description), and only
                        # an EXACT match is ever accepted.
                        exact_match = search_concept_exact_only(str(value), effective_standard)
                        resolved = {"source_concept": exact_match, "standard_concept": exact_match}
                    else:
                        resolved = resolve_concept_pair(str(value), effective_standard)
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

                    value_to_concept_id[str(value)] = standard_concept["concept_id"] if standard_concept else None
                    value_to_source_concept_id[str(value)] = source_concept["concept_id"] if source_concept else None
                    value_to_target_table[str(value)] = target["table"] if target else None

                    if use_exact_only:
                        reason = (
                            f"Exact text match found in '{effective_standard}'" if source_concept
                            else f"No EXACT match in '{effective_standard}' - approximate matching is "
                                 f"deliberately disabled for free-text local vocabulary values."
                        )
                    elif source_concept is None:
                        reason = f"No candidate found in vocabulary '{effective_standard}'"
                    elif standard_concept is None:
                        reason = (
                            f"Found source concept {source_concept['concept_id']} "
                            f"('{source_concept['concept_name']}') in '{effective_standard}', but it has no "
                            f"'Maps to' Standard equivalent."
                        )
                    elif standard_concept is source_concept:
                        reason = f"'{effective_standard}' is itself a Standard vocabulary - source and standard concept are the same."
                    else:
                        reason = (
                            f"Source concept {source_concept['concept_id']} in '{effective_standard}' maps to "
                            f"Standard concept {standard_concept['concept_id']} via 'Maps to'."
                        )

                    table_mapping_records.append(MappingRecord(
                        source=source_name,
                        field=f"{table_name}.{field_name}",
                        standard=effective_standard,
                        source_value=str(value),
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
        structural_targets, vocab_field_retry_log = self._resolve_all_target_fields(tables, enriched_tables, profiling_per_table)

        result = AgentResult(
            execution_id=execution_id,
            agent_name=self.name,
            status=AgentStatus.SUCCESS,
            output={
                "per_table": per_table_output,
                "structural_target_mappings": [m.model_dump(mode="json") for m in structural_targets],
                "local_vocab_joins": local_joins_used,
                "vocab_field_retry_log": vocab_field_retry_log,
            },
            tools_used=[
                "build_structural_mapping", "write_initial_staging", "map_concept",
                "resolve_target", "get_table_columns", "find_paired_source_value_field",
            ],
            reasoning_summary=(
                f"Mapped {len(tables)} table(s) via domain routing; "
                f"{len(all_mapping_records)} semantic mappings attempted; "
                f"{len(structural_targets)} target field(s) resolved across "
                f"{len(IN_SCOPE_TABLES)} OMOP table(s)."
            ),
        )
        report = self._build_report(structural_targets, per_table_output)
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
        self, tables: dict[str, Any], enriched_tables: dict[str, Any], profiling_per_table: dict[str, Any]
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
                    plain_resolutions.extend(
                        self._resolve_plain_fields(target_table, plain_fields, single_source_summary, data_types)
                    )
            else:
                plain_resolutions = self._resolve_plain_fields(target_table, plain_fields, tables_summary, data_types)
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
                if paired_resolution is None or not paired_resolution.source_table:
                    records.append(StructuralTargetMapping(
                        target_table=target_table, target_field=concept_field,
                        data_type=data_types.get(concept_field),
                        reason=f"Paired field '{paired_field}' was not resolved in this batch.",
                    ))
                    continue

                df = tables.get(paired_resolution.source_table)
                if df is None or paired_resolution.source_field not in df.columns:
                    continue
                distinct_values = df[paired_resolution.source_field].dropna().unique()

                def _resolve_all(values):
                    resolved = []
                    for v in values:
                        c = (
                            resolve_ethnicity_rigid(str(v)) if vocabulary_domain == "Ethnicity" else None
                        ) or map_concept(str(v), vocabulary_domain)
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
                while match_rate == 0.0 and len(resolved_values) > 0 and retries_used < MAX_VOCAB_FIELD_RESOLUTION_ATTEMPTS - 1:
                    retries_used += 1
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
                            f"Resolved against fixed OMOP vocabulary '{vocabulary_domain}' "
                            f"(paired with {paired_field})"
                            if candidate else f"No candidate found in vocabulary '{vocabulary_domain}'"
                        ),
                    ))
        return records, vocab_field_retry_log

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
        self, target_table: str, plain_fields: list[str], tables_summary: dict, data_types: dict[str, str]
    ) -> list[StructuralTargetMapping]:
        if not plain_fields:
            return []
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
        for m in parsed.get("mappings", []):
            if not m.get("source_table") or not m.get("source_field"):
                continue  # LLM explicitly found no match - don't record a guess
            records.append(StructuralTargetMapping(
                target_table=target_table,
                target_field=m.get("target_field", ""),
                source_table=m["source_table"],
                source_field=m["source_field"],
                data_type=data_types.get(m.get("target_field", "")),
                confidence=m.get("confidence"),
                reason=m.get("reason", ""),
            ))
        return records

    @staticmethod
    def _build_tables_summary(tables: dict[str, Any], profiling_per_table: dict[str, Any]) -> dict:
        summary = {}
        for table_name, df in tables.items():
            profile = profiling_per_table.get(table_name, {}).get("profile", {})
            columns = {}
            for col in df.columns:
                if col.startswith("_"):
                    continue
                sample_values = profile.get(col, {}).get("sample_values")
                if sample_values is None:
                    sample_values = df[col].dropna().unique()[:3].tolist()
                columns[col] = sample_values
            summary[table_name] = columns
        return summary