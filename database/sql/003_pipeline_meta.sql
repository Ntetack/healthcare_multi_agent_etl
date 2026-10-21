-- Tracks which source *batches* (one folder per batch, per source) have
-- already been processed, so the Profiling Agent only picks up new
-- folders on each run instead of reprocessing everything.
--
-- Lifecycle: Profiling Agent inserts/updates a row as IN_PROGRESS when it
-- picks a folder to process. Loading Agent marks it SUCCESS once the
-- batch is fully loaded. Root Cause Analyzer / Coordinator mark it
-- FAILED on any unrecovered pipeline failure, making the folder eligible
-- for a retry on the next run.
CREATE SCHEMA IF NOT EXISTS pipeline_meta;

CREATE TABLE IF NOT EXISTS pipeline_meta.processed_folders (
    source_name    TEXT NOT NULL,
    folder_path    TEXT NOT NULL,
    execution_id   TEXT NOT NULL,
    status         TEXT NOT NULL CHECK (status IN ('IN_PROGRESS', 'SUCCESS', 'FAILED')),
    started_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    finished_at    TIMESTAMPTZ,
    PRIMARY KEY (source_name, folder_path)
);
