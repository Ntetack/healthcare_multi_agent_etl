"""list_batch_folders() is pure/filesystem-only and can be tested without
a DB; the DB-backed functions (get_processed_folders, mark_*) require
Postgres and are covered at integration level."""
from app.tools.data.folder_watcher import list_batch_folders


def test_list_batch_folders_sorted(tmp_path):
    (tmp_path / "2026-08-19_batch1").mkdir()
    (tmp_path / "2026-08-01_batch0").mkdir()
    (tmp_path / "not_a_dir.csv").write_text("x")

    folders = list_batch_folders(tmp_path)
    names = [f.name for f in folders]
    assert names == ["2026-08-01_batch0", "2026-08-19_batch1"]


def test_list_batch_folders_missing_root(tmp_path):
    assert list_batch_folders(tmp_path / "does_not_exist") == []
