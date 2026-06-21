"""Shared IO for v3 analysis scripts.

The one subtlety: the `id` field in predictions is NOT unique (one id string
maps to several distinct image pairs). The correct per-item key is the dataset
row index. New runs store it as `item` (run_eval.py). Older exp1 predictions
lack it, so we reconstruct item identity from FILE ORDER: run_eval writes an
item's languages contiguously and each language appears at most once per item,
so a repeated language marks the start of a new item.
"""
import json
from pathlib import Path


def load_rows(paths):
    """Load prediction jsonl file(s); tag each row with its model key."""
    rows = []
    for p in paths:
        p = Path(p)
        if p.stem.startswith("predictions_"):
            model_key = p.stem[len("predictions_"):]
        else:
            model_key = "qwen7b"  # legacy single-model exp1 file
        for line in p.read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                r.setdefault("model", model_key)
                rows.append(r)
    return ensure_item_ids(rows)


def ensure_item_ids(rows):
    """Guarantee every row has a unique-per-item `item` key.

    If `item` is already present (new runs), keep it. Otherwise reconstruct it
    per model from append order: a repeated language => a new item.
    """
    if all("item" in r for r in rows):
        return rows
    # reconstruct per model, preserving the given (file) order
    from collections import defaultdict
    counters = defaultdict(lambda: [0, set()])  # model -> [idx, seen langs]
    for r in rows:
        if "item" in r:
            continue
        st = counters[r["model"]]
        if r["lang"] in st[1]:
            st[0] += 1
            st[1] = set()
        st[1].add(r["lang"])
        r["item"] = f"{r['model']}#{st[0]}"
    return rows
