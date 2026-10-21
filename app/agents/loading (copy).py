"""
Loading Agent.

Combines what Mapping and Transformation already resolved into complete
OMOP rows and loads them into OMOP_TEMP, following a FIXED load order
(app/tools/mapping/omop_load_order.py, derived from OMOP's official FK
constraints - never guessed at runtime).

Two kinds of source data to assemble, per target table:
  1. Domain-driven event rows (condition_occurrence, drug_exposure,
     measurement, procedure_occurrence, observation): rows are filtered
     from their source table using the per-row `<field>_target_table`
     column Mapping now attaches, then combined with the resolved
     `<field>_concept_id`.
  2. Structural fields (person, visit_occurrence, death - and
     observation_period, deferred, see below): assembled from the
     `__omop_<table>__<field>` columns Transformation produced, which
     may live on DIFFERENT source tables. When more than one source
     table contributes fields for the same target table, the Loading
     Agent asks the LLM ONCE which columns join the two tables
     (app/tools/mapping/join_key_resolver.py) - the actual join is then
     executed deterministically with pandas.merge(), and the answer is
     cached for the rest of the run so the same pair is never asked twice.

PERSON is always resolved first: a sequential person_id is generated
from its primary source column, and kept in memory for this run only -
this is NOT the cross-batch crosswalk that was deliberately removed
earlier (that one served cross-run deduplication/upsert); this is the
minimum structural bookkeeping needed to wire foreign keys within a
single run, unavoidable in any relational load.

OBSERVATION_PERIOD is explicitly NOT computed here - its start/end dates
are DERIVED (min/max of a person's clinical event dates), not mapped
from a single source field. Flagged as a known, separately-tracked gap
rather than silently skipped.
"""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from app.agents.base import BaseAgent
from app.schemas.agent_result import AgentResult, AgentStatus
from app.tools.data.folder_watcher import mark_status
from app.tools.mapping.join_key_resolver import resolve_join_key
from app.tools.mapping.omop_load_order import LOAD_ORDER
from app.tools.mapping.omop_schema_introspection import get_table_columns
from app.tools.mapping.omop_target_schema import TABLE_FIELD_TEMPLATES
from app.tools.omop.omop_loader import load_to_omop, promote_to_final, reset_temp_for_new_run, verify_load

# Every OMOP table (except PERSON, already handled via person_id, and
# DEATH, whose primary key IS person_id per the CDM spec) has its OWN
# surrogate primary key, distinct from person_id - a patient can have
# many visits/conditions/etc. This must be generated here, same as
# person_id: sequential, in-memory, valid for this run only.
PRIMARY_KEY_FIELD = {
    "visit_occurrence": "visit_occurrence_id",
    "condition_occurrence": "condition_occurrence_id",
    "drug_exposure": "drug_exposure_id",
    "measurement": "measurement_id",
    "procedure_occurrence": "procedure_occurrence_id",
    "observation": "observation_id",
    "observation_period": "observation_period_id",
}

# Below this, a plain-field structural resolution (the LLM's own
# field-matching guess, e.g. "condition_start_date <- conditions.START")
# is excluded from row assembly entirely - a low-confidence guess is
# worse than no mapping at all, since it can silently populate a column
# with data that doesn't actually belong there.
MIN_STRUCTURAL_CONFIDENCE = 0.3

# Vocabulary-field records (source_value set, resolved deterministically
# via search_concept()) use a DIFFERENT, well-defined confidence scale
# (see semantic_mapper.py: 1.0 exact code, 0.95 exact name, 0.7
# substring, and for fuzzy trigram matches, the ACTUAL similarity score
# itself - continuously ranging from FUZZY_SIMILARITY_THRESHOLD, 0.3, up
# to just under 1.0). This threshold distinguishes a WEAK, likely
# coincidental fuzzy match (e.g. a Race value like "ASIAN" accidentally
# resembling some unrelated concept in the much narrower "Ethnicity"
# vocabulary) from a STRONG one that's almost certainly correct (e.g.
# "BLACK/AFRICAN AMERICAN" matching "Black or African American" - only
# fuzzy because of the "/" punctuation, not because it's actually
# uncertain). An earlier version of this fix used a flat 0.5 for every
# fuzzy match regardless of strength, which wrongly excluded genuinely
# correct matches like that one - see
# _filter_low_confidence_plain_fields's docstring for the full story.
MIN_VOCAB_FIELD_CONFIDENCE = 0.55

# Each domain-driven event table's ONE primary required (NOT NULL) date
# field, paired with its corresponding datetime column - used to
# reconcile the two when only one was resolved (see
# _apply_omop_date_conventions).
PRIMARY_REQUIRED_DATE_FIELD = {
    "condition_occurrence": ("condition_start_date", "condition_start_datetime"),
    "drug_exposure": ("drug_exposure_start_date", "drug_exposure_start_datetime"),
    "measurement": ("measurement_date", "measurement_datetime"),
    "procedure_occurrence": ("procedure_date", "procedure_datetime"),
    "observation": ("observation_date", "observation_datetime"),
    "observation_period": ("observation_period_start_date", None),  # no datetime sibling in the OMOP spec
    "visit_occurrence": ("visit_start_date", "visit_start_datetime"),
    "death": ("death_date", "death_datetime"),
}

# Some structural tables have a PRIMORDIAL concept field - one that
# defines the very meaning of the row (e.g. visit_concept_id for
# VISIT_OCCURRENCE: a "visit" with no visit type at all isn't a
# meaningful clinical record). Deliberately NOT applied to the 5
# domain-driven event tables (condition_occurrence, drug_exposure,
# measurement, procedure_occurrence, observation): a row can only ever
# reach insertion there in the first place if a concept was already
# found during Mapping's own routing (see resolve_concept_pair /
# DOMAIN_TO_TABLE) - this same class of check would be redundant there.
# VISIT_OCCURRENCE's visit_concept_id, by contrast, comes from a
# SEPARATE mechanism (paired vocab-field resolution) that can fail to
# find any plausible source at all without affecting whether the row
# was assembled in the first place.
PRIMARY_REQUIRED_CONCEPT_FIELD = {
    "visit_occurrence": "visit_concept_id",
}


