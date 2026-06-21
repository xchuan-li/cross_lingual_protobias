# P5 — Cross-lingual Prototypicality Bias in Multimodal AI

Does a VLM pick the **typical-but-wrong** image over the **semantically-correct-but-atypical** one — and does that bias change across languages? We evaluate **Qwen2.5-VL** on **ProtoBias** with a 2AFC protocol.

**Main finding (v2):** Bias is **attribute-specific** (wealth=.77, power=.67 vs morality=.49, intellect=.48) and **cross-linguistically invariant** (EN/ZH/AR/HI). It is a structural property of visual representation, not language-driven.

## Project versions

| Version | Focus | Status |
|---|---|---|
| [v1](v1/README.md) | Course MVP: pipeline + pilot run (450 rows, EN/ZH/AR) | Done |
| [v2](v2/README.md) | Full 4-language eval + attribute-specific discovery (3600 rows) | Done |
| [v3](v3/README.md) | Workshop paper: mixed-effects model, extended languages, translation QA | Planned |

## Repository layout

```
v1/              # Course MVP
  experiments/
  paper/         # ProgressReport_1, SPEAKER_NOTES
v2/              # Full eval + attribute discovery
  experiments/
    exp1_900x4lang/       # 3600-row main eval
    exp2_attribute_bias/  # socio_attr re-analysis
  paper/         # proposal_new.md, SUPPLEMENT_additions.pptx
v3/              # Planned workshop paper
  paper/
shared/
  code/          # pipeline (run_eval.py, backends.py, translate.py, analyze.py, …)
  figures/       # main result figures (fig1, fig2)
papers/          # reference PDFs (ProtoBias + related work)
archive/         # HuggingFace HTML cache, SLURM logs
PROJECT_NOTES.md # long-term project memory (data, decisions, progress log)
```

## Quick start

```bash
cd shared/code
pip install datasets pillow tqdm matplotlib deep-translator
python translate.py        # build translations.json (run on login node — needs network)
python run_eval.py --mock  # smoke-test without GPU
python analyze.py          # figures + summary.csv
```

For GPU runs: see `shared/code/README.md` and `submit_eval.sh`.

## Data & model

- **Data:** `subha-roy/dl4dh_data` (ProtoBias, 1500 rows, 3 domains × 500)
- **Model:** `Qwen/Qwen2.5-VL-7B-Instruct`
