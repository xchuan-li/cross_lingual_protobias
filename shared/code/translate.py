"""Translate the neutral `text` prompt of each sampled row into all active
languages, and cache the result to results/translations.json.

The cache is plain JSON keyed by row id, so you can HUMAN-REVIEW translations
(open the file and eyeball them) -- this directly answers the "how did you
ensure translation quality?" question in QA.

Backend: deep-translator (Google). English is kept as-is (data is English).
Run:  python translate.py
"""
import json

import config
from data_utils import sample_rows


def get_translator():
    try:
        from deep_translator import GoogleTranslator
    except ImportError:
        raise SystemExit(
            "Install the translator first:  pip install deep-translator"
        )
    return GoogleTranslator


def main():
    rows = sample_rows()
    cache = {}
    if config.TRANSLATIONS_PATH.exists():
        cache = json.loads(config.TRANSLATIONS_PATH.read_text())

    GoogleTranslator = get_translator()
    n_new = 0
    for r in rows:
        rid = r["id"]
        entry = cache.setdefault(rid, {"source": r["text"]})
        for lang in config.ACTIVE_LANGUAGES:
            if lang in entry:
                continue
            if lang == "en":
                entry[lang] = r["text"]
            else:
                tgt = config.LANGUAGES[lang]["code"]
                entry[lang] = GoogleTranslator(source="en", target=tgt).translate(r["text"])
                n_new += 1
    config.TRANSLATIONS_PATH.write_text(
        json.dumps(cache, ensure_ascii=False, indent=2)
    )
    print(f"Translated {n_new} new (row x lang) entries.")
    print(f"Cache: {config.TRANSLATIONS_PATH}  ({len(cache)} rows)")
    # show a couple for sanity
    for rid in list(cache)[:2]:
        print("\n", rid, json.dumps(cache[rid], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
