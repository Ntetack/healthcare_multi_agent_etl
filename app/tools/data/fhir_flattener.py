"""
FHIR flattener: turns FHIR resources into wide, string-valued tables, one
table per resource type, whose columns are FHIR element paths.

Why a wide table and not one row per value: every downstream agent
(Profiling, Mapping, Transformation, Loading) reasons about COLUMNS, their
sample values and the join keys between tables. A table whose columns are
`code.code`, `onsetDateTime` or `subject.id` is something they already
know how to use, exactly as for a CSV export. Nothing downstream needs to
know that the data came from FHIR.

Flattening rules (deterministic, no model call):

  - Nested objects become dotted paths: `period.start`, `valueQuantity.unit`.
  - A CodeableConcept keeps ONE coding, lifted to its parent path:
    `code.system`, `code.code`, `code.display` (plus `code.text`). The
    chosen coding is the first one whose system is in `known_systems`,
    otherwise the first one. If there are several codings, all of them
    are kept as JSON in `code.coding.json_all`.
  - A Reference keeps its raw text and, when it can be resolved, the id of
    the target resource: `subject.reference` and `subject.id`. Resolvable
    forms are `urn:uuid:<id>`, `Type/<id>`, absolute URLs and `#<id>`. A
    conditional reference (`Type?identifier=system|value`) cannot be
    resolved to an id and yields `subject.identifier` instead.
  - Extensions are named after the last segment of their URL:
    `extension.us-core-race.ombCategory.code`. A Coding or CodeableConcept
    value inside an extension is lifted to the extension path.
  - Any other array keeps its first element at the array path, and the
    complete array as JSON in `<path>.json_all` when it has more than one
    element, so no information is lost.
  - The narrative (`text`) and `meta` of a resource are dropped.
  - Repeating elements that carry their own code and value become CHILD
    TABLES, one row per element (see CHILD_TABLES). An Observation
    holding a blood pressure panel stores its systolic and diastolic
    results as `component` elements: they go to `Observation_component`,
    where each row has the columns of the element (`code.code`,
    `valueQuantity.value`...) and the context it needs, copied from the
    parent under the prefix `parent.` (the parent id, its status, its
    references and its dates). A child row is therefore usable on its own,
    without a join, exactly like a row of the parent table. The parent
    table no longer holds the element. A parent without a value of its own,
    such as a panel, is kept as a row: nothing is dropped silently.
  - Every value is a string and a missing value is an empty string, as in
    the CSV loader.

PostgreSQL limits identifiers to 63 characters, so column names are capped
at MAX_COLUMN_NAME_LENGTH characters. A longer path is shortened
deterministically with a hash, and never silently merged with another one.
The Mapping Agent appends up to 18 characters to the name of a CODED
field it enriches (`_source_concept_id`): a field declared as coded
must therefore keep a path of at most 45 characters. This is a constraint
on declared coded fields, not on the flattening itself.
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Iterable

import pandas as pd

MAX_COLUMN_NAME_LENGTH = 63

_DROPPED_TOP_LEVEL_KEYS = {"resourceType", "meta", "text"}
_EXTENSION_KEYS = ("extension", "modifierExtension")
_CODING_FIELDS = ("system", "version", "code", "display")

# Resource type -> repeating elements extracted into their own child table
# (named "<ResourceType>_<element>"). Only elements that carry their own
# code and value belong here: a plain list of strings does not.
CHILD_TABLES: dict[str, tuple[str, ...]] = {"Observation": ("component",)}

# Columns a child row copies from its parent: the id and the status, the
# references to other resources, and every date (a FHIR date or dateTime
# always starts with YYYY-MM).
_INHERITED_EXACT = {"id", "status"}
_INHERITED_SUFFIXES = (".id", ".reference", ".identifier")
_ISO_DATE = re.compile(
    r"^\d{4}-\d{2}(-\d{2}([Tt ]\d{2}:\d{2}(:\d{2}(\.\d+)?)?(Z|[+-]\d{2}:\d{2})?)?)?$"
)


def normalize_reference(reference: str) -> dict[str, str]:
    """Extracts what can be resolved from a FHIR reference string.

    Returns a dict with `id` (the id of the target resource, when the
    reference points to one) and/or `identifier` (the value of a
    conditional reference, which names a resource by business identifier
    and not by id). Both keys are absent when nothing can be extracted."""
    ref = (reference or "").strip()
    if not ref:
        return {}

    if ref.startswith(("urn:uuid:", "urn:oid:")):
        return {"id": ref.split(":", 2)[2]}

    if "?" in ref:
        query = ref.split("?", 1)[1]
        if "identifier=" in query:
            value = query.split("identifier=", 1)[1].split("&", 1)[0]
            value = value.rsplit("|", 1)[-1]
            return {"identifier": value} if value else {}
        return {}

    if ref.startswith("#"):
        return {"id": ref[1:]} if len(ref) > 1 else {}

    segments = [s for s in ref.split("/") if s]
    if "_history" in segments:
        segments = segments[: segments.index("_history")]
    return {"id": segments[-1]} if segments else {}


def _scalar_to_str(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _short_url(url: str) -> str:
    """Last segment of an extension URL, used as its column name."""
    segment = (url or "").split("#")[-1].rstrip("/").rsplit("/", 1)[-1]
    return segment or "unknown"


def _cap_column_name(name: str) -> str:
    """Shortens a path longer than MAX_COLUMN_NAME_LENGTH, keeping its
    beginning and end readable and adding a hash so two long paths can
    never collapse into the same column."""
    if len(name) <= MAX_COLUMN_NAME_LENGTH:
        return name
    digest = hashlib.md5(name.encode("utf-8")).hexdigest()[:8]
    return f"{name[:22]}~{digest}~{name[-8:]}"


def _pick_coding(codings: list, known_systems: set[str] | None) -> dict | None:
    candidates = [c for c in codings if isinstance(c, dict)]
    if not candidates:
        return None
    if known_systems:
        for coding in candidates:
            if coding.get("system") in known_systems:
                return coding
    return candidates[0]


def flatten_resource(
    resource: dict,
    known_systems: set[str] | None = None,
    exclude_keys: Iterable[str] = (),
) -> dict[str, str]:
    """Flattens one FHIR resource into a single row {column: value}.
    The top-level keys in `exclude_keys` are skipped: they are the elements
    extracted into child tables by extract_child_rows()."""
    row: dict[str, str] = {}
    excluded = set(exclude_keys)

    def put(path: str, value: str) -> None:
        # First occurrence wins: a path produced twice (for example by two
        # extensions with the same short name) keeps its first value, the
        # complete data remaining available in a json_all column.
        row.setdefault(_cap_column_name(path), value)

    def walk_value(value: Any, path: str) -> None:
        if isinstance(value, dict):
            walk_dict(value, path)
        elif isinstance(value, list):
            if not value:
                return
            if len(value) > 1:
                put(f"{path}.json_all", json.dumps(value, ensure_ascii=False, separators=(",", ":")))
            walk_value(value[0], path)
        else:
            put(path, _scalar_to_str(value))

    def walk_dict(data: dict, path: str) -> None:
        for key, value in data.items():
            if not path and (key in _DROPPED_TOP_LEVEL_KEYS or key in excluded):
                continue
            sub = f"{path}.{key}" if path else key

            if key == "coding" and isinstance(value, list):
                put_codings(value, path, sub)
            elif key in _EXTENSION_KEYS and isinstance(value, list):
                put_extensions(value, sub)
            elif key == "reference" and isinstance(value, str) and path:
                put(sub, value)
                resolved = normalize_reference(value)
                if "id" in resolved:
                    put(f"{path}.id", resolved["id"])
                if "identifier" in resolved:
                    put(f"{path}.identifier", resolved["identifier"])
            else:
                walk_value(value, sub)

    def put_codings(codings: list, parent_path: str, array_path: str) -> None:
        chosen = _pick_coding(codings, known_systems)
        if chosen is not None:
            for field in _CODING_FIELDS:
                value = chosen.get(field)
                if value not in (None, ""):
                    put(f"{parent_path}.{field}" if parent_path else field, _scalar_to_str(value))
        if len(codings) > 1:
            put(f"{array_path}.json_all", json.dumps(codings, ensure_ascii=False, separators=(",", ":")))

    def put_extensions(extensions: list, array_path: str) -> None:
        seen: set[str] = set()
        collided = False
        for ext in extensions:
            if not isinstance(ext, dict):
                continue
            prefix = f"{array_path}.{_short_url(ext.get('url', ''))}"
            if prefix in seen:
                collided = True
                continue
            seen.add(prefix)
            for key, value in ext.items():
                if key == "url":
                    continue
                if key in _EXTENSION_KEYS and isinstance(value, list):
                    put_extensions(value, prefix)
                elif key in ("valueCoding", "valueCodeableConcept") and isinstance(value, dict):
                    # A coded value is lifted to the extension path, as for
                    # a CodeableConcept anywhere else in the resource.
                    walk_dict(value, prefix)
                else:
                    walk_value(value, f"{prefix}.{key}")
        if collided:
            put(f"{array_path}.json_all", json.dumps(extensions, ensure_ascii=False, separators=(",", ":")))

    walk_dict(resource, "")
    return row


def _inherited_context(parent_row: dict[str, str]) -> dict[str, str]:
    """Columns of a flattened parent row that its child rows carry along,
    prefixed with `parent.`."""
    inherited: dict[str, str] = {}
    for column, value in parent_row.items():
        if value == "" or column.endswith("json_all"):
            continue
        keep = (
            column in _INHERITED_EXACT
            or column.endswith(_INHERITED_SUFFIXES)
            or bool(_ISO_DATE.match(value))
        )
        if keep:
            inherited[_cap_column_name(f"parent.{column}")] = value
    return inherited


def extract_child_rows(
    resource: dict,
    parent_row: dict[str, str],
    known_systems: set[str] | None = None,
) -> dict[str, list[dict[str, str]]]:
    """Builds the child rows of one resource, grouped by child table name.
    Each row has a synthetic id `<parent id>#<position>`, the flattened
    columns of its element, and the context inherited from the parent."""
    resource_type = resource.get("resourceType", "Unknown")
    context = _inherited_context(parent_row)
    children: dict[str, list[dict[str, str]]] = {}
    for element_name in CHILD_TABLES.get(resource_type, ()):
        elements = resource.get(element_name)
        if not isinstance(elements, list):
            continue
        for position, element in enumerate(elements):
            if not isinstance(element, dict):
                continue
            own = flatten_resource(element, known_systems)
            own.pop("id", None)
            child = {"id": f"{resource.get('id', '')}#{position}", **own, **context}
            children.setdefault(f"{resource_type}_{element_name}", []).append(child)
    return children


def build_fhir_tables(
    sources: Iterable[tuple[str, Iterable[dict]]],
    known_systems: set[str] | None = None,
) -> dict[str, pd.DataFrame]:
    """Builds one wide table per resource type, plus one per child table,
    from (file_name, resources) pairs. Every table starts with `id`, ends
    with `_source_file`, and holds only strings, with an empty string for a
    missing value."""
    rows_by_table: dict[str, list[dict[str, str]]] = {}
    for file_name, resources in sources:
        for resource in resources:
            if not isinstance(resource, dict):
                continue
            resource_type = resource.get("resourceType", "Unknown")
            row = flatten_resource(resource, known_systems, exclude_keys=CHILD_TABLES.get(resource_type, ()))
            row["_source_file"] = file_name
            rows_by_table.setdefault(resource_type, []).append(row)
            for table_name, child_rows in extract_child_rows(resource, row, known_systems).items():
                for child in child_rows:
                    child["_source_file"] = file_name
                rows_by_table.setdefault(table_name, []).extend(child_rows)

    tables: dict[str, pd.DataFrame] = {}
    for table_name, rows in rows_by_table.items():
        columns: list[str] = []
        seen: set[str] = set()
        for row in rows:
            for column in row:
                if column not in seen and column != "_source_file":
                    seen.add(column)
                    columns.append(column)
        if "id" in seen:
            columns.remove("id")
            columns.insert(0, "id")
        columns.append("_source_file")
        tables[table_name] = pd.DataFrame(rows, columns=columns).fillna("").astype(str)
    return tables
