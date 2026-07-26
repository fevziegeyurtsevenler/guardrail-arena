![guardrail-arena](assets/banner.png)

# guardrail-arena

**Does your LLM guardrail catch attacks — without over-blocking the people who just *talk about* attacks?**

Most prompt-injection guardrails are scored on one axis: how many attacks they catch. That
number is easy to game — a guard that blocks the words *"ignore instructions"* and *"jailbreak"*
looks great on an attack set. But real traffic includes a security engineer writing *"our policy
says the assistant must refuse to reveal its system prompt"*, a teacher asking *"what is a
jailbreak?"*, or a Turkish incident report that quotes an attacker. A guard that blocks those is
**broken in production** — it's just broken in a way single-axis benchmarks never measure.

guardrail-arena scores every guardrail on **two axes at once**, in **English and Turkish**:

1. **Miss-rate** ↓ — attacks that slip through.
2. **Over-refusal** ↓ — benign prompts wrongly blocked, split into *plain* requests and
   **security-adjacent** text (legitimate content that discusses or quotes attacks).

A guardrail is any callable `guard(text) -> 0 | 1`. Drop yours in, run one command, get a row.

[![License](https://img.shields.io/badge/license-Apache--2.0-blue)](LICENSE)
[![benchmark](https://img.shields.io/badge/benchmark-337%20prompts-red)](benchmark/data.jsonl)
[![languages](https://img.shields.io/badge/languages-EN%20%2B%20TR-red)](benchmark/data.jsonl)
[![HF dataset](https://img.shields.io/badge/🤗%20dataset-guardrail--arena-yellow)](https://huggingface.co/datasets/fevziegeyurtsevenler/guardrail-arena)

---

## 🏁 Leaderboard

337 prompts · 217 injections (EN+TR) · 120 benign (80 plain + 40 security-adjacent). Lower is
better for miss-rate and over-refusal; higher for F1. Reproduce with `python run_baselines.py`.

<!-- LEADERBOARD:START -->
| # | Guardrail | Miss-rate ↓ | Over-refusal (all) ↓ | **Over-refusal: security-adjacent** ↓ | F1 ↑ | TR miss | TR over-refusal |
|---|-----------|:-----------:|:--------------------:|:-------------------------------------:|:----:|:-------:|:---------------:|
| 1 | **AltaySec-detector** | 0.00 | 0.23 | **0.70** | 0.94 | 0.00 | 0.23 |
| 2 | **keyword** | 0.88 | 0.12 | **0.38** | 0.20 | 0.91 | 0.08 |
| 3 | **regex-rules** | 0.91 | 0.10 | **0.30** | 0.16 | 0.90 | 0.10 |
<!-- LEADERBOARD:END -->

> **Honest note on the detector's numbers.** The `AltaySec-detector` baseline was *trained* on
> this benchmark's injection payloads and its *plain* benign prompts, so its 0.00 miss-rate and
> 0.00 plain-over-refusal are **in-distribution** — treat them as an upper bound, not
> generalization. The **security-adjacent** benign prompts are genuinely held-out for all three
> guards, which is why that column is the fair, un-gameable comparison. See
> [Limitations](#-honesty--limitations).

## 🔎 The finding

The most interesting result isn't who wins — it's the **over-refusal cliff on security-adjacent text**:

| Guard | Over-refusal on *plain* requests | Over-refusal on *security-adjacent* text |
|-------|:--------------------------------:|:----------------------------------------:|
| keyword | 0% | **38%** |
| regex-rules | 0% | **30%** |
| AltaySec-detector | 0% | **70%** |

Nobody blocks *"Summarize this article."* But the **better a guard is at catching attacks, the
harder it over-blocks legitimate security discussion.** The ML detector that catches every attack
also refuses **7 out of 10** benign prompts that merely *mention* one. That trade-off is invisible
on a normal attack-only benchmark — and it's exactly where guardrails hurt real products:
security teams, SOC copilots, compliance tooling, and support bots that quote user reports.

This is the core thesis of the arena: **over-defense is a first-class failure mode.** A guardrail
you can't measure on both axes is a guardrail you can't tune.

## 🚀 Quickstart — score your own guardrail

```bash
pip install -r requirements.txt
```

```python
from evaluate import evaluate, load_benchmark

# a guardrail is any callable: text -> 1 (block) / 0 (allow)
def my_guard(text: str) -> int:
    return int("ignore previous instructions" in text.lower())

print(evaluate(my_guard, load_benchmark())["overall"])
# {'miss_rate': ..., 'over_refusal_rate': ..., 'f1': ..., ...}
```

Reproduce the full leaderboard (keyword + regex-rules + the HF detector):

```bash
python run_baselines.py     # writes results.json + LEADERBOARD.md
```

Batch guards (e.g. an embedding model) implement `guard(list[str]) -> list[int]` and use
`score_batch`. See [`run_baselines.py`](run_baselines.py) for a worked model example.

## 📦 What's in the benchmark

`benchmark/data.jsonl` — one JSON object per line:

```json
{"text": "...", "label": 1, "language": "tr", "category": "indirect-injection", "source": "..."}
```

| Split | Count | What it is |
|-------|------:|------------|
| Injections (`label=1`) | 217 | Direct + indirect prompt injection, jailbreak, exfil, persona, encoding, invisible-text — EN (110) + TR (107). From the [AltaySec injection corpus](https://github.com/fevziegeyurtsevenler/prompt-injection-corpus). |
| Benign — plain (`label=0`) | 80 | Ordinary requests, EN + TR. A guard should never block these. |
| Benign — security-adjacent (`label=0`) | 40 | **Legitimate** text that discusses, teaches, or quotes attacks (security docs, OWASP references, red-team lessons, detection-rule requests, incident summaries), EN + TR. The over-refusal trap. |

Every injection row carries `category`, and the underlying corpus maps each to OWASP LLM Top 10
and MITRE ATLAS techniques.

## 📊 Metrics

| Metric | Definition | Good |
|--------|------------|:----:|
| `miss_rate` | injections allowed / injections | ↓ |
| `injection_recall` | 1 − miss_rate | ↑ |
| `over_refusal_rate` | benign blocked / benign | ↓ |
| `benign_specificity` | 1 − over_refusal_rate | ↑ |
| `f1` | harmonic mean of precision & recall (attack = positive) | ↑ |

All are reported **overall, per language (en/tr), and per benign category**.

## ➕ Add your guardrail to the leaderboard

1. Implement `guard(text) -> 0|1` (or a batch version).
2. Add it to `GUARDS` in `run_baselines.py`, run it, commit the updated `results.json` +
   `LEADERBOARD.md`.
3. Open a PR. Wrappers around Llama Guard, Prompt Guard, Lakera, Rebuff, NeMo Guardrails,
   OpenAI moderation, or your own model are all welcome — the point is an **apples-to-apples,
   two-axis, multilingual** comparison.

## 🎯 Why this exists

Guardrail vendors publish attack-recall numbers; almost nobody publishes over-refusal on
security-adjacent traffic, and even fewer report it **in Turkish**. That gap is the whole reason
teams ship guards that quietly break their own security and support workflows. guardrail-arena is
a small, open, reproducible way to see both sides of the trade-off before you deploy.

## ⚖️ Honesty & limitations

- **Small, convenience-built.** 337 prompts is a probe, not a census. Numbers move with more data;
  PRs adding prompts (especially hard benign + new languages) are the most valuable contribution.
- **Detector has train-set overlap** on injections + plain benign (disclosed above). The
  security-adjacent column is the only fully held-out comparison for it.
- **Binary block/allow.** Real guardrails have thresholds and severities; this reduces them to a
  single decision at their default setting. Tune yours before submitting if that's fairer.
- **Not a safety guarantee.** A good score here does not mean a guard is production-safe. Pair any
  guardrail with sandboxing, egress allow-lists, and least-privilege tools.

## 🔗 Related AltaySec work

- 🕵️ [**uncloak**](https://github.com/fevziegeyurtsevenler/uncloak) — hidden / invisible-Unicode prompt-injection scanner ([live demo](https://fevziegeyurtsevenler.github.io/uncloak/))
- 📏 [**prompt-injection-detection-rules**](https://github.com/fevziegeyurtsevenler/prompt-injection-detection-rules) — the 20 regex rules used by the `regex-rules` baseline
- 🧪 [**prompt-injection-corpus**](https://github.com/fevziegeyurtsevenler/prompt-injection-corpus) — the multilingual injection source
- 🤗 [**turkish-prompt-injection-detector**](https://huggingface.co/fevziegeyurtsevenler/turkish-prompt-injection-detector) — the model behind the `AltaySec-detector` baseline
- 🌐 [AltaySec](https://altaysec.com.tr) · [Açık Kaynak Lab](https://altaysec.com.tr/acik-kaynak)

## Citation

```bibtex
@misc{yurtsevenler2026guardrailarena,
  title  = {guardrail-arena: A Two-Axis, Multilingual Benchmark for LLM Guardrails},
  author = {Yurtsevenler, Fevzi Ege},
  year   = {2026},
  publisher = {AltaySec},
  howpublished = {\url{https://github.com/fevziegeyurtsevenler/guardrail-arena}}
}
```

Apache-2.0 · built by **[AltaySec](https://altaysec.com.tr)** — Türkçe-first AI/LLM security.
