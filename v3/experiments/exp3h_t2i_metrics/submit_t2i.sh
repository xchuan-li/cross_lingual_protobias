#!/bin/bash
#SBATCH --job-name=protobias_t2i
#SBATCH --partition=a40
#SBATCH --gres=gpu:a40:1
#SBATCH --cpus-per-task=8
#SBATCH --time=01:00:00
#SBATCH --output=%x_%j.out
#SBATCH --error=%x_%j.err

# T2I alignment metrics (CLIPScore / PickScore) on the ProtoBias pairs.
# Mirrors submit_eval.sh: same venv, same HF cache workspace, offline compute.
#
# The translation cache is NOT needed here (English text only). But CLIP +
# PickScore weights and the HF dataset must already be in the cache. If the
# compute node is offline and they aren't cached, first run ONCE on the LOGIN
# node (online) to populate the cache:
#     python compute_t2i_metrics.py --limit 2 --metrics clip pick
# then submit this job for the full set.
set -e

SCRIPT_DIR="${SLURM_SUBMIT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}"
cd "$SCRIPT_DIR"
echo "Running in: $SCRIPT_DIR"
nvidia-smi || true

module load python/3.12-base 2>/dev/null || true
# reuse the eval venv (transformers/torch/datasets already there)
source "$SCRIPT_DIR/../../../shared/code/.venv/bin/activate" 2>/dev/null || \
  source .venv/bin/activate

export HF_HOME="${HF_HOME:-$(ws_find protobias 2>/dev/null)/hf_cache}"
export HF_HUB_OFFLINE=1
export HF_DATASETS_OFFLINE=1
export TOKENIZERS_PARALLELISM=false

python -c "import torch; print('CUDA:', torch.cuda.is_available())"

echo "=== compute_t2i_metrics (clip + pick) ==="
python compute_t2i_metrics.py --metrics clip pick

echo "=== analyze_t2i ==="
python analyze_t2i.py

echo "Done. results/t2i_scores.csv + figures/figI,figJ in $SCRIPT_DIR"
