"""Mapping snapshots: keep the complete mapping of a validated batch and
replay it on another batch of the SAME source.

What is replayed, and what is not
---------------------------------
The Mapping Agent makes two kinds of decisions:

* decisions of the language model: which source column fills a target
  field, which dictionary table a local identifier joins to, which other
  column a vocabulary field should be read from when the first one
  matched nothing;
* deterministic decisions: the vocabulary searches that turn a raw code or
  label into a concept.

A replay freezes the first kind and recomputes the second. The model is
therefore not called for anything the snapshot covers, while a code that
did not exist in the first batch is still resolved against the vocabulary
like in any normal run. The complete mapping of the original batch is kept
inside the snapshot as an audit copy, and after a replay the concepts of
the values present in both batches are compared (``value_drift``), which
reveals a vocabulary update or a changed curated file.

Nothing here is source specific, and nothing is replayed silently across
sources: a snapshot belongs to one source and is refused for another.

A snapshot holds distinct codes and labels, never patient rows.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SNAPSHOT_FORMAT = 1
ON_MISMATCH_CHOICES = ("fallback", "fail")
_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


class MappingReplayError(RuntimeError):
    """A snapshot cannot be used as asked (wrong source, strict mode, ...)."""


# ----------------------------------------------------------------------
# Files
# ----------------------------------------------------------------------
def snapshot_dir() -> Path:
    return Path(os.getenv("MAPPING_SNAPSHOT_DIR", "mappings"))


def snapshot_path(source_name: str, name: str) -> Path:
    for label, value in (("source", source_name), ("snapshot name", name)):
        if not _NAME_RE.match(value or ""):
            raise ValueError(f"Invalid {label} '{value}': use letters, digits, '.', '_' or '-'.")
    return snapshot_dir() / source_name / f"{name}.json"


def save_snapshot(snapshot: dict[str, Any], overwrite: bool = False) -> Path:
    path = snapshot_path(snapshot["source_name"], snapshot["name"])
    if path.exists() and not overwrite:
        raise FileExistsError(f"Mapping snapshot '{path}' already exists (use overwrite to replace it).")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(snapshot, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
    return path


def load_snapshot(source_name: str, name: str) -> dict[str, Any]:
    path = snapshot_path(source_name, name)
    if not path.exists():
        raise FileNotFoundError(f"Mapping snapshot '{name}' not found for source '{source_name}' (looked in {path}).")
    return json.loads(path.read_text(encoding="utf-8"))


# ----------------------------------------------------------------------
# Building a snapshot
# ----------------------------------------------------------------------
def get_vocabulary_version() -> str | None:
    """Release label of the Athena vocabularies loaded in cdm_vocab, or None
    when it cannot be read (no database, no VOCABULARY row)."""
    try:
        from sqlalchemy import text

        from app.tools.database.db import session_scope

        with session_scope() as session:
            row = session.execute(
                text("SELECT vocabulary_version FROM cdm_vocab.vocabulary WHERE vocabulary_id = 'None'")
            ).first()
            return row[0] if row and row[0] else None
    except Exception:  # noqa: BLE001 - informational only
        return None


def _sha256(path: Path) -> str | None:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def build_fingerprint(tables: dict[str, Any], batch_cfg: dict, source_folder: Path | None) -> dict[str, Any]:
    """A compact description of the batch a mapping was made for. Used to
    explain WHY a replay is risky, never to decide silently."""
    declared = sorted(
        [table, field, standard]
        for table, fields in (batch_cfg.get("tables") or {}).items()
        for field, standard in fields.items()
        if standard
    )
    curated: dict[str, str | None] = {}
    for fields in (batch_cfg.get("fixed_value_mappings") or {}).values():
        for spec in fields.values():
            mapping_file = spec.get("mapping_file")
            if mapping_file and source_folder is not None:
                curated[str(mapping_file)] = _sha256(Path(source_folder) / mapping_file)
    return {
        "tables": {
            name.lower(): sorted(c.lower() for c in df.columns if not str(c).startswith("_"))
            for name, df in tables.items()
        },
        "declared_coded_fields": declared,
        "curated_files": curated,
    }


def derive_frozen(mapping_output: dict[str, Any]) -> dict[str, Any]:
    """Extracts, from the output of a Mapping run, exactly the decisions a
    replay must not ask the model again."""
    plain = [
        {k: r.get(k) for k in ("target_table", "target_field", "source_table", "source_field", "confidence", "reason")}
        for r in mapping_output.get("structural_target_mappings", [])
        if r.get("source_value") is None and r.get("source_table") and r.get("source_field")
    ]
    return {
        "plain_fields": plain,
        "plain_field_scopes": list(mapping_output.get("plain_field_scopes", [])),
        "vocab_sources": list(mapping_output.get("vocab_field_sources", [])),
        "local_vocab_joins": dict(mapping_output.get("local_vocab_joins", {})),
        "local_vocab_join_failed": sorted((mapping_output.get("local_vocab_join_failures") or {}).keys()),
    }


def build_snapshot(
    *,
    name: str,
    source_name: str,
    execution_id: str,
    batch_folder: str | None,
    mapping_output: dict[str, Any],
    tables: dict[str, Any],
    batch_cfg: dict,
    source_folder: Path | None,
    llm_provider: str | None = None,
    llm_model: str | None = None,
    cdm_version: str | None = None,
    vocabulary_version: str | None = None,
) -> dict[str, Any]:
    return {
        "snapshot_format": SNAPSHOT_FORMAT,
        "name": name,
        "source_name": source_name,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "created_from": {
            "execution_id": execution_id,
            "batch": Path(batch_folder).name if batch_folder else None,
            "llm_provider": llm_provider,
            "llm_model": llm_model,
        },
        "environment": {"cdm_version": cdm_version, "vocabulary_version": vocabulary_version},
        "fingerprint": build_fingerprint(tables, batch_cfg, source_folder),
        "frozen": derive_frozen(mapping_output),
        # The complete mapping of the original batch: audit copy and
        # reference for value_drift. Replay itself reads only "frozen".
        "mapping": mapping_output,
    }


def save_snapshot_from_final_state(
    final_state: dict[str, Any], name: str, overwrite: bool = False
) -> tuple[Path | None, str]:
    """Saves the mapping of a finished run, but only if that run reached
    promotion: a mapping whose batch failed validation must not become the
    reference every later batch is replayed from."""
    if not final_state.get("promote_output") or final_state.get("failure_event"):
        return None, "the run did not reach promotion (validation failed or the run stopped), so nothing was saved"
    mapping_output = final_state.get("mapping_output")
    if not mapping_output:
        return None, "the run has no mapping output"

    from app.models.config import get_llm_config
    from app.tools.data.metadata_loader import source_root_path

    source_name = final_state["source_name"]
    llm_cfg = get_llm_config()
    snapshot = build_snapshot(
        name=name,
        source_name=source_name,
        execution_id=final_state["execution_id"],
        batch_folder=final_state.get("source_path"),
        mapping_output=mapping_output,
        tables=final_state.get("_raw_tables") or {},
        batch_cfg=final_state.get("batch_metadata") or {},
        source_folder=source_root_path(source_name),
        llm_provider=llm_cfg.provider,
        llm_model=llm_cfg.model,
        cdm_version=os.getenv("CDM_VERSION", "5.4"),
        vocabulary_version=get_vocabulary_version(),
    )
    return save_snapshot(snapshot, overwrite=overwrite), "saved"


# ----------------------------------------------------------------------
# Value drift
# ----------------------------------------------------------------------
def _value_index(mapping_output: dict[str, Any]) -> dict[tuple[str, str, str], Any]:
    index: dict[tuple[str, str, str], Any] = {}
    for table in (mapping_output.get("per_table") or {}).values():
        for rec in table.get("semantic_mapping", []):
            key = ("semantic", str(rec.get("field", "")).lower(), str(rec.get("source_value")))
            index[key] = rec.get("target_concept_id")
    for rec in mapping_output.get("structural_target_mappings", []):
        if rec.get("source_value") is not None:
            field = f"{rec.get('target_table')}.{rec.get('target_field')}".lower()
            index[("vocab", field, str(rec["source_value"]))] = rec.get("target_concept_id")
    return index


def compute_value_drift(old_output: dict[str, Any], new_output: dict[str, Any], limit: int = 20) -> dict[str, Any]:
    """Compares the concepts chosen for the values present in BOTH the
    original mapping and the replayed one. A non-zero ``changed`` means the
    same raw value now resolves to another concept: vocabulary update,
    changed curated file or changed declaration."""
    old, new = _value_index(old_output), _value_index(new_output)
    common = old.keys() & new.keys()
    changed = sorted(k for k in common if old[k] != new[k])
    return {
        "compared": len(common),
        "changed": len(changed),
        "new_values": len(new.keys() - old.keys()),
        "changed_examples": [
            {"kind": k[0], "field": k[1], "source_value": k[2], "was": old[k], "now": new[k]} for k in changed[:limit]
        ],
    }


# ----------------------------------------------------------------------
# Replay plan
# ----------------------------------------------------------------------
class ReplayPlan:
    """What the Mapping Agent consults instead of the model.

    ``on_mismatch`` decides what happens to a decision the snapshot cannot
    provide for this batch (a column that no longer exists, a source table
    that feeds an event table for the first time):

    * ``fallback`` (default): it is resolved automatically, as in a normal
      run, and listed in the report;
    * ``fail``: the run stops with ``MappingReplayError``.
    """

    def __init__(
        self,
        snapshot: dict[str, Any],
        *,
        tables: dict[str, Any],
        batch_cfg: dict,
        source_name: str,
        source_folder: Path | None = None,
        on_mismatch: str = "fallback",
        cdm_version: str | None = None,
        vocabulary_version: str | None = None,
    ):
        if on_mismatch not in ON_MISMATCH_CHOICES:
            raise ValueError(f"on_mismatch must be one of {ON_MISMATCH_CHOICES}, got '{on_mismatch}'")
        self.snapshot = snapshot
        self.name = snapshot.get("name", "?")
        self.on_mismatch = on_mismatch
        self._tables = tables
        self._table_names = {t.lower(): t for t in tables}
        self._column_names = {t: {str(c).lower(): c for c in df.columns} for t, df in tables.items()}

        frozen = snapshot.get("frozen", {})
        self._plain: dict[tuple[str, str], list[dict]] = {}
        for entry in frozen.get("plain_fields", []):
            self._plain.setdefault((entry["target_table"], entry["target_field"]), []).append(entry)
        self._scopes = {
            (s["target_table"], (s.get("source_table") or "").lower()) for s in frozen.get("plain_field_scopes", [])
        }
        # A vocabulary field can be read from several source columns (one per
        # source table); the snapshot keeps all of them, in order.
        self._vocab_sources: dict[tuple[str, str], list[dict]] = {}
        for v in frozen.get("vocab_sources", []):
            self._vocab_sources.setdefault((v["target_table"], v["target_field"]), []).append(v)
        self._joins = {k.lower(): v for k, v in frozen.get("local_vocab_joins", {}).items()}
        self._joins_failed = {k.lower() for k in frozen.get("local_vocab_join_failed", [])}

        self.report: dict[str, Any] = {
            "snapshot": self.name,
            "created_from": snapshot.get("created_from", {}),
            "on_mismatch": on_mismatch,
            "reused": {"plain_fields": 0, "plain_fields_unresolved_in_snapshot": 0, "vocab_sources": 0, "local_joins": 0},
            "fallbacks": [],
            "rejected": [],
            "warnings": [],
            "value_drift": None,
        }
        self._check_compatibility(source_name, batch_cfg, source_folder, cdm_version, vocabulary_version)

    # -- compatibility --------------------------------------------------
    def _check_compatibility(
        self, source_name: str, batch_cfg: dict, source_folder: Path | None,
        cdm_version: str | None, vocabulary_version: str | None,
    ) -> None:
        errors: list[str] = []
        if self.snapshot.get("snapshot_format") != SNAPSHOT_FORMAT:
            errors.append(
                f"unsupported snapshot format {self.snapshot.get('snapshot_format')!r} (expected {SNAPSHOT_FORMAT})"
            )
        if self.snapshot.get("source_name") != source_name:
            errors.append(
                f"the snapshot belongs to source '{self.snapshot.get('source_name')}', not '{source_name}'"
            )
        env = self.snapshot.get("environment", {})
        if env.get("cdm_version") and cdm_version and env["cdm_version"] != cdm_version:
            errors.append(f"CDM version differs (snapshot {env['cdm_version']}, current {cdm_version})")
        if errors:
            raise MappingReplayError(f"Cannot replay mapping snapshot '{self.name}': " + "; ".join(errors) + ".")

        warnings = self.report["warnings"]
        if env.get("vocabulary_version") and vocabulary_version and env["vocabulary_version"] != vocabulary_version:
            warnings.append(
                f"vocabulary release differs (snapshot '{env['vocabulary_version']}', current "
                f"'{vocabulary_version}'): concepts may have changed, see value_drift"
            )

        fp = self.snapshot.get("fingerprint", {})
        current = build_fingerprint(self._tables, batch_cfg, source_folder)
        old_cols, new_cols = fp.get("tables", {}), current["tables"]
        new_tables = sorted(set(new_cols) - set(old_cols))
        gone_tables = sorted(set(old_cols) - set(new_cols))
        if new_tables:
            warnings.append(f"table(s) not in the snapshot's batch: {', '.join(new_tables)}")
        if gone_tables:
            warnings.append(f"table(s) of the snapshot's batch absent from this batch: {', '.join(gone_tables)}")
        for table in sorted(set(old_cols) & set(new_cols)):
            added, removed = sorted(set(new_cols[table]) - set(old_cols[table])), sorted(set(old_cols[table]) - set(new_cols[table]))
            if added:
                warnings.append(f"{table}: new column(s) {', '.join(added)}")
            if removed:
                warnings.append(f"{table}: missing column(s) {', '.join(removed)}")

        old_decl = {tuple(x) for x in fp.get("declared_coded_fields", [])}
        new_decl = {tuple(x) for x in current["declared_coded_fields"]}
        if old_decl != new_decl:
            warnings.append(
                f"coded-field declarations differ from the snapshot's batch "
                f"(+{len(new_decl - old_decl)} / -{len(old_decl - new_decl)})"
            )
        for fname in sorted(set(fp.get("curated_files", {})) | set(current["curated_files"])):
            if fp.get("curated_files", {}).get(fname) != current["curated_files"].get(fname):
                warnings.append(f"curated mapping file '{fname}' changed since the snapshot was made")

    # -- helpers --------------------------------------------------------
    def _actual_table(self, name: str | None) -> str | None:
        return self._table_names.get((name or "").lower())

    def _actual_column(self, table: str | None, column: str | None) -> str | None:
        if table is None:
            return None
        return self._column_names.get(table, {}).get((column or "").lower())

    def note_fallback(self, kind: str, detail: str) -> None:
        self.report["fallbacks"].append({"kind": kind, "detail": detail})
        if self.on_mismatch == "fail":
            raise MappingReplayError(
                f"Mapping snapshot '{self.name}' does not cover this batch ({kind}: {detail}) "
                f"and on_mismatch is 'fail'."
            )

    # -- plain fields (decided by the model in a normal run) ------------
    def plain_resolutions(
        self, target_table: str, plain_fields: list[str], scope_source: str | None
    ) -> tuple[list[dict], list[str]]:
        """Returns (frozen entries ready to use, fields that must be resolved
        the normal way). A field the snapshot examined and found no source
        for is neither: it stays unresolved, exactly as it did originally.

        ``scope_source`` is the single source table of an event table's
        resolution (each contributing source table is resolved separately),
        or None for the other tables."""
        if (target_table, (scope_source or "").lower()) not in self._scopes:
            self.note_fallback("plain_scope", f"{target_table} fed by {scope_source or 'the batch'} is not in the snapshot")
            return [], list(plain_fields)

        entries: list[dict] = []
        uncovered: list[str] = []
        for field in plain_fields:
            candidates = self._plain.get((target_table, field), [])
            if scope_source is not None:
                candidates = [c for c in candidates if c["source_table"].lower() == scope_source.lower()]
            if not candidates:
                self.report["reused"]["plain_fields_unresolved_in_snapshot"] += 1
                continue
            chosen = candidates[0]
            table = self._actual_table(chosen["source_table"])
            column = self._actual_column(table, chosen["source_field"])
            if column is None:
                self.note_fallback(
                    "plain_field",
                    f"{target_table}.{field} <- {chosen['source_table']}.{chosen['source_field']} not found in this batch",
                )
                uncovered.append(field)
                continue
            entries.append({**chosen, "source_table": table, "source_field": column})
            self.report["reused"]["plain_fields"] += 1
        return entries, uncovered

    # -- vocabulary fields ----------------------------------------------
    def vocab_sources(self, target_table: str, concept_field: str) -> list[tuple[str, str]]:
        """The columns a vocabulary field was finally read from (after any
        retry in the original run), one per source table; empty when the
        snapshot has nothing. A column that no longer exists in this batch
        is reported as a fallback and left out."""
        found: list[tuple[str, str]] = []
        for entry in self._vocab_sources.get((target_table, concept_field), []):
            table = self._actual_table(entry["source_table"])
            column = self._actual_column(table, entry["source_field"])
            if column is None:
                self.note_fallback(
                    "vocab_source",
                    f"{target_table}.{concept_field} <- {entry['source_table']}.{entry['source_field']} not found in this batch",
                )
                continue
            self.report["reused"]["vocab_sources"] += 1
            found.append((table, column))
        return found

    def vocab_source(self, target_table: str, concept_field: str) -> tuple[str, str] | None:
        """First column of vocab_sources(), kept for callers that expect one."""
        sources = self.vocab_sources(target_table, concept_field)
        return sources[0] if sources else None

    # -- local vocabulary joins -----------------------------------------
    def local_join(self, table: str, field: str) -> tuple[str, Any]:
        """('hit', join_spec) | ('failed', reason) | ('miss', None)."""
        key = f"{table}.{field}".lower()
        if key in self._joins_failed:
            return "failed", "No valid join was found for this field when the snapshot was made (replayed)."
        spec = self._joins.get(key)
        if spec is None:
            self.note_fallback("local_join", f"{table}.{field} is not in the snapshot")
            return "miss", None

        join_table = self._actual_table(spec.get("join_table"))
        if join_table is None:
            self.note_fallback("local_join", f"{table}.{field}: dictionary table '{spec.get('join_table')}' not found in this batch")
            return "miss", None
        translated = dict(spec)
        translated["join_table"] = join_table
        translated["join_key_target"] = self._actual_column(join_table, spec.get("join_key_target")) or spec.get("join_key_target")
        translated["resolved_column"] = self._actual_column(join_table, spec.get("resolved_column")) or spec.get("resolved_column")
        fact_table = self._actual_table(table)
        translated["join_key_source"] = self._actual_column(fact_table, spec.get("join_key_source")) or spec.get("join_key_source")
        self.report["reused"]["local_joins"] += 1
        return "hit", translated

    def join_rejected(self, table: str, field: str, reason: str) -> None:
        """A replayed join that failed the real-overlap check on this batch."""
        self.report["rejected"].append({"kind": "local_join", "detail": f"{table}.{field}: {reason}"})
        if self.on_mismatch == "fail":
            raise MappingReplayError(
                f"Replayed join for {table}.{field} was rejected on this batch ({reason}) and on_mismatch is 'fail'."
            )

    # -- report ----------------------------------------------------------
    def markdown_section(self) -> str:
        r = self.report
        lines = [
            "## Replayed mapping",
            "",
            f"- Snapshot: `{r['snapshot']}` (made from run `{r['created_from'].get('execution_id')}`, "
            f"batch `{r['created_from'].get('batch')}`, model `{r['created_from'].get('llm_model')}`)",
            f"- Policy when the snapshot does not cover a decision: `{r['on_mismatch']}`",
            f"- Reused without asking the model: {r['reused']['plain_fields']} plain field(s), "
            f"{r['reused']['vocab_sources']} vocabulary source(s), {r['reused']['local_joins']} local join(s)",
            f"- Fields the snapshot had left unresolved (kept unresolved): "
            f"{r['reused']['plain_fields_unresolved_in_snapshot']}",
            f"- Resolved the normal way (not covered): {len(r['fallbacks'])}",
            f"- Replayed joins rejected on this batch: {len(r['rejected'])}",
        ]
        drift = r.get("value_drift")
        if drift:
            lines.append(
                f"- Value drift: {drift['changed']} of {drift['compared']} common value(s) resolve to another "
                f"concept; {drift['new_values']} value(s) are new in this batch"
            )
        for title, items in (("Not covered", r["fallbacks"]), ("Rejected", r["rejected"])):
            if items:
                lines += ["", f"### {title}", *[f"- {i['kind']}: {i['detail']}" for i in items]]
        if r["warnings"]:
            lines += ["", "### Warnings", *[f"- {w}" for w in r["warnings"]]]
        if drift and drift["changed_examples"]:
            lines += ["", "### Changed concepts (first examples)"]
            lines += [
                f"- {e['field']} = `{e['source_value']}`: {e['was']} -> {e['now']}" for e in drift["changed_examples"]
            ]
        return "\n".join(lines)
