# Pipeline — Cross-lingual Prototypicality Bias (2AFC eval)

Measures whether Qwen2.5-VL picks the **typical-but-wrong** image over the
**semantically-correct-but-atypical** one, and whether that bias changes across
languages (RQ1) and is worse in socially sensitive domains (RQ2).

See `../PROJECT_NOTES.md` for the full motivation, data description, and design.

## Files
| file | role |
|---|---|
| `config.py` | all settings: sample size, languages, model, paths |
| `data_utils.py` | load + balanced-sample ProtoBias; decode image pairs |
| `translate.py` | translate the neutral `text` into each language → `results/translations.json` (human-reviewable) |
| `backends.py` | `MockChooser` (no GPU, for testing) and `QwenChooser` (real) |
| `run_eval.py` | 2AFC loop → `results/predictions.jsonl` (resumable) |
| `analyze.py` | aggregate → `figures/fig1`, `fig2`, `results/summary.csv` |

## Quick start

### A) Laptop smoke test (no GPU, no model)
```bash
pip install datasets pillow tqdm matplotlib
# create fake translations + run with the mock model to verify plumbing:
python translate.py        # or skip; run_eval can use any translations.json
python run_eval.py --mock
python analyze.py
```
`MockChooser` *simulates* a biased model (and fakes stronger bias in
low-resource languages) so the figures look realistic — **these are not real
results**, only a plumbing check.

### B) Real run on the GPU machine
```bash
pip install -r requirements.txt
pip install torch --index-url https://download.pytorch.org/whl/cu121
pip install "transformers>=4.49" accelerate qwen-vl-utils

python translate.py        # needs network (Google translate)
python run_eval.py         # real Qwen2.5-VL; writes predictions.jsonl
python analyze.py          # figures + summary.csv
```

## Knobs (in `config.py`)
- `N_PER_DOMAIN` — 50 for pilot, set `None` for all 1500.
- `ACTIVE_LANGUAGES` — currently `["en","zh","ar"]`; add `"hi"` for the next round.
- `QWEN_MODEL` — `Qwen2.5-VL-7B-Instruct` (single GPU) or `-32B-` (stronger).
- `IMAGE_MAX_SIDE` — downscale for speed (originals are 1024²).

## Method notes (for the report / QA)
- **2AFC, randomized left/right** so image position can't be a confound.
- Metric = **% adversarial chosen** (chance = 0.5).
- Whole prompt (instruction + description) is in the target language → clean RQ1.
- Answer forced to a **digit (1/2)** so parsing is language-neutral.
- **Known confound:** the adversarial image also changes a visual `knob`
  (e.g. color), so a wrong pick isn't purely prototypicality. Mention this.
- Translations cached as JSON → eyeball them to answer "translation quality?".
