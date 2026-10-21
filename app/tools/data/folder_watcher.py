"""
New-data detection. Each source lands its batches in a fresh subfolder
under the source's root path (e.g. data/raw/hospital_a/2026-08-19_batch1/)
rather than adding files into an existing folder. Detection is therefore
just: list subfolders, compare against pipeline_meta.processed_folders.

Pure/deterministic where possible; the two DB-writing functions
(mark_in_progress / mark_status) are simple, intentionally dumb - no
business logic, just state transitions the agents call explicitly.
"""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import text

from app.tools.database.db import session_scope


def list_batch_folders(source_root_path: str | Path) -> list[Path]:
    """All immediate subfolders under the source root, sorted so the
    oldest batch (by folder name, which should be date-prefixed) is
    processed first."""
    root = Path(source_root_path)
    if not root.exists():
        return []
    return sorted(p for p in root.iterdir() if p.is_dir())


def get_processed_folders(source_name: str, exclude_status: tuple[str, ...] = ("SUCCESS",)) -> set[str]:
    """Folder paths already processed for this source, i.e. not eligible
    for reprocessing. FAILED folders are NOT excluded by default, so they
    remain eligible for a retry; IN_PROGRESS ones are excluded to avoid a
    concurrent run picking the same folder (see sequential-execution
    assumption documented in README.md)."""
    with session_scope() as session:
        rows = session.execute(
            text(
                """
                SELECT folder_path FROM pipeline_meta.processed_folders
                WHERE source_name = :source_name
                  AND status = ANY(:statuses)
                """
            ),
            {"source_name": source_name, "statuses": list(exclude_status) + ["IN_PROGRESS"]},
        ).scalars().all()
    return set(rows)


def find_next_folder(source_name: str, source_root_path: str | Path) -> Path | None:
    """Returns the next batch folder to process for this source, or None
    if there's nothing new."""
    all_folders = list_batch_folders(source_root_path)
    already_done = get_processed_folders(source_name)
    for folder in all_folders:
        if str(folder) not in already_done:
            return folder
    return None


def mark_in_progress(source_name: str, folder_path: str | Path, execution_id: str) -> None:
    with session_scope() as session:
        session.execute(
            text(
                """
                INSERT INTO pipeline_meta.processed_folders
                    (source_name, folder_path, execution_id, status, started_at)
                VALUES (:source_name, :folder_path, :execution_id, 'IN_PROGRESS', now())
                ON CONFLICT (source_name, folder_path)
                DO UPDATE SET execution_id = :execution_id, status = 'IN_PROGRESS',
                               started_at = now(), finished_at = NULL
                """
            ),
            {"source_name": source_name, "folder_path": str(folder_path), "execution_id": execution_id},
        )


def mark_status(source_name: str, folder_path: str | Path, status: str) -> None:
    """status: 'SUCCESS' or 'FAILED'. Called by the Loading Agent (SUCCESS)
    or the Root Cause Analyzer / Coordinator (FAILED) - never by the
    Profiling Agent itself, which only knows the run has started, not
    whether it will ultimately succeed."""
    if status not in ("SUCCESS", "FAILED"):
        raise ValueError("status must be 'SUCCESS' or 'FAILED'")
    with session_scope() as session:
        session.execute(
            text(
                """
                UPDATE pipeline_meta.processed_folders
                SET status = :status, finished_at = now()
                WHERE source_name = :source_name AND folder_path = :folder_path
                """
            ),
            {"status": status, "source_name": source_name, "folder_path": str(folder_path)},
        )
