"""Smoke tests for the benchmark and scoring harness."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from evaluate import load_benchmark, evaluate, score_batch


def test_benchmark_wellformed():
    rows = load_benchmark()
    assert len(rows) > 300
    langs, labels, cats = set(), set(), set()
    for r in rows:
        assert set(("text", "label", "language", "category")) <= set(r)
        assert r["label"] in (0, 1)
        assert r["text"].strip()
        langs.add(r["language"]); labels.add(r["label"]); cats.add(r["category"])
    assert {"en", "tr"} <= langs
    assert labels == {0, 1}
    assert "benign-security-adjacent" in cats  # the over-refusal trap must exist


def test_perfect_and_null_guards():
    rows = load_benchmark()
    # oracle guard = ground truth -> zero miss, zero over-refusal, F1 = 1
    oracle = evaluate(lambda t: 1, rows)  # blocks everything
    assert oracle["overall"]["miss_rate"] == 0.0
    assert oracle["overall"]["over_refusal_rate"] == 1.0
    allow_all = evaluate(lambda t: 0, rows)  # blocks nothing
    assert allow_all["overall"]["miss_rate"] == 1.0
    assert allow_all["overall"]["over_refusal_rate"] == 0.0


def test_metrics_shape():
    rows = load_benchmark()
    out = evaluate(lambda t: int("ignore" in t.lower()), rows)
    assert {"overall", "by_language", "over_refusal_by_benign_category"} <= set(out)
    assert {"en", "tr"} <= set(out["by_language"])
    assert "benign-security-adjacent" in out["over_refusal_by_benign_category"]


def test_batch_matches_single():
    rows = load_benchmark()
    g = lambda t: int("jailbreak" in t.lower())
    a = evaluate(g, rows)["overall"]
    b = score_batch(lambda ts: [g(t) for t in ts], rows)["overall"]
    assert a == b
