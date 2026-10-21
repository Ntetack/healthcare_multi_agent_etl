"""
Persistent memory for mapping decisions that would otherwise be
rediscovered identically, from scratch, on every single batch of the
SAME source - starting with local-vocabulary join resolutions (e.g.
MIMIC-III's labevents.ITEMID -> D_LABITEMS join, which never changes
between batches of the same source).

Design principles (see the conversation that led to this module):
  - The pipeline NEVER blocks on human review. Every entry, whether
    `llm_suggested` or `human_confirmed`, is used immediately and
    autonomously - the status is a REVIEW TRACKER, never a gate.
  - A `human_confirmed` entry is never silently overwritten by a later
    LLM call - a person's correction, once made, sticks permanently
    until they change it again themselves.
  - Scoped strictly per source_name - a discovery made for one source
    never leaks into another, consistent with this project's rule of
    never letting one source's knowledge silently generalize to
    another's.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import text

from app.tools.database.db import session_scope

CREATE_TABLE_SQL = """
CREATE SCHEMA IF NOT EXISTS pipeline_meta;

CREATE TABLE IF NOT EXISTS pipeline_meta.mapping_cache (
    source_name TEXT NOT NULL,
    cache_kind TEXT NOT NULL,       -- e.g. 'local_vocab_join' - room for other kinds later
    table_name TEXT NOT NULL,
    field_name TEXT NOT NULL,
    resolution JSONB NOT NULL,      -- the actual cached decision (join_table, resolved_column, ...)
    status TEXT NOT NULL DEFAULT 'llm_suggested',  -- 'llm_suggested' | 'human_confirmed'
    discovered_at TIMESTAMP NOT NULL DEFAULT now(),
    confirmed_at TIMESTAMP,
    confirmed_by TEXT,
    PRIMARY KEY (source_name, cache_kind, table_name, field_name)
);
"""


def ensure_mapping_cache_table() -> None:
    """Idempotent setup - safe to call at the start of every run."""
    with session_scope() as session:
        session.execute(text(CREATE_TABLE_SQL))


def get_cached_resolution(source_name: str, cache_kind: str, table_name: str, field_name: str) -> dict | None:
    """Returns the cached resolution dict if one exists for this exact
    (source, kind, table, field), regardless of its status - both
    llm_suggested and human_confirmed entries are used immediately and
    identically. Returns None if nothing is cached yet, meaning the
    caller should fall through to its own discovery mechanism (e.g. an
    LLM call) and then store the result via store_resolution()."""
    with session_scope() as session:
        row = session.execute(
            text(
                """
                SELECT resolution, status FROM pipeline_meta.mapping_cache
                WHERE source_name = :source_name AND cache_kind = :cache_kind
                  AND table_name = :table_name AND field_name = :field_name
                """
            ),
            {"source_name": source_name, "cache_kind": cache_kind, "table_name": table_name, "field_name": field_name},
        ).mappings().first()
        if row is None:
            return None
        resolution = dict(row["resolution"])
        resolution["_cache_status"] = row["status"]
        return resolution


def store_resolution(
    source_name: str, cache_kind: str, table_name: str, field_name: str, resolution: dict
) -> None:
    """Stores a newly-discovered (LLM) resolution as 'llm_suggested' -
    NEVER overwrites an existing 'human_confirmed' entry, since a
    person's correction must stick permanently until they change it
    themselves. Safe to call every time a fresh discovery happens; the
    human-confirmed guard makes repeated calls harmless."""
    with session_scope() as session:
        existing = session.execute(
            text(
                """
                SELECT status FROM pipeline_meta.mapping_cache
                WHERE source_name = :source_name AND cache_kind = :cache_kind
                  AND table_name = :table_name AND field_name = :field_name
                """
            ),
            {"source_name": source_name, "cache_kind": cache_kind, "table_name": table_name, "field_name": field_name},
        ).mappings().first()
        if existing is not None and existing["status"] == "human_confirmed":
            return  # never overwrite a human's correction

        session.execute(
            text(
                """
                INSERT INTO pipeline_meta.mapping_cache
                    (source_name, cache_kind, table_name, field_name, resolution, status, discovered_at)
                VALUES (:source_name, :cache_kind, :table_name, :field_name, CAST(:resolution AS jsonb), 'llm_suggested', :now)
                ON CONFLICT (source_name, cache_kind, table_name, field_name)
                DO UPDATE SET resolution = EXCLUDED.resolution, discovered_at = EXCLUDED.discovered_at
                """
            ),
            {
                "source_name": source_name, "cache_kind": cache_kind, "table_name": table_name,
                "field_name": field_name, "resolution": _to_jsonb(resolution),
                "now": datetime.now(timezone.utc),
            },
        )


def confirm_resolution(
    source_name: str, cache_kind: str, table_name: str, field_name: str,
    resolution: dict, confirmed_by: str,
) -> None:
    """Human review path - called by scripts/review_mapping_cache.py,
    never by the autonomous pipeline itself. Marks the entry
    'human_confirmed' with the (possibly corrected) resolution, which
    store_resolution() will then always respect and never overwrite."""
    with session_scope() as session:
        session.execute(
            text(
                """
                INSERT INTO pipeline_meta.mapping_cache
                    (source_name, cache_kind, table_name, field_name, resolution, status, discovered_at, confirmed_at, confirmed_by)
                VALUES (:source_name, :cache_kind, :table_name, :field_name, CAST(:resolution AS jsonb), 'human_confirmed', :now, :now, :confirmed_by)
                ON CONFLICT (source_name, cache_kind, table_name, field_name)
                DO UPDATE SET resolution = EXCLUDED.resolution, status = 'human_confirmed',
                              confirmed_at = EXCLUDED.confirmed_at, confirmed_by = EXCLUDED.confirmed_by
                """
            ),
            {
                "source_name": source_name, "cache_kind": cache_kind, "table_name": table_name,
                "field_name": field_name, "resolution": _to_jsonb(resolution),
                "now": datetime.now(timezone.utc), "confirmed_by": confirmed_by,
            },
        )


def list_cache_entries(source_name: str | None = None, status: str | None = None) -> list[dict]:
    """For scripts/review_mapping_cache.py - lists entries, optionally
    filtered by source and/or status (e.g. only 'llm_suggested' ones,
    to prioritize what still needs a human look)."""
    query = "SELECT * FROM pipeline_meta.mapping_cache WHERE 1=1"
    params: dict[str, Any] = {}
    if source_name:
        query += " AND source_name = :source_name"
        params["source_name"] = source_name
    if status:
        query += " AND status = :status"
        params["status"] = status
    query += " ORDER BY source_name, table_name, field_name"

    with session_scope() as session:
        rows = session.execute(text(query), params).mappings().all()
        return [dict(r) for r in rows]


def _to_jsonb(resolution: dict) -> str:
    """Serializes to a JSON string - the SQL statements cast this
    explicitly via CAST(:resolution AS jsonb) rather than the shorthand
    :resolution::jsonb, which SQLAlchemy's text() bind-parameter parser
    misreads (the :: cast operator immediately after a named parameter
    confuses it, producing a literal ":resolution::jsonb" left
    unsubstituted in the final SQL - confirmed in production via a
    psycopg2 syntax error)."""
    import json
    return json.dumps(resolution)
