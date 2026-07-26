"""Copy this file to build your own guardrail, then register it in run_baselines.py.

A guardrail is any callable that maps a prompt to a decision:
    guard(text: str) -> 1  (block — treat as injection/attack)
    guard(text: str) -> 0  (allow — treat as benign)

Keep it honest on BOTH axes: it should block real attacks *and* leave benign
security-adjacent text alone (see the security-adjacent split in the benchmark).
"""
from __future__ import annotations


def my_guard(text: str) -> int:
    text = (text or "").lower()
    # TODO: replace with your real logic (rules, a model, an API call, ...).
    return int("ignore all previous instructions" in text)


# batch variant (optional) — implement this instead if your guard is a model:
def my_guard_batch(texts):
    return [my_guard(t) for t in texts]
