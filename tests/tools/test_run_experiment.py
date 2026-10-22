import importlib.util
from pathlib import Path

p = Path(__file__).resolve().parents[2] / "scripts" / "run_experiment.py"
spec = importlib.util.spec_from_file_location("run_experiment", p)
re_ = importlib.util.module_from_spec(spec); spec.loader.exec_module(re_)


class Fake:
    """A source with n batches; a batch disappears from the queue once its pipeline succeeds."""
    def __init__(self, n, fail_on=None):
        self.queue = [Path(f"/data/b{i}") for i in range(1, n + 1)]
        self.n, self.fail_on, self.calls, self.compares, self.scored = n, fail_on, [], [], []

    def reset(self, source, dry):
        self.calls.append("reset"); self.queue = [Path(f"/data/b{i}") for i in range(1, self.n + 1)]

    def next_folder(self, source):
        return self.queue[0] if self.queue else None

    def run_pipeline(self, source, eid):
        self.calls.append(eid)
        if eid == self.fail_on:
            return 1
        self.queue.pop(0); return 0

    def collect_dqd(self, eid, dest): return None
    def mapping_scores(self, gold, eid, scenario, run, batch, csv): self.scored.append((eid, batch))
    def append_metrics(self, path, row): self.calls.append(("metrics", row["batch"]))

    def compare(self, schema, scenario, run, batch, csv, report, extra):
        self.compares.append((schema, scenario, run, batch)); return 0


def hooks_for(fake):
    class H: pass
    for k in ("reset", "next_folder", "run_pipeline", "collect_dqd", "compare", "append_metrics", "mapping_scores"):
        setattr(H, k, staticmethod(getattr(fake, k)))
    return H


def run(fake, *args):
    return re_.main(["--source", "s", "--out", "/nonexistent", *args], hooks=hooks_for(fake))


def test_single_mode_processes_one_batch_then_stops():
    f = Fake(3)
    assert run(f, "--scenario", "S1", "--runs", "1", "--mode", "single") == 0
    assert [c for c in f.calls if isinstance(c, str) and c.startswith("S1")] == ["S1-run1-b1"]
    assert f.compares == [("omop_temp", "S1", 1, "")]


def test_all_mode_processes_every_batch_and_compares_on_the_cumulative_schema():
    f = Fake(3)
    assert run(f, "--scenario", "S1", "--runs", "1", "--mode", "all") == 0
    assert [c for c in f.calls if isinstance(c, str) and c.startswith("S1")] == ["S1-run1-b1", "S1-run1-b2", "S1-run1-b3"]
    assert f.compares == [("omop", "S1", 1, "")]


def test_s4_compares_after_each_batch():
    f = Fake(2)
    assert run(f, "--scenario", "S4", "--runs", "1", "--mode", "all") == 0
    assert f.compares == [("omop_temp", "S4", 1, "1"), ("omop_temp", "S4", 1, "2")]


def test_every_run_starts_with_a_reset_and_runs_are_numbered():
    f = Fake(1)
    run(f, "--scenario", "S2", "--runs", "3", "--first-run", "4")
    assert f.calls.count("reset") == 3
    assert [c for c in f.calls if isinstance(c, str) and c.startswith("S2")] == ["S2-run4-b1", "S2-run5-b1", "S2-run6-b1"]


def test_a_failed_pipeline_ends_the_run_without_comparison_and_returns_nonzero():
    f = Fake(2, fail_on="S1-run1-b1")
    assert run(f, "--scenario", "S1", "--runs", "1", "--mode", "all") == 1
    assert f.compares == []


def test_a_batch_that_stays_eligible_does_not_loop_forever():
    f = Fake(1)
    f.run_pipeline = lambda s, e: (f.calls.append(e) or 0)       # success code but the batch is never marked done
    assert run(f, "--scenario", "S1", "--runs", "1", "--mode", "all") == 1
    assert len([c for c in f.calls if isinstance(c, str) and c.startswith("S1")]) == 1


def test_reset_only_does_not_run_anything():
    f = Fake(1)
    assert run(f, "--scenario", "S1", "--reset-only") == 0
    assert f.calls == ["reset"]


def test_arguments_after_double_dash_reach_the_comparison():
    f = Fake(1); seen = []
    f.compare = lambda *a: seen.append(a[-1]) or 0
    re_.main(["--source", "s", "--scenario", "S1", "--runs", "1", "--out", "/x", "--", "--patients-csv", "p.csv"], hooks=hooks_for(f))
    assert seen == [["--patients-csv", "p.csv"]]


def test_collect_dqd_takes_the_dashboard_output_not_the_agent_summary(tmp_path, monkeypatch):
    import json
    monkeypatch.setattr(re_, "ROOT", tmp_path)
    folder = tmp_path / "runs" / "X" / "validation"; folder.mkdir(parents=True)
    (folder / "result.json").write_text(json.dumps({"agent_name": "validation_agent", "output": {}}))
    (folder / "a-dqd.json").write_text(json.dumps({"CheckResults": [{"passed": 1}]}))
    dest = tmp_path / "out" / "dqd.json"
    assert re_.collect_dqd("X", dest) == dest and "CheckResults" in dest.read_text()
    (folder / "a-dqd.json").unlink()
    assert re_.collect_dqd("X", tmp_path / "out" / "none.json") is None


def test_gold_adds_the_mapping_scores_of_each_batch():
    f = Fake(2)
    run(f, "--scenario", "S4", "--runs", "1", "--mode", "all", "--gold", "g.csv")
    assert f.scored == [("S4-run1-b1", "1"), ("S4-run1-b2", "2")]
    f2 = Fake(1)
    run(f2, "--scenario", "S1", "--runs", "1", "--gold", "g.csv")
    assert f2.scored == [("S1-run1-b1", "")]
    f3 = Fake(1)
    run(f3, "--scenario", "S1", "--runs", "1")
    assert f3.scored == []
