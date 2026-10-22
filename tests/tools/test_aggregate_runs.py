import importlib.util
import pathlib

import numpy as np
from scipy import stats

p = pathlib.Path(__file__).resolve().parents[2] / "scripts" / "aggregate_runs.py"
spec = importlib.util.spec_from_file_location("aggregate_runs", p)
ar = importlib.util.module_from_spec(spec); spec.loader.exec_module(ar)


def test_one_sided_matches_scipy_and_rejects_clear_effect():
    v = [0.86, 0.88, 0.85, 0.87, 0.89]
    r = ar.one_sided_greater(v, 0.80, 0.05)
    t, pv = stats.ttest_1samp(v, 0.80, alternative="greater")
    assert abs(r["t"] - t) < 1e-12 and abs(r["p"] - pv) < 1e-12 and r["reject"] is True
    assert abs(r["dz"] - (np.mean(v) - 0.80) / np.std(v, ddof=1)) < 1e-12


def test_one_sided_does_not_reject_below_threshold():
    r = ar.one_sided_greater([0.70, 0.72, 0.69, 0.71, 0.70], 0.80, 0.05)
    assert r["reject"] is False


def test_zero_variance_compares_directly():
    assert ar.one_sided_greater([0.9] * 5, 0.8, 0.05)["reject"] is True
    assert ar.one_sided_greater([0.7] * 5, 0.8, 0.05)["reject"] is False
    assert ar.one_sided_greater([0.9] * 5, 0.8, 0.05)["p"] is None


def test_tost_equivalent_and_not():
    assert ar.tost([0.001, -0.002, 0.0, 0.002, -0.001], 0.05, 0.05)["equivalent"] is True
    assert ar.tost([0.10, 0.12, 0.09, 0.11, 0.10], 0.05, 0.05)["equivalent"] is False


def test_tost_p_is_max_of_two_one_sided():
    d = [0.01, 0.03, -0.01, 0.02, 0.0]
    r = ar.tost(d, 0.05, 0.05)
    lo = stats.ttest_1samp(d, -0.05, alternative="greater").pvalue
    up = stats.ttest_1samp(d, 0.05, alternative="less").pvalue
    assert abs(r["p"] - max(lo, up)) < 1e-12


def test_tost_zero_variance_and_n1():
    assert ar.tost([0.01] * 5, 0.05, 0.05)["equivalent"] is True
    assert ar.tost([0.06] * 5, 0.05, 0.05)["equivalent"] is False
    assert ar.tost([0.01], 0.05, 0.05)["equivalent"] is None


def test_end_to_end(tmp_path):
    rng = np.random.default_rng(0)
    lines = ["scenario,metric,unit,run,batch,value"]
    for run in range(1, 6):
        lines.append(f"S1,f1,,{run},,{0.88 + rng.normal(0, 0.01):.4f}")
        lines.append(f"S3,f1,,{run},,{0.70 + rng.normal(0, 0.01):.4f}")
        lines.append(f"S1,field_agreement,person,{run},,{0.97 + rng.normal(0, 0.005):.4f}")
        lines.append(f"S1,field_agreement,drug_exposure,{run},,{0.60 + rng.normal(0, 0.02):.4f}")
        b1 = 0.85 + rng.normal(0, 0.01)
        lines.append(f"S4,f1,,{run},1,{b1:.4f}")
        lines.append(f"S4,f1,,{run},2,{b1 + rng.normal(0, 0.005):.4f}")
    f = tmp_path / "runs.csv"; f.write_text("\n".join(lines))
    res = ar.analyse(ar.read_runs(str(f)))
    assert res["H1"]["S1"]["reject"] is True and res["H1"]["S3"]["reject"] is False
    assert res["H2"][("S1", "person")]["reject"] is True and res["H2"][("S1", "drug_exposure")]["reject"] is False
    assert res["H3"]["f1"]["equivalent"] is True
    text = ar.render(res, 0.05)
    assert "H3" in text and "S4" in text
    out = tmp_path / "r.md"
    assert ar.main([str(f), "--out", str(out)]) == 0 and out.exists()


def test_tiny_p_values_are_not_written_as_zero():
    assert ar._p(1e-9) == "<0.0001" and ar._p(0.0243) == "0.0243" and ar._p(None) == "n/a"
