import csv
import importlib.util
from pathlib import Path

p = Path(__file__).resolve().parents[2] / "scripts" / "mapping_metrics.py"
spec = importlib.util.spec_from_file_location("mapping_metrics", p)
mm = importlib.util.module_from_spec(spec); spec.loader.exec_module(mm)

GOLD = ("omop_table,omop_field,expected_source_table,expected_source_field,status,notes\n"
        "person,gender_source_value,patients,GENDER,MAP,\n"
        "person,year_of_birth,patients,BIRTHDATE,MAP,\n"
        "visit_occurrence,visit_start_date,encounters,START,MAP,\n"
        "visit_occurrence,visit_end_date,encounters,STOP,MAP,\n")
AGENT = ("section,status,target_table,target_field,source_table,source_field,confidence,reason\n"
         "structural_field,OK,person,gender_source_value,patients,GENDER,1,\n"
         "structural_field,OK,person,year_of_birth,patients,BIRTHDATE,1,\n"
         "structural_field,OK,visit_occurrence,visit_start_date,encounters,START,1,\n"
         "structural_field,OK,visit_occurrence,visit_start_date,procedures,DATE,1,\n")


def _files(tmp_path):
    g, a = tmp_path / "gold.csv", tmp_path / "report.csv"
    g.write_text(GOLD); a.write_text(AGENT)
    return g, a


def test_score_counts_pairs_the_way_the_methodology_defines_them(tmp_path):
    g, a = _files(tmp_path)
    s = mm.score(g, a)
    # M_B1 = 4 pairs, M_GT = 4 pairs, 3 in common
    assert (s["tp"], s["fp"], s["fn"]) == (3, 1, 1)
    assert s["precision"] == 0.75 and s["recall"] == 0.75 and abs(s["f1"] - 0.75) < 1e-12


def test_append_rows_replaces_a_rerun_and_keeps_other_metrics(tmp_path):
    out = tmp_path / "runs.csv"
    out.write_text("scenario,metric,unit,run,batch,value\nS1,field_agreement,person,1,,0.996000\n")
    mm.append_rows(out, "S1", 1, {"precision": 0.5, "recall": 0.6, "f1": 0.55})
    mm.append_rows(out, "S1", 1, {"precision": 0.7, "recall": 0.8, "f1": 0.75})
    rows = list(csv.DictReader(out.open()))
    assert [r["metric"] for r in rows] == ["field_agreement", "precision", "recall", "f1"]
    assert rows[3]["value"] == "0.750000"


def test_backfill_reads_one_report_per_run_and_feeds_the_aggregation(tmp_path):
    g, a = _files(tmp_path)
    for r in (1, 2, 3):
        d = tmp_path / "runs" / f"S1-run{r}-b1" / "mapping"; d.mkdir(parents=True)
        (d / "report.csv").write_text(AGENT)
    out = tmp_path / "runs.csv"
    assert mm.main(["--gold", str(g), "--scenario", "S1", "--backfill", "3", "--runs-csv", str(out),
                    "--agent-template", str(tmp_path / "runs" / "S1-run{run}-b1" / "mapping" / "report.csv")]) == 0
    agg_spec = importlib.util.spec_from_file_location("agg", Path(__file__).resolve().parents[2] / "scripts" / "aggregate_runs.py")
    agg = importlib.util.module_from_spec(agg_spec); agg_spec.loader.exec_module(agg)
    res = agg.analyse(agg.read_runs(str(out)))
    assert res["H1"]["S1"]["n"] == 3 and res["H1"]["S1"]["mean"] == 0.75
