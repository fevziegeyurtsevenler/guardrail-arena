"""Run the baseline guardrails on the benchmark and write results.json + LEADERBOARD.md.

Baselines:
  - keyword     : naive substring matching
  - regex-rules : prompt-injection-detection-rules (20 open regex rules)
  - AltaySec detector : the multilingual sentence-transformer + LR model (optional;
                        needs `pip install sentence-transformers scikit-learn`)
"""
from __future__ import annotations

import json
import os

from evaluate import load_benchmark, evaluate, score_batch
from guards.baselines import keyword_guard, rules_guard

HERE = os.path.dirname(__file__)
rows = load_benchmark()
results = {}

results["keyword"] = evaluate(keyword_guard, rows)
results["regex-rules"] = evaluate(rules_guard, rows)

# Optional model baseline
try:
    import joblib
    from huggingface_hub import hf_hub_download
    from sentence_transformers import SentenceTransformer

    enc = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    clf = joblib.load(hf_hub_download("fevziegeyurtsevenler/turkish-prompt-injection-detector", "model.joblib"))

    def model_batch(texts):
        emb = enc.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        return (clf.predict_proba(emb)[:, 1] >= 0.5).astype(int).tolist()

    results["AltaySec-detector"] = score_batch(model_batch, rows)
except Exception as e:  # noqa: BLE001
    print("model baseline skipped:", str(e)[:100])

json.dump(results, open(os.path.join(HERE, "results.json"), "w"), indent=2, ensure_ascii=False)

# leaderboard markdown — ranked by F1; surfaces the security-adjacent over-refusal (the honest,
# held-out axis) separately from plain over-refusal.
order = sorted(results, key=lambda g: -results[g]["overall"]["f1"])
lines = [
    "| # | Guardrail | Miss-rate ↓ | Over-refusal (all) ↓ | **Over-refusal: security-adjacent** ↓ | F1 ↑ | TR miss | TR over-refusal |",
    "|---|-----------|:-----------:|:--------------------:|:-------------------------------------:|:----:|:-------:|:---------------:|",
]
for i, g in enumerate(order, 1):
    o = results[g]["overall"]
    tr = results[g]["by_language"].get("tr", {})
    bc = results[g]["over_refusal_by_benign_category"]
    sa = bc.get("benign-security-adjacent", 0.0)
    lines.append(f"| {i} | **{g}** | {o['miss_rate']:.2f} | {o['over_refusal_rate']:.2f} | "
                 f"**{sa:.2f}** | {o['f1']:.2f} | {tr.get('miss_rate','—')} | {tr.get('over_refusal_rate','—')} |")
open(os.path.join(HERE, "LEADERBOARD.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
print("\n".join(lines))
print("\nwrote results.json + LEADERBOARD.md")
