# Cross-lingual Prototypicality Bias in Multimodal AI

Does a vision-language model pick the **typical-but-wrong** image over the
**semantically-correct-but-atypical** one — and does that bias change across
languages and get worse in socially sensitive domains?

We evaluate **Qwen2.5-VL** on the **ProtoBias** dataset with a 2-alternative
forced-choice (2AFC) protocol, asking the same question in multiple languages.

- **RQ1** — Is prototypicality bias consistent across languages (English, Chinese, Arabic, Hindi)?
- **RQ2** — Are cross-lingual differences stronger in socially sensitive domains
  (e.g. demography) than in neutral ones (animals, objects)?

## Method (in brief)

For every image pair × language:
1. decode the *(correct, adversarial)* image pair,
2. randomize left/right order (so position can't be a confound),
3. ask the model, **in the target language**, which image matches the
   (translated) neutral description, forcing a single-digit `1`/`2` answer,
4. record whether it picked the adversarial (prototypical) image.

Metric = **prototypicality error rate** = % of trials where the adversarial
image was chosen (chance = 0.5), reported with 95% Wilson confidence intervals.

## Repository layout

| path | what |
|---|---|
| [`code/`](code/) | the full pipeline — see [`code/README.md`](code/README.md) for run instructions |
| `code/config.py` | all settings (sample size, languages, model, paths) |
| `code/run_eval.py` | 2AFC evaluation loop (resumable) → `results/predictions.jsonl` |
| `code/analyze.py` | aggregation → figures + `results/summary.csv` |
| `code/results/`, `code/figures/` | outputs from a pilot run |
| `code/experiments/` | per-experiment configs, results, and notes |
| `code/submit_eval.sh` | SLURM job script for the GPU cluster |
| `PROJECT_NOTES.md`, `proposal_new.md`, `Project_overview.md` | motivation, design, and proposal |

## Quick start

```bash
cd code
pip install datasets pillow tqdm matplotlib deep-translator
python translate.py        # build results/translations.json (human-reviewable)
python run_eval.py --mock  # smoke-test the pipeline with no GPU/model
python analyze.py          # figures + summary.csv
```

`--mock` uses a **simulated** biased model purely to verify the plumbing — those
figures are **not real results**. For a real run on a GPU (Qwen2.5-VL), see
[`code/README.md`](code/README.md).

## Data & model

- **Data:** [`subha-roy/dl4dh_data`](https://huggingface.co/datasets/subha-roy/dl4dh_data) (ProtoBias) on the Hugging Face Hub.
- **Model:** [`Qwen/Qwen2.5-VL-7B-Instruct`](https://huggingface.co/Qwen/Qwen2.5-VL-7B-Instruct).
