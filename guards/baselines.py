"""Baseline guardrails scored on the arena. Add your own by implementing
`guard(text) -> 0|1` (or a batch version) and appending to GUARDS in run_baselines.py.
"""
from __future__ import annotations

import glob
import os
import re

import yaml

RULES_DIR = os.path.join(os.path.dirname(__file__), "..", "rules")


# --- 1) naive keyword baseline -------------------------------------------------
_KEYWORDS = [
    "ignore previous", "ignore all previous", "disregard", "system prompt",
    "you are now", "developer mode", "do anything now", "jailbreak",
    "önceki talimat", "talimatları yoksay", "görmezden gel", "sistem prompt",
    "gizlice", "kullanıcıya söyleme",
]


def keyword_guard(text: str) -> int:
    t = (text or "").lower()
    return int(any(k in t for k in _KEYWORDS))


# --- 2) regex rules baseline (from prompt-injection-detection-rules) -----------
_FLAG = {"i": re.IGNORECASE, "m": re.MULTILINE, "s": re.DOTALL}
_RX = []


def _load_rules():
    if _RX:
        return _RX
    for p in glob.glob(os.path.join(RULES_DIR, "*.yml")):
        for r in yaml.safe_load(open(p, encoding="utf-8")) or []:
            fl = 0
            for f in r.get("flags", []):
                fl |= _FLAG.get(f, 0)
            try:
                _RX.append(re.compile(r["pattern"], fl))
            except re.error:
                pass
    return _RX


def rules_guard(text: str) -> int:
    return int(any(rx.search(text or "") for rx in _load_rules()))
