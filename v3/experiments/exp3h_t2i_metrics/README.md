# exp3h — T2I alignment metrics (PR-II advisor ask)

Advisor feedback on PR II: *"add some T2I evaluation metrics in the results,
such as VQAScore, CLIPScore, PickScore."*

Our headline measure is **behavioural** — a VLM is asked to pick one of two
images. T2I alignment metrics add an orthogonal, **representational** measure of
the *same* items: score the neutral English description against each image and
compare.

```
margin = score(correct_image, text) - score(adversarial_image, text)
margin > 0  ->  metric prefers the semantically-correct (atypical) image
margin < 0  ->  metric prefers the typical-but-wrong image
               = the metric ITSELF is prototypicality-biased (no VLM involved)
metric_bias_rate = share of items with margin < 0   (0.5 = no bias)
```

## Two questions this answers

1. **Is the bias in the representation, or only in the VLM's decoding?**
   If CLIP/PickScore already score the typical image higher — especially on the
   same attributes/subcategories where the VLM is biased (wealth/power; bird,
   vehicle) — the bias is baked into the image-text embedding space, not an
   artifact of one VLM's answer generation.

2. **Does the VLM's choice track the metric?** (`analyze_t2i.py`, join on `item`)
   Split the VLM's English correct-pick rate by which image the metric scored
   higher. A positive "tracking gap" means behaviour and representation are the
   same phenomenon at two levels.

## Metrics
| key | what | model | cost |
|---|---|---|---|
| `clip` | CLIPScore = cosine(image, text) | `openai/clip-vit-large-patch14` | light |
| `pick` | PickScore (human-preference CLIP) | `yuvalkirstain/PickScore_v1` | light |
| `mclip` | multilingual CLIPScore (for translated prompts) | `google/siglip-base-patch16-256-multilingual` | light |
| `vqa` | VQAScore, P(image entails text) | `t2v_metrics` (`clip-flant5-xxl`) | heavy, separate env |

`clip`/`pick` have English-only text towers, so the cross-lingual run
(`--text translated`) uses `mclip` (SigLIP-multilingual) on the actual
translated prompts. `vqa` needs a dedicated environment (`pip install
t2v_metrics`, default model `clip-flant5-xxl`); it is skipped automatically if
the package is absent, so the others always run.

## Run
```bash
# plumbing test — no downloads, no GPU (uses item metadata + translations.json)
python compute_t2i_metrics.py --mock && python analyze_t2i.py
python compute_t2i_metrics.py --mock --text translated && python analyze_xlingual.py

# (1) English representation run — CLIPScore + PickScore.  Resumable on (item, metric).
python compute_t2i_metrics.py --metrics clip pick    # -> results/t2i_scores.csv
python analyze_t2i.py                                 # -> figI, figJ

# (2) Cross-lingual run (mentor ask) — score the TRANSLATED prompt per language
#     with a multilingual backbone.  Resumable on (item, lang, metric).
python compute_t2i_metrics.py --text translated       # -> results/t2i_scores_xlingual.csv
python analyze_xlingual.py                            # -> figK_xlingual_bias_mclip.png

# (3) VQAScore — in a SEPARATE environment (see below).
python compute_t2i_metrics.py --metrics vqa           # appends to results/t2i_scores.csv
```

### VQAScore — dedicated environment (mentor's instruction)
`t2v_metrics` pins its own deps and conflicts with the eval venv, so build a
fresh one and use the package default `clip-flant5-xxl` (~11B, fits one A40):
```bash
python -m venv .venv_vqa && source .venv_vqa/bin/activate
pip install t2v_metrics                     # pulls its own torch/transformers
export HF_HOME="$(ws_find protobias)/hf_cache"
python compute_t2i_metrics.py --metrics vqa --limit 2   # prime clip-flant5-xxl, smoke test
python compute_t2i_metrics.py --metrics vqa             # full run (resumable)
```
If pip resolution fights, resolve per the error (ChatGPT/Claude help) — usually a
torch/transformers version pin. VQAScore rows land in the same `t2i_scores.csv`
and `analyze_t2i.py` picks them up as a third metric automatically.

## Results (CLIPScore + PickScore, 900 items)

**1. The bias is in the representation, not just the VLM's decoding.**
Overall metric bias rate — share of items where the metric scores the
typical-but-wrong image higher — is **CLIP 0.71, PickScore 0.67**, far above the
0.5 no-bias line, and similar across all three domains.

**2. The embedding space carries the VLM's exact attribute signature** (fig `figI`).
Demography metric bias rate falls monotonically wealth → intellect, mirroring
the behavioural wealth/power >> morality/intellect pattern from exp2/exp3a:

| socio_attr | CLIP bias rate | PickScore bias rate |
|---|---|---|
| wealth | 0.90 | 0.90 |
| power | 0.77 | 0.77 |
| civility | 0.67 | 0.61 |
| morality | 0.65 | 0.57 |
| intellect | 0.65 | 0.54 |

**3. The VLM's choice tracks the metric** (fig `figJ`, tracking gap +0.26 to +0.34,
consistent across both models × both metrics). When the metric prefers the
correct image the VLM picks it ~0.64–0.70 of the time; when the metric prefers
the typical image the VLM picks correct only ~0.34–0.41. VLM–metric agreement
0.62–0.66. The behavioural bias and the embedding-space bias are the same
phenomenon at two levels — so prototypicality bias is a property of the shared
image-text representation, not an artifact of one model's answer generation.

## Cross-lingual result (mclip on the translated prompts, 900 items × 7 langs)

The mentor asked to run the T2I evaluation on the translated prompts. Using
SigLIP-multilingual (`mclip`) on the real translated text gives a clean
**dissociation** (fig `figK_xlingual_bias_mclip.png`):

- The representation is prototypicality-biased in **every** language — metric
  bias rate 0.58–0.66, all far above 0.5.
- But it is **flat across languages** — no Bengali/Greek amplification (Bengali
  is if anything slightly *lower*, 0.58 vs English 0.65; all CIs overlap).

So the two axes split by level:
- **Attribute bias → representational**: VLM, CLIP, PickScore and mclip all show
  the wealth/power >> morality/intellect pattern.
- **Language effect → NOT in the shared representation**: the behavioural
  Bengali/Greek lift does not appear in the multilingual embedding, so it arises
  in the VLM's own language handling / decoding, not in image–text alignment.

Caveat: SigLIP-multilingual is trained to align many languages *equally* well, so
it is not expected to penalise low-resource languages — this shows the effect is
absent from *this* representation, not that it is absent from every VLM's own
text encoder.

## Scope / caveats
- **English text only** by design: this isolates the *representation* question.
  The cross-lingual axis stays with the VLM behaviour (exp3a/b). A multilingual
  extension would swap in a multilingual CLIP (e.g.
  `sentence-transformers/clip-ViT-B-32-multilingual-v1`) — noted as follow-up.
- Demography attribute cells are small (wealth n≈31 per the seed-42 sample), so
  read figI with its Wilson CIs; the domain/subcategory pools are larger.
- CLIPScore text is truncated to CLIP's 77-token limit (fine — `text` is short).

## Outputs
- `results/t2i_scores.csv` — per item × metric: score_correct, score_adv, margin
- `results/metric_bias_by_attr.csv`, `metric_bias_by_subcategory.csv`
- `results/vlm_metric_tracking.csv` — VLM–metric agreement + tracking gap
- `figures/figI_metric_bias_by_attr.png`, `figures/figJ_vlm_tracks_metric.png`