class LoadingAgent(BaseAgent):
    name = "loading_agent"
    stage = "loading"

    def run(self, state: dict[str, Any]) -> AgentResult:
        mode = state.get("loading_mode", "load_temp")
        if mode == "load_temp":
            return self._load_temp(state)
        return self._promote_final(state)

    # ------------------------------------------------------------------
    # load_temp
    # ------------------------------------------------------------------
    def _load_temp(self, state: dict[str, Any]) -> AgentResult:
        reset_temp_for_new_run()
        tables: dict[str, pd.DataFrame] = dict(state.get("_transformed_tables") or {})
        structural_targets = state.get("mapping_output", {}).get("structural_target_mappings", [])
        structural_targets = self._filter_low_confidence_plain_fields(structural_targets)
        batch_type_concepts = state.get("batch_metadata", {}).get("type_concepts", {})
        join_key_cache: dict[tuple, tuple[str, str] | None] = {}
        self._join_key_log: dict[tuple, tuple[str, str] | None] = {}
        self._person_id_resolution_log: dict[tuple, dict] = {}
        # Dates filled from the visit (imputations, not observations):
        # {"<table><-<source>": {rows_imputed, rows_in_source, ...}}
        self._date_imputation_log: dict[str, dict] = {}
        per_table_result: dict[str, Any] = {}
        finalized_rows: dict[str, pd.DataFrame] = {}

        # --- Step 1: resolve PERSON first, everything else needs it ----
        person_source_table, person_source_field = self._find_field_source(
            structural_targets, "person", "person_source_value"
        )
        if person_source_table is None or person_source_table not in tables:
            result = AgentResult(
                execution_id=state["execution_id"], agent_name=self.name, status=AgentStatus.FAIL,
                output={"error": "Could not resolve person_source_value - cannot assign person_id for this batch."},
                reasoning_summary="Loading aborted: no person_source_value resolution found for this batch.",
            )
            return self.persist(result, stage_override="loading_load_temp")

        person_df = tables[person_source_table].copy()
        codes, uniques = pd.factorize(person_df[person_source_field])
        person_df["_person_id"] = codes + 1  # sequential, this-run-only surrogate key
        tables[person_source_table] = person_df

        try:
            # --- Pass 1: assemble + finalize every table EXCEPT
            # observation_period, WITHOUT inserting yet - its computation
            # (Step 2 below) needs to scan every other table's already-
            # finalized dates, most of which come AFTER it in LOAD_ORDER.
            for target_table in LOAD_ORDER:
                if target_table == "observation_period":
                    continue

                if target_table in ("person", "visit_occurrence", "death"):
                    rows = self._assemble_structural_table(
                        target_table, person_source_table, person_df, tables,
                        structural_targets, join_key_cache, is_person_table=(target_table == "person"),
                    )
                else:
                    rows = self._assemble_domain_table(
                        target_table, person_source_table, person_df, tables, structural_targets, join_key_cache,
                        visit_occurrence_df=finalized_rows.get("visit_occurrence"),
                    )

                if rows is None or rows.empty:
                    per_table_result[target_table] = {"rows_loaded": 0, "reason": "no rows resolved for this batch"}
                    continue

                rows, truncated, date_drop_diagnostic, concept_drop_diagnostic = self._finalize_rows(
                    target_table, rows, batch_type_concepts
                )
                if "person_id" in rows.columns:
                    self._person_id_resolution_log[f"{target_table}<-BEFORE_INSERT"] = {
                        "total_rows": len(rows), "null_person_id": int(rows["person_id"].isna().sum()),
                    }
                if rows.empty:
                    reason = "all rows dropped (missing required concept)" if concept_drop_diagnostic \
                        else "all rows dropped (missing required date)"
                    per_table_result[target_table] = {"rows_loaded": 0, "reason": reason}
                    if date_drop_diagnostic:
                        per_table_result[target_table]["dropped_missing_date"] = date_drop_diagnostic
                    if concept_drop_diagnostic:
                        per_table_result[target_table]["dropped_missing_concept"] = concept_drop_diagnostic
                    continue

                finalized_rows[target_table] = rows
                if "_debug_source_table" in rows.columns:
                    # The REAL, post-drop breakdown - what actually
                    # survives to be inserted, not the earlier
                    # pre-drop count from _assemble_domain_table.
                    real_breakdown = {}
                    for source, group in rows.groupby("_debug_source_table"):
                        real_breakdown[source] = {
                            "total": len(group),
                            "null": int(group["person_id"].isna().sum()) if "person_id" in group.columns else 0,
                        }
                    self._person_id_resolution_log[f"{target_table}<-FINAL_BY_SOURCE"] = real_breakdown
                    rows = rows.drop(columns=["_debug_source_table"])
                    finalized_rows[target_table] = rows
                if truncated:
                    per_table_result.setdefault(target_table, {})["truncated_fields"] = truncated
                imputed_here = {
                    key.split("<-", 1)[1]: info for key, info in self._date_imputation_log.items()
                    if key.startswith(f"{target_table}<-")
                }
                if imputed_here:
                    per_table_result.setdefault(target_table, {})["dates_imputed_from_visit"] = imputed_here
                if date_drop_diagnostic:
                    per_table_result.setdefault(target_table, {})["dropped_missing_date"] = date_drop_diagnostic
                if concept_drop_diagnostic:
                    per_table_result.setdefault(target_table, {})["dropped_missing_concept"] = concept_drop_diagnostic

            # --- Step 2: compute OBSERVATION_PERIOD from every OTHER
            # finalized table's dates - generic (scans any column ending
            # in "_date", no per-table field list to hand-maintain).
            op_rows = self._compute_observation_period(finalized_rows)
            if op_rows is not None and not op_rows.empty:
                op_rows, op_truncated, op_date_drop, op_concept_drop = self._finalize_rows(
                    "observation_period", op_rows, batch_type_concepts
                )
                if not op_rows.empty:
                    finalized_rows["observation_period"] = op_rows

            # --- Cleanup: strip the NATURALKEY_* preservation columns
            # before insertion - they existed only to let the date
            # fallback above find a real join key dynamically; they are
            # not real OMOP fields and must never reach the database.
            for table_name, rows in finalized_rows.items():
                natural_cols = [c for c in rows.columns if c.startswith("NATURALKEY_")]
                if natural_cols:
                    finalized_rows[table_name] = rows.drop(columns=natural_cols)

            # --- Pass 2: insert everything, in the fixed FK-safe order --
            for target_table in LOAD_ORDER:
                rows = finalized_rows.get(target_table)
                if rows is None:
                    per_table_result.setdefault(target_table, {
                        "rows_loaded": 0, "reason": "no rows resolved for this batch",
                    })
                    continue
                n = load_to_omop(target_table, rows)
                ok = verify_load(target_table, n)
                per_table_result.setdefault(target_table, {})
                per_table_result[target_table]["rows_loaded"] = n
                per_table_result[target_table]["verified"] = ok
        except Exception:
            # A mid-loop crash (e.g. a DB insert failure on one table)
            # must not erase the diagnostic value of everything learned
            # up to that point - persist it BEFORE re-raising, so the
            # Root Cause Analyzer's failure routing still works exactly
            # as before, but this run's join_keys_resolved and
            # per_table_result (which tables succeeded, with what) are
            # no longer silently lost.
            partial = AgentResult(
                execution_id=state["execution_id"], agent_name=self.name, status=AgentStatus.FAIL,
                output={
                    "per_table": per_table_result,
                    "join_keys_resolved": {f"{a}<->{b}": key for (a, b), key in self._join_key_log.items()},
                    "person_id_resolution": self._person_id_resolution_log,
                    "dates_imputed_from_visit": self._date_imputation_log,
                },
                reasoning_summary=(
                    f"Loading crashed after successfully loading {len(per_table_result)} table(s) - "
                    f"see per_table for what succeeded, join_keys_resolved for join diagnostics, and "
                    f"person_id_resolution for exactly which source table(s) produced unresolved person_id."
                ),
            )
            self.persist(partial, stage_override="loading_load_temp")
            raise

        result = AgentResult(
            execution_id=state["execution_id"], agent_name=self.name, status=AgentStatus.SUCCESS,
            output={
                "per_table": per_table_result,
                "join_keys_resolved": {f"{a}<->{b}": key for (a, b), key in self._join_key_log.items()},
                "person_id_resolution": self._person_id_resolution_log,
                "dates_imputed_from_visit": self._date_imputation_log,
            },
            tools_used=["load_to_omop", "verify_load", "resolve_join_key"],
            reasoning_summary=f"Loaded {len(per_table_result)} table(s) into OMOP_TEMP, following the fixed OMOP load order.",
        )
        return self.persist(result, stage_override="loading_load_temp")

    # ------------------------------------------------------------------
    # Structural tables (person, visit_occurrence, death)
    # ------------------------------------------------------------------
    def _assemble_structural_table(
        self, target_table, person_source_table, person_df, tables,
        structural_targets, join_key_cache, is_person_table: bool,
    ) -> pd.DataFrame | None:
        fields = [
            m for m in structural_targets
            if m.get("target_table") == target_table and m.get("source_table") and m.get("source_field")
        ]
        if not fields:
            return None

        by_source_table: dict[str, list[dict]] = {}
        for f in fields:
            by_source_table.setdefault(f["source_table"], []).append(f)

        # Counts DISTINCT target fields, never raw record count - a
        # mechanism that produces multiple records per field (e.g. the
        # fixed-value-mapping resolver, one record per distinct RAW
        # VALUE rather than one per field) must never inflate a source
        # table's apparent field count and wrongly win primary_table
        # selection over a table with genuinely more distinct fields.
        # Confirmed in production: ADMISSIONS' 5 real fields (race/
        # ethnicity) produced 37 raw records (9 values x race_concept_id
        # alone), outweighing PATIENTS' 9 real fields under the old
        # raw-count logic and silently dropping every PATIENTS-derived
        # column (year_of_birth, person_source_value, ...) from PERSON.
        primary_table = max(
            by_source_table, key=lambda t: len({f["target_field"] for f in by_source_table[t]})
        )
        base_df = tables[primary_table].copy()

        for other_table, other_fields in by_source_table.items():
            if other_table == primary_table:
                continue
            key = self._get_join_key(primary_table, base_df, other_table, tables[other_table], join_key_cache)
            if key is None:
                continue  # this table's fields can't be joined in for this batch - skipped, not guessed
            key_a, key_b = key
            other_cols_needed = set()
            for f in other_fields:
                # Vocabulary fields (source_value set) were already
                # transformed into __omop_{target_table}__{target_field}
                # by the Transformation Agent - THAT column must be
                # brought in, not the raw source_field, which never
                # carries the resolved concept_id at all. Confirmed in
                # production: race_concept_id/ethnicity_concept_id came
                # from ADMISSIONS while PATIENTS was primary - the raw
                # "ethnicity" column was merged in instead of
                # "__omop_person__race_concept_id", silently defaulting
                # every row to 0 (this had never been triggered before,
                # since every vocab field previously happened to share
                # its source table with person_source_value itself).
                other_cols_needed.add(f"__omop_{target_table}__{f['target_field']}")
                other_cols_needed.add(f["source_field"])
            other_cols = [c for c in other_cols_needed if c in tables[other_table].columns] + [key_b]
            other_cols = list(dict.fromkeys(other_cols))  # de-dup while preserving order
            # Deduplicated on the join key BEFORE merging - without this,
            # a secondary table with multiple rows per key (e.g.
            # ADMISSIONS, several rows per patient) silently MULTIPLIES
            # base_df's rows, one per matching row on the right side,
            # instead of enriching each existing row with one extra
            # value - confirmed in production: a 100-patient PERSON
            # table became ~129 rows once ethnicity was resolved from
            # ADMISSIONS, causing a person_id primary key collision at
            # insert time. Keeps the first occurrence, consistent with
            # the same protection already used in apply_local_vocab_join().
            other_df_deduped = tables[other_table][other_cols].drop_duplicates(subset=[key_b], keep="first")
            base_df = base_df.merge(
                other_df_deduped, left_on=key_a, right_on=key_b, how="left", suffixes=("", "_joined")
            )

        row = pd.DataFrame(index=base_df.index)
        for f in fields:
            output_col = f"__omop_{target_table}__{f['target_field']}"
            if output_col in base_df.columns:
                row[f["target_field"]] = base_df[output_col]

        # Preserve the primary table's own RAW columns too (prefixed,
        # never colliding with real OMOP field names) - this table's own
        # assigned primary key (e.g. visit_occurrence_id) is a
        # sequentially generated surrogate, NOT directly comparable to
        # any other table's raw foreign key value (e.g. a domain table's
        # own "visit_occurrence_id" structural resolution, which is
        # really just its raw source column, like hadm_id, never
        # translated). Keeping the raw columns here lets a later
        # fallback (see _assemble_domain_table's date fallback) find a
        # REAL join key dynamically via the same deterministic overlap
        # check used everywhere else in this project - never a
        # hardcoded column name assumption.
        for col in base_df.columns:
            if not col.startswith("_") and not col.startswith("__omop_"):
                row[f"NATURALKEY_{col}"] = base_df[col].to_numpy()

        if is_person_table:
            row["person_id"] = base_df["_person_id"] if primary_table == person_source_table else \
                self._resolve_person_id_for(target_table, primary_table, base_df, person_source_table, person_df, join_key_cache)
            row = self._derive_birth_components(row)
        else:
            row["person_id"] = self._resolve_person_id_for(
                target_table, primary_table, base_df, person_source_table, person_df, join_key_cache
            )
            if target_table == "death":
                row = self._drop_non_death_rows(row)
        return row

    @staticmethod
    def _drop_non_death_rows(row: pd.DataFrame) -> pd.DataFrame:
        """DEATH is optional per person (0 or 1 row) - unlike PERSON or
        VISIT_OCCURRENCE, which always get a row for every source
        entity. The structural assembly above builds one candidate DEATH
        row per row of the primary source table (e.g. every patient),
        regardless of whether they actually died - a living patient's
        death_date is genuinely absent, not unresolved. Those rows must
        be dropped entirely rather than inserted with a NULL death_date,
        which both violates the NOT NULL constraint and is semantically
        wrong (there is no 'living patient with no death date' record in
        DEATH - there is simply no record at all)."""
        if "death_date" not in row.columns:
            return row
        return row[row["death_date"].notna()]

    @staticmethod
    def _derive_birth_components(row: pd.DataFrame) -> pd.DataFrame:
        """OMOP CDM requires PERSON.year_of_birth (NOT NULL) and also
        defines month_of_birth/day_of_birth, even when the source only
        provides a single birth_datetime (as Synthea and many real
        exports do). This is a FIXED decomposition rule of the CDM
        specification itself - birth_datetime always implies its own
        year/month/day - so it's derived deterministically here rather
        than asked of the LLM (there is no source column to find; it's
        arithmetic on a field already resolved)."""
        if "birth_datetime" not in row.columns:
            return row
        parsed = pd.to_datetime(row["birth_datetime"], errors="coerce")
        if "year_of_birth" not in row.columns or row["year_of_birth"].isna().all():
            row["year_of_birth"] = parsed.dt.year
        if "month_of_birth" not in row.columns or row["month_of_birth"].isna().all():
            row["month_of_birth"] = parsed.dt.month
        if "day_of_birth" not in row.columns or row["day_of_birth"].isna().all():
            row["day_of_birth"] = parsed.dt.day
        return row

    @staticmethod
    def _fill_missing_dates_from_visit(frame: pd.DataFrame, date_col: str, visit_dates: Any) -> int:
        """Fills `date_col` of `frame` (in place) from `visit_dates`, a
        positional array aligned with the frame's rows, ONLY where the
        current value is missing and a visit date is available. A value
        the source really provides is never overwritten. If the column
        does not exist yet it is created from `visit_dates`. Returns how
        many rows received a date (0 when nothing was missing or no
        visit date could be found)."""
        visit_dates = np.asarray(visit_dates, dtype=object)
        if date_col not in frame.columns:
            frame[date_col] = visit_dates
            return int(pd.notna(visit_dates).sum())

        current = frame[date_col]
        fillable = current.isna().to_numpy() & pd.notna(visit_dates)
        if not fillable.any():
            return 0
        values = current.to_numpy(dtype=object, copy=True)
        values[fillable] = visit_dates[fillable]
        frame[date_col] = pd.Series(values, index=frame.index).infer_objects()
        return int(fillable.sum())

    # ------------------------------------------------------------------
    # Domain-driven event tables
    # ------------------------------------------------------------------
    def _assemble_domain_table(
        self, target_table, person_source_table, person_df, tables, structural_targets, join_key_cache,
        visit_occurrence_df: pd.DataFrame | None = None,
    ) -> pd.DataFrame | None:
        """Rewritten for simplicity and robustness: each contributing
        source table is processed in ONE self-contained block - no
        pre-grouped dict shared across iterations, no index-based
        assignment anywhere. Every array is attached by raw numpy
        position (`.to_numpy()`), and a hard `assert` immediately after
        resolving person_id makes any length mismatch impossible to
        miss (it crashes right here, with full context, rather than
        surfacing three steps later as a cryptic NOT NULL violation)."""
        template = TABLE_FIELD_TEMPLATES.get(target_table)
        if template is None:
            return None
        concept_field, source_value_field = template["concept_field"], template["source_value_field"]
        source_concept_field = template.get("source_concept_field")

        per_source_frames: list[pd.DataFrame] = []

        for source_table_name, df in tables.items():
            target_table_columns = [c for c in df.columns if c.endswith("_target_table")]
            for target_col in target_table_columns:
                field_name = target_col[: -len("_target_table")]
                concept_col = f"{field_name}_concept_id"
                if concept_col not in df.columns:
                    continue

                subset = df.loc[df[target_col] == target_table].reset_index(drop=True)
                if subset.empty:
                    continue

                person_ids = self._resolve_person_id_for(
                    target_table, source_table_name, subset, person_source_table, person_df, join_key_cache
                )
                person_ids_arr = person_ids.to_numpy()
                assert len(person_ids_arr) == len(subset), (
                    f"person_id resolution length mismatch for target_table='{target_table}', "
                    f"source_table='{source_table_name}': got {len(person_ids_arr)} values "
                    f"for {len(subset)} rows - this should be structurally impossible."
                )

                frame = pd.DataFrame({
                    concept_field: subset[concept_col].to_numpy(),
                    source_value_field: subset[field_name].to_numpy(),
                    "person_id": person_ids_arr,
                    "_debug_source_table": source_table_name,
                })

                # The source concept (e.g. condition_source_concept_id) -
                # the code's OWN concept in its declared vocabulary,
                # distinct from concept_field's STANDARD concept (see
                # resolve_concept_pair() in semantic_mapper.py). Only
                # populated if Mapping actually produced this column -
                # older/simpler mechanisms that never computed a source
                # concept leave it absent, and that's fine (falls back
                # to the NOT NULL=0 convention in Loading like any other
                # unresolved concept field).
                source_concept_col = f"{field_name}_source_concept_id"
                if source_concept_field and source_concept_col in subset.columns:
                    frame[source_concept_field] = subset[source_concept_col].to_numpy()

                # Merge structural fields (dates, etc.) for THIS SAME
                # source table - filtered directly here, not via a
                # dict pre-built across the whole function, so there is
                # no shared mutable state that could leak between
                # different source tables' iterations.
                #
                # person_id and the table's own surrogate PK must NEVER
                # be overwritten by structural mappings: Mapping often
                # proposes person_id <- source PATIENT (UUID) + cast_integer,
                # which produces NaN and would wipe the correctly resolved
                # sequential person_id (see RUN-76419fb3 NotNullViolation).
                pk_field = PRIMARY_KEY_FIELD.get(target_table)
                protected = {"person_id"}
                if pk_field:
                    protected.add(pk_field)

                for m in structural_targets:
                    if (m.get("target_table") != target_table
                            or m.get("source_table") != source_table_name
                            or not m.get("source_field")):
                        continue
                    tf = m["target_field"]
                    if tf in protected:
                        continue
                    output_col = f"__omop_{target_table}__{tf}"
                    if output_col in subset.columns:
                        frame[tf] = subset[output_col].to_numpy()

                # Date fallback - ONLY when THIS source table produced
                # no value at all for the primary required date field
                # (e.g. DIAGNOSES_ICD has no date column of its own):
                # find a REAL join key between this source table and
                # visit_occurrence's own preserved raw columns
                # (NATURALKEY_*), via the same deterministic overlap check
                # used everywhere else in this project - NEVER via
                # visit_occurrence_id itself, which is a sequentially
                # assigned surrogate, not directly comparable to a
                # domain table's own raw foreign key value (confirmed in
                # production: DIAGNOSES_ICD.hadm_id values like 165520
                # never matched visit_occurrence_id's 1, 2, 3...,
                # silently finding nothing every time). This is a
                # documented OHDSI ETL convention for sources lacking a
                # genuine event-level date (confirmed via the
                # ETL-LambdaBuilder specification for Premier:
                # "condition start date is determined as the visit
                # start date... the exact day of diagnosis is not
                # recorded"), applied here generically to any domain
                # table, not hardcoded to condition_occurrence. A source
                # that DOES have its own real date (e.g. Synthea's
                # conditions.START) is never touched by this - the
                # fallback fills ONLY the values that are missing,
                # whether the whole column is absent from this source's
                # frame (DIAGNOSES_ICD, PROCEDURES_ICD) or present but
                # empty for some rows (MIMIC CPTEVENTS: CHARTDATE is
                # NULL for every ICU cost-center row, 1288 of 1579 in
                # the audited batch - before this, those rows reached
                # _drop_rows_missing_required_date and were lost). A
                # date that the source really provides is never
                # overwritten. Every date filled this way is an
                # imputation, not an observation, so it is counted in
                # self._date_imputation_log and reported per table.
                primary_date_field = PRIMARY_REQUIRED_DATE_FIELD.get(target_table)
                needs_date_fallback = bool(primary_date_field) and (
                    primary_date_field[0] not in frame.columns or bool(frame[primary_date_field[0]].isna().any())
                )
                if (needs_date_fallback
                        and visit_occurrence_df is not None and "visit_start_date" in visit_occurrence_df.columns):
                    natural_cols = [c for c in visit_occurrence_df.columns if c.startswith("NATURALKEY_")]
                    join_key = self._find_unique_join_key(
                        subset, visit_occurrence_df[natural_cols]
                    ) if natural_cols else None
                    if join_key is not None:
                        key_a, key_b = join_key
                        # Safety net: _find_unique_join_key prefers the
                        # MOST unique candidate, but doesn't guarantee
                        # perfect uniqueness if none exists - this
                        # prevents a crash even then, without it being
                        # the primary correctness mechanism anymore.
                        visit_occurrence_deduped = visit_occurrence_df.drop_duplicates(subset=[key_b], keep="first")
                        visit_dates = visit_occurrence_deduped.set_index(key_b)["visit_start_date"]
                        # Not indexed by subset's own row order (frame
                        # was built from subset already) - realign via
                        # the same source column used for the join.
                        imputed = self._fill_missing_dates_from_visit(
                            frame, primary_date_field[0], subset[key_a].map(visit_dates).to_numpy()
                        )
                        if imputed:
                            # A source table can contribute several
                            # concept columns to the same target table:
                            # accumulate rather than overwrite.
                            entry = self._date_imputation_log.setdefault(
                                f"{target_table}<-{source_table_name}",
                                {"rows_imputed": 0, "rows_in_source": 0,
                                 "date_field": primary_date_field[0],
                                 "filled_from": "visit_occurrence.visit_start_date"},
                            )
                            entry["rows_imputed"] += imputed
                            entry["rows_in_source"] += len(frame)

                per_source_frames.append(frame)

        if not per_source_frames:
            return None

        combined = pd.concat(per_source_frames, ignore_index=True)

        # PRE-drop breakdown only - _finalize_rows (called by the
        # caller, AFTER this returns) can still remove rows missing a
        # required date/concept, so this count does NOT yet reflect
        # what actually gets inserted. The caller recomputes the real,
        # POST-drop breakdown using _debug_source_table (deliberately
        # NOT dropped here anymore) and logs THAT as FINAL_BY_SOURCE -
        # confirmed in production: the provenance report's row counts
        # didn't match the database, because this breakdown was taken
        # before rows could still be dropped.
        breakdown = {}
        for source, group in combined.groupby("_debug_source_table"):
            breakdown[source] = {"total": len(group), "null": int(group["person_id"].isna().sum())}
        self._person_id_resolution_log[f"{target_table}<-BEFORE_DROP_BY_SOURCE"] = breakdown

        return combined

    # ------------------------------------------------------------------
    # Shared helpers
    # ------------------------------------------------------------------
    def _resolve_person_id_for(
        self, target_table: str, source_table_name: str, df: pd.DataFrame, person_source_table: str,
        person_df: pd.DataFrame, join_key_cache: dict,
    ) -> pd.Series:
        """Maps every row of `df` (from source_table_name) to the
        person_id assigned in Step 1, joining through person_df if
        source_table_name isn't the person table itself. Diagnostics are
        keyed by (target_table, source_table_name) - NOT source_table_name
        alone - since the same source table can contribute rows to
        SEVERAL different target tables (e.g. conditions.CODE routing
        some values to condition_occurrence and others to observation);
        keying by source table alone would let a later, successful call
        silently overwrite an earlier, failing one's diagnostic."""
        log_key = f"{target_table}<-{source_table_name}"
        if source_table_name == person_source_table:
            return df["_person_id"] if "_person_id" in df.columns else pd.Series([None] * len(df), index=df.index)

        key = self._get_join_key(source_table_name, df, person_source_table, person_df, join_key_cache)
        if key is None:
            self._person_id_resolution_log[log_key] = {
                "total_rows": len(df), "null_person_id": len(df), "join_key": None,
            }
            return pd.Series([None] * len(df), index=df.index)
        key_a, key_b = key
        key_b_to_person_id = dict(zip(person_df[key_b], person_df["_person_id"]))
        resolved = df[key_a].map(key_b_to_person_id)
        self._person_id_resolution_log[log_key] = {
            "total_rows": len(df), "null_person_id": int(resolved.isna().sum()), "join_key": list(key),
            "sample_unmatched_values": df.loc[resolved.isna(), key_a].dropna().unique()[:5].tolist(),
        }
        return resolved

    # Overlap fraction above which a column pair is trusted without
    # asking the LLM at all - deterministic and reproducible across
    # retries, unlike an LLM call that isn't guaranteed to answer
    # identically twice for the same pair of tables.
    _DETERMINISTIC_OVERLAP_THRESHOLD = 0.8

    def _get_join_key(self, table_a, df_a, table_b, df_b, join_key_cache):
        cache_key = (table_a, table_b)
        if cache_key in join_key_cache:
            return join_key_cache[cache_key]

        # Deterministic pre-check FIRST: many real sources repeat the
        # exact same (foreign_key, primary_key) pattern across every
        # table (e.g. Synthea's "PATIENT" column always references
        # "patients.Id") - if any column pair already shows strong real
        # overlap, use it directly without ever asking the LLM, so the
        # SAME correct answer is found every time, including on a
        # retry after a failure, rather than depending on the LLM
        # reasoning identically twice.
        deterministic = self._find_deterministic_join_key(df_a, df_b)
        if deterministic is not None:
            join_key_cache[cache_key] = deterministic
            self._join_key_log[cache_key] = deterministic
            return deterministic

        sample_a = {c: df_a[c].dropna().unique()[:3].tolist() for c in df_a.columns if not c.startswith("_")}
        sample_b = {c: df_b[c].dropna().unique()[:3].tolist() for c in df_b.columns if not c.startswith("_")}
        result = resolve_join_key(self.llm, table_a, sample_a, table_b, sample_b)

        if result is not None:
            key_a, key_b = result
            if key_a not in df_a.columns or key_b not in df_b.columns:
                # The LLM named a column that doesn't actually exist -
                # reject outright rather than crash later on a KeyError.
                result = None
            else:
                # A key that exists but doesn't semantically match real
                # values would otherwise cause df[key_a].map(...) to
                # silently produce NaN for every row - an invisible
                # failure that only surfaces much later as a confusing
                # NOT NULL violation. Verify real overlap first.
                overlap = df_a[key_a].isin(df_b[key_b]).mean()
                if overlap == 0:
                    result = None

        join_key_cache[cache_key] = result
        self._join_key_log[cache_key] = result
        return result

    def _find_unique_join_key(self, df_a: pd.DataFrame, df_b: pd.DataFrame) -> tuple[str, str] | None:
        """Like _find_deterministic_join_key, but for a use case that
        needs df_b's key to be UNIQUE (e.g. set_index + map, to attach
        exactly one value per row) - a many-to-one key (e.g. a person-
        level identifier repeated across several of their own visits)
        would silently attach the WRONG row's value to most matches
        instead of crashing outright, which is worse: a silent
        correctness issue rather than a visible failure (confirmed in
        production: subject_id, repeated across a patient's several
        visits, was found as a valid high-overlap candidate ahead of
        hadm_id, the genuinely unique visit-level key).

        Among every candidate pair clearing the overlap threshold,
        prefers the one where df_b's column has the FEWEST duplicate
        values - a perfectly unique key wins outright; if none is
        perfectly unique, the closest one is used rather than refusing
        entirely, since a mostly-unique key is still far better than an
        arbitrary pick."""
        candidates: list[tuple[float, float, tuple[str, str]]] = []  # (overlap, dup_ratio, (col_a, col_b))
        for col_a in df_a.columns:
            if col_a.startswith("_"):
                continue
            values_a = df_a[col_a].dropna()
            if values_a.empty:
                continue
            for col_b in df_b.columns:
                if col_b.startswith("_"):
                    continue
                values_b = df_b[col_b].dropna()
                if values_b.empty:
                    continue
                overlap = values_a.isin(values_b).mean()
                if overlap <= self._DETERMINISTIC_OVERLAP_THRESHOLD:
                    continue
                dup_ratio = 1 - (values_b.nunique() / len(values_b))
                candidates.append((overlap, dup_ratio, (col_a, col_b)))

        if not candidates:
            return None
        # Sort by uniqueness FIRST (fewest duplicates wins), overlap as
        # the tiebreaker - correctness (a real 1:1 key) matters more
        # here than which candidate happened to have marginally higher
        # overlap.
        candidates.sort(key=lambda c: (c[1], -c[0]))
        return candidates[0][2]

    def _find_deterministic_join_key(self, df_a: pd.DataFrame, df_b: pd.DataFrame) -> tuple[str, str] | None:
        """Scans column pairs for strong real-value overlap - if found,
        this is used instead of asking the LLM at all. Purely data-
        driven (no naming assumptions), so it generalizes beyond any
        one source's conventions while staying fully deterministic."""
        best: tuple[str, str] | None = None
        best_overlap = self._DETERMINISTIC_OVERLAP_THRESHOLD
        for col_a in df_a.columns:
            if col_a.startswith("_"):
                continue
            values_a = df_a[col_a].dropna()
            if values_a.empty:
                continue
            for col_b in df_b.columns:
                if col_b.startswith("_"):
                    continue
                values_b = df_b[col_b].dropna()
                if values_b.empty:
                    continue
                overlap = values_a.isin(values_b).mean()
                if overlap > best_overlap:
                    best_overlap = overlap
                    best = (col_a, col_b)
        return best

    @staticmethod
    def _apply_varchar_length_limits(target_table: str, rows: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
        """Truncates string values to fit their target column's REAL
        max length (introspected, never guessed) - prevents
        StringDataRightTruncation errors (e.g. a SNOMED concept_name
        used as visit_source_value exceeding varchar(50)) rather than
        letting the DB reject the whole batch over it. Truncation is
        NEVER silent: every truncated field is reported in the
        AgentResult output, since it does lose information."""
        try:
            columns_info = get_table_columns(target_table)
        except Exception:
            return rows, {}  # can't introspect (missing table, or no DB) - leave as-is

        max_lengths = {
            c["column_name"]: c["character_maximum_length"]
            for c in columns_info if c.get("character_maximum_length")
        }
        rows = rows.copy()
        truncated: dict[str, int] = {}
        for col in rows.columns:
            max_len = max_lengths.get(col)
            if max_len is None:
                continue
            lengths = rows[col].astype(str).str.len()
            too_long = lengths > max_len
            n_truncated = int(too_long.sum())
            if n_truncated:
                rows.loc[too_long, col] = rows.loc[too_long, col].astype(str).str.slice(0, max_len)
                truncated[col] = n_truncated
        return rows, truncated

    @staticmethod
    def _apply_fixed_type_concepts(target_table: str, rows: pd.DataFrame, batch_type_concepts: dict) -> pd.DataFrame:
        """Fills record-provenance fields (e.g. visit_type_concept_id)
        with THIS BATCH's declared ETL-convention value - provenance
        (EHR export, claim, registry...) is a fact about the batch/
        source, not the framework, so it's declared once per batch in
        that batch's own metadata.yaml (a `type_concepts:` section),
        confirmed against the actually-loaded vocabulary. A different
        source with different true provenance declares a different
        value; nothing here is hardcoded globally. Fields with no
        declared value fall back to concept_id 0 via
        _apply_concept_id_convention rather than a guess."""
        defaults = batch_type_concepts.get(target_table, {})
        if not defaults:
            return rows
        rows = rows.copy()
        for field, concept_id in defaults.items():
            rows[field] = concept_id
        return rows

    @staticmethod
    def _filter_low_confidence_plain_fields(structural_targets: list[dict]) -> list[dict]:
        """Excludes low-confidence structural resolutions from ever
        being used to assemble rows - a wrong guess is worse than no
        mapping at all, since it can silently populate a column with
        data that doesn't belong there.

        Two different confidence scales are in play, so two different
        thresholds:
          - Plain fields (source_value is None - the LLM's own
            field-matching guess): MIN_STRUCTURAL_CONFIDENCE (0.3).
          - Vocabulary-field records (source_value set, e.g.
            ethnicity_concept_id): MIN_VOCAB_FIELD_CONFIDENCE (0.55) -
            OUR OWN well-defined tier system from semantic_mapper.py
            (1.0 exact code, 0.95 exact name, 0.7 substring, 0.5 fuzzy
            trigram). The fuzzy tier is deliberately excluded here: a
            typo-tolerant last-resort match is exactly what produces
            false positives for narrow vocabularies (e.g. OMOP's
            'Ethnicity' only has Hispanic/Not-Hispanic - a source
            column combining race AND ethnicity, as MIMIC-III's
            ADMISSIONS.ethnicity does, will correctly find nothing
            exact for a race value like 'ASIAN', and the fuzzy fallback
            must not be trusted to fill that gap with a coincidental
            character-overlap guess)."""
        filtered = []
        for m in structural_targets:
            confidence = m.get("confidence")
            if confidence is None:
                filtered.append(m)
                continue
            is_plain_field = m.get("source_value") is None
            threshold = MIN_STRUCTURAL_CONFIDENCE if is_plain_field else MIN_VOCAB_FIELD_CONFIDENCE
            if confidence < threshold:
                continue
            filtered.append(m)
        return filtered

    @staticmethod
    def _assign_primary_key(target_table: str, rows: pd.DataFrame) -> pd.DataFrame:
        """Generates this table's own surrogate primary key (e.g.
        visit_occurrence_id) - sequential, in-memory, valid for this run
        only, same convention as person_id. A table's own primary key is
        NEVER sourced from the data; it must always be assigned here."""
        pk_field = PRIMARY_KEY_FIELD.get(target_table)
        if pk_field is None:
            return rows
        rows = rows.copy()
        rows[pk_field] = range(1, len(rows) + 1)
        return rows

    @staticmethod
    def _apply_concept_id_convention(target_table: str, rows: pd.DataFrame) -> pd.DataFrame:
        """OMOP CDM convention: an unmapped concept field is represented
        by concept_id 0 ("No matching concept"), never NULL - even
        NOT NULL columns are satisfied by this. Applied here rather than
        earlier in the pipeline because it's specifically a LOADING
        convention (Mapping/Transformation correctly represent "no match
        found" as a real None, which is the honest intermediate state).

        Also CREATES missing *_concept_id columns that the live OMOP DDL
        marks as NOT NULL (e.g. condition_type_concept_id). Those are
        provenance / type-concept fields that Mapping correctly leaves
        unresolved when no source column exists; without a batch-level
        type_concepts declaration they would be omitted from the
        DataFrame, to_sql would skip them, and Postgres would reject the
        INSERT with NotNullViolation. Defaulting to 0 is the CDM-safe
        fallback (see _apply_fixed_type_concepts when metadata does
        declare a real type concept)."""
        rows = rows.copy()
        # Fill existing concept_id columns
        for col in list(rows.columns):
            if col.endswith("concept_id"):
                rows[col] = rows[col].fillna(0).astype("int64")
        # Ensure NOT NULL concept_id columns from the live DDL exist
        try:
            columns_info = get_table_columns(target_table)
        except Exception:
            return rows
        for c in columns_info:
            name = c.get("column_name") or ""
            if not name.endswith("concept_id"):
                continue
            if (c.get("is_nullable") or "YES").upper() == "YES":
                continue
            if name not in rows.columns:
                rows[name] = 0
            else:
                rows[name] = rows[name].fillna(0).astype("int64")
        return rows

    def _finalize_rows(
        self, target_table: str, rows: pd.DataFrame, batch_type_concepts: dict
    ) -> tuple[pd.DataFrame, dict, dict, dict]:
        """Applies every per-table convention in the right order - shared
        by both regular tables and the derived OBSERVATION_PERIOD, so
        the latter gets the exact same treatment (primary key, fixed
        type concepts, varchar limits, concept_id defaults, date
        conventions) as everything else, not a special case."""
        rows = self._assign_primary_key(target_table, rows)
        rows = self._apply_fixed_type_concepts(target_table, rows, batch_type_concepts)
        rows, truncated = self._apply_varchar_length_limits(target_table, rows)
        rows = self._apply_concept_id_convention(target_table, rows)
        rows, concept_drop_diagnostic = self._drop_rows_missing_required_concept(target_table, rows)
        rows = self._apply_omop_date_conventions(target_table, rows)
        rows, date_drop_diagnostic = self._drop_rows_missing_required_date(target_table, rows)
        return rows, truncated, date_drop_diagnostic, concept_drop_diagnostic

    @staticmethod
    def _compute_observation_period(finalized_rows: dict[str, pd.DataFrame]) -> pd.DataFrame | None:
        """OBSERVATION_PERIOD is derived from VISIT_OCCURRENCE, one
        period per hospital stay (or per group of overlapping/adjacent
        stays), NEVER a single min/max span across every clinical event
        a person ever had.

        This follows OMOP's own documented convention (OHDSI
        CommonDataModel wiki): "no two observation periods can overlap
        in time for a given person", and "absence of data indicates
        that no clinical events occurred to the patient" - confirmed by
        OHDSI's own EHR guidance, which gives the exact scenario this
        replaces: a multi-year gap between two clusters of clinical
        events must produce TWO separate observation periods, never one
        that falsely implies continuous observation through the gap.

        For a source like MIMIC, the institution only observes a
        patient WHILE ADMITTED (no outpatient/ambulatory continuous
        coverage exists here at all) - so the natural period boundary
        is the hospital stay itself. This mirrors how other episodic-
        data ETLs handle the same field (e.g. the OHDSI ETL-LambdaBuilder
        specification for Premier: observation_period dates are taken
        directly from visit_occurrence's own dates).

        Visits for the same person that overlap or are immediately
        adjacent (one starts on or before the previous one's end) are
        merged into a single period; a genuine gap between two
        admissions produces two separate, non-overlapping periods."""
        visits = finalized_rows.get("visit_occurrence")
        if visits is None or visits.empty:
            return None
        if "person_id" not in visits.columns or "visit_start_date" not in visits.columns:
            return None

        df = visits[["person_id", "visit_start_date"]].copy()
        df["visit_end_date"] = visits["visit_end_date"] if "visit_end_date" in visits.columns else visits["visit_start_date"]
        df = df.dropna(subset=["person_id", "visit_start_date"])
        df["visit_end_date"] = df["visit_end_date"].fillna(df["visit_start_date"])
        if df.empty:
            return None

        periods = []
        for person_id, group in df.groupby("person_id"):
            group = group.sort_values("visit_start_date")
            current_start, current_end = None, None
            for _, row in group.iterrows():
                start, end = row["visit_start_date"], row["visit_end_date"]
                if current_start is None:
                    current_start, current_end = start, end
                elif start <= current_end:
                    # Overlapping or same-day adjacent stay - part of
                    # the same continuous period, extend it.
                    current_end = max(current_end, end)
                else:
                    # A real gap - this institution had no information
                    # about the person during it. Close the current
                    # period and start a genuinely new, separate one.
                    periods.append({
                        "person_id": person_id,
                        "observation_period_start_date": current_start,
                        "observation_period_end_date": current_end,
                    })
                    current_start, current_end = start, end
            if current_start is not None:
                periods.append({
                    "person_id": person_id,
                    "observation_period_start_date": current_start,
                    "observation_period_end_date": current_end,
                })

        if not periods:
            return None
        return pd.DataFrame(periods)

    @staticmethod
    def _apply_omop_date_conventions(target_table: str, rows: pd.DataFrame) -> pd.DataFrame:
        """OMOP CDM conventions for required date fields:

        1. drug_exposure_end_date/end_datetime missing (e.g. an ongoing
           Synthea medication where STOP is blank) - documented OHDSI
           convention when the true end is unknown: default to
           drug_exposure_start_date/start_datetime.

        2. For EVERY domain-driven event table's primary required date
           field (measurement_date, condition_start_date, procedure_date,
           observation_date, drug_exposure_start_date): if the plain
           `_date` version is missing but the `_datetime` version was
           resolved (or vice versa) - same underlying event, just
           resolved through a different structural mapping call (see
           MappingAgent._resolve_all_target_fields's per-contributing-
           source-table resolution) - reconcile them rather than leaving
           one genuinely-known value unused while its NOT NULL sibling
           column fails the insert."""
        rows = rows.copy()

        primary_date_field = PRIMARY_REQUIRED_DATE_FIELD.get(target_table)
        if primary_date_field:
            date_col, datetime_col = primary_date_field
            if date_col in rows.columns and datetime_col in rows.columns:
                # date missing, datetime known -> derive the date part.
                # Runs BEFORE the drug_exposure-specific end<-start
                # fallback below - otherwise that fallback could copy a
                # still-null start_date into end_date, before start_date
                # itself ever gets the chance to be derived here
                # (confirmed in production: an INPUTEVENTS_MV-derived
                # drug_exposure row with only start_datetime/end_datetime
                # resolved, no plain start_date/end_date at all, ended up
                # with a permanently NULL end_date because of this exact
                # ordering).
                missing_date = rows[date_col].isna() & rows[datetime_col].notna()
                if missing_date.any():
                    rows.loc[missing_date, date_col] = pd.to_datetime(
                        rows.loc[missing_date, datetime_col]
                    ).dt.date
                # datetime missing, date known -> reuse the date as-is
                # (no time component to add, but satisfies NOT NULL if
                # the datetime column also happens to require one).

        if target_table == "drug_exposure":
            if "drug_exposure_start_date" in rows.columns and "drug_exposure_end_date" in rows.columns:
                missing = rows["drug_exposure_end_date"].isna()
                rows.loc[missing, "drug_exposure_end_date"] = rows.loc[missing, "drug_exposure_start_date"]
            if "drug_exposure_start_datetime" in rows.columns and "drug_exposure_end_datetime" in rows.columns:
                missing = rows["drug_exposure_end_datetime"].isna()
                rows.loc[missing, "drug_exposure_end_datetime"] = rows.loc[missing, "drug_exposure_start_datetime"]

        return rows

    @staticmethod
    def _drop_rows_missing_required_date(target_table: str, rows: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
        """For domain-driven event tables, drop rows whose primary
        required date is STILL null after every resolution attempt and
        convention fallback (see _apply_omop_date_conventions) - these
        are rows contributed by a source table with no resolvable date
        field mapped for it at all (e.g. a code from a table Mapping
        never found a date for). Rather than crash the entire batch on
        a NOT NULL violation, these specific rows are excluded - with a
        clear diagnostic (count + sample source values) so the gap
        stays visible and actionable, rather than silently lost or
        blocking every other correctly-resolved row in the same table.

        If the required date column is MISSING ENTIRELY (never resolved
        by Mapping for ANY row in this table - e.g. VISIT_OCCURRENCE's
        visit_start_date when the batch has no admissions-level source
        table at all), every row is dropped - but ONLY if the live DDL
        actually marks that column NOT NULL. Never assumed: a field
        that's genuinely nullable in this DDL is fine left unresolved
        (equivalent to every value being NULL, which the database
        itself accepts) - dropping rows based on an unconfirmed
        assumption would be worse than the problem it prevents."""
        primary = PRIMARY_REQUIRED_DATE_FIELD.get(target_table)
        if primary is None:
            return rows, {}
        date_col, _ = primary

        if date_col not in rows.columns:
            try:
                columns_info = get_table_columns(target_table)
            except Exception:
                return rows, {}
            column_info = next((c for c in columns_info if c.get("column_name") == date_col), None)
            is_not_null = column_info is not None and (column_info.get("is_nullable") or "YES").upper() == "NO"
            if not is_not_null:
                return rows, {}
            diagnostic = {
                "dropped_rows": len(rows),
                "reason": f"{date_col} is NOT NULL in the real DDL but was never resolved for this "
                          f"table at all (the column doesn't exist in the assembled data) - every row "
                          f"dropped rather than crashing on insert.",
                "sample_source_values": [],
            }
            return rows.iloc[0:0].reset_index(drop=True), diagnostic

        missing = rows[date_col].isna()
        if not missing.any():
            return rows, {}

        template = TABLE_FIELD_TEMPLATES.get(target_table, {})
        source_value_field = template.get("source_value_field")
        sample_values = (
            rows.loc[missing, source_value_field].dropna().unique()[:5].tolist()
            if source_value_field and source_value_field in rows.columns
            else []
        )
        diagnostic = {
            "dropped_rows": int(missing.sum()),
            "reason": f"{date_col} could not be resolved for these rows - "
                      f"no date field was mapped for their contributing source table.",
            "sample_source_values": sample_values,
        }
        return rows[~missing].reset_index(drop=True), diagnostic

    @staticmethod
    def _drop_rows_missing_required_concept(target_table: str, rows: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
        """For structural tables with a PRIMORDIAL concept field (see
        PRIMARY_REQUIRED_CONCEPT_FIELD), drop rows where that field was
        never actually resolved - i.e. still at 0 ("No matching
        concept") after _apply_concept_id_convention's NOT-NULL
        fallback. A row satisfying only the database's NOT NULL
        constraint (via the 0 default) but never actually resolving its
        defining concept (e.g. a "visit" with no visit_concept_id at
        all) is not a semantically meaningful record - excluded here
        rather than silently inserted as a technically-valid but
        clinically-empty row.

        Must run AFTER _apply_concept_id_convention specifically:
        before that step the field may still be a genuine NULL (not yet
        defaulted to 0), which this check would not catch."""
        concept_field = PRIMARY_REQUIRED_CONCEPT_FIELD.get(target_table)
        if concept_field is None:
            return rows, {}
        if concept_field not in rows.columns:
            return rows, {}

        # Only treat 0 as "never resolved" if this field is confirmed
        # NOT NULL in the live DDL - same principle as volet 3's date
        # check. If the field is genuinely nullable, a 0 could
        # legitimately be real data unrelated to "unresolved", and
        # _apply_concept_id_convention's unconditional fillna(0) (which
        # doesn't itself check nullability for EXISTING columns) must
        # not be mistaken for a definitive "this was never resolved"
        # signal without checking the real schema first.
        try:
            columns_info = get_table_columns(target_table)
        except Exception:
            return rows, {}
        column_info = next((c for c in columns_info if c.get("column_name") == concept_field), None)
        is_not_null = column_info is not None and (column_info.get("is_nullable") or "YES").upper() == "NO"
        if not is_not_null:
            return rows, {}

        missing = rows[concept_field] == 0
        if not missing.any():
            return rows, {}

        template = TABLE_FIELD_TEMPLATES.get(target_table, {})
        source_value_field = template.get("source_value_field")
        sample_values = (
            rows.loc[missing, source_value_field].dropna().unique()[:5].tolist()
            if source_value_field and source_value_field in rows.columns
            else []
        )
        diagnostic = {
            "dropped_rows": int(missing.sum()),
            "reason": f"{concept_field} could not be resolved for these rows (defaulted to 0 = "
                      f"'No matching concept') - a row with no primordial concept is not a "
                      f"meaningful record, regardless of satisfying the NOT NULL constraint.",
            "sample_source_values": sample_values,
        }
        return rows[~missing].reset_index(drop=True), diagnostic

    @staticmethod
    def _find_field_source(structural_targets, target_table, target_field):
        for m in structural_targets:
            if m.get("target_table") == target_table and m.get("target_field") == target_field:
                return m.get("source_table"), m.get("source_field")
        return None, None

    # ------------------------------------------------------------------
    # promote_final
    # ------------------------------------------------------------------
    def _promote_final(self, state: dict[str, Any]) -> AgentResult:
        per_table_result = {}
        for table in LOAD_ORDER:
            try:
                per_table_result[table] = promote_to_final(table)
            except Exception as exc:
                per_table_result[table] = {"skipped": True, "reason": str(exc)}

        source_path = state.get("source_path")
        if source_path:
            mark_status(state["source_name"], source_path, "SUCCESS")

        result = AgentResult(
            execution_id=state["execution_id"], agent_name=self.name, status=AgentStatus.SUCCESS,
            output={"per_table": per_table_result},
            reasoning_summary=f"Promoted {len(per_table_result)} table(s) from OMOP_TEMP to OMOP_FINAL (append).",
        )
        return self.persist(result, stage_override="loading_promote_final")
