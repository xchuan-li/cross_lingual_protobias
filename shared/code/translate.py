"""Translate the neutral `text` prompt of each sampled row into all active
languages, and cache the result to results/translations.json.

The cache is plain JSON keyed by row id, so you can HUMAN-REVIEW translations
(open the file and eyeball them) -- this directly answers the "how did you
ensure translation quality?" question in QA.

Backend: deep-translator (Google). English is kept as-is (data is English).

Resumable + safe: shows a progress bar, retries a failed call a couple of times,
and saves the cache incrementally (every SAVE_EVERY new translations) so an
interrupted or rate-limited run loses nothing and just resumes from the cache.
Run:  python translate.py
"""
import json
import time

from tqdm import tqdm

import config
from data_utils import sample_rows

SAVE_EVERY = 25      # flush cache to disk every N new translations
RETRIES = 3          # attempts per (row, lang) before giving up
RETRY_SLEEP = 2.0    # seconds between retries (rate-limit backoff)


def get_translator():
    try:
        from deep_translator import GoogleTranslator
    except ImportError:
        raise SystemExit(
            "Install the translator first:  pip install deep-translator"
        )
    return GoogleTranslator


def _save(cache):
    config.TRANSLATIONS_PATH.write_text(
        json.dumps(cache, ensure_ascii=False, indent=2)
    )


def main():
    rows = sample_rows()
    cache = {}
    if config.TRANSLATIONS_PATH.exists():
        cache = json.loads(config.TRANSLATIONS_PATH.read_text())

    GoogleTranslator = get_translator()
    n_new, n_fail = 0, 0
    pending = [(r, l) for r in rows for l in config.ACTIVE_LANGUAGES
               if l not in cache.get(r["id"], {})]
    print(f"{len(pending)} (row x lang) to translate "
          f"(langs={config.ACTIVE_LANGUAGES}); {len(cache)} rows cached.")

    for r, lang in tqdm(pending, desc="translate"):
        entry = cache.setdefault(r["id"], {"source": r["text"]})
        if lang in entry:
            continue
        if lang == "en":
            entry[lang] = r["text"]
            continue
        tgt = config.LANGUAGES[lang]["code"]
        for attempt in range(RETRIES):
            try:
                entry[lang] = GoogleTranslator(source="en", target=tgt).translate(r["text"])
                n_new += 1
                break
            except Exception as e:
                if attempt == RETRIES - 1:
                    n_fail += 1
                    tqdm.write(f"  ! {r['id']}/{lang} failed after {RETRIES}: {e}")
                else:
                    time.sleep(RETRY_SLEEP)
        if n_new and n_new % SAVE_EVERY == 0:
            _save(cache)

    _save(cache)
    print(f"\nTranslated {n_new} new entries ({n_fail} failed -> will retry on "
          f"next run). Cache: {config.TRANSLATIONS_PATH} ({len(cache)} rows)")
    for rid in list(cache)[:2]:
        print("\n", rid, json.dumps(cache[rid], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
