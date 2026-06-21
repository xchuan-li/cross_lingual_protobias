#!/bin/bash
#SBATCH --job-name=protobias
#SBATCH --partition=a40
#SBATCH --gres=gpu:a40:1
#SBATCH --cpus-per-task=8
#SBATCH --time=02:00:00
#SBATCH --output=%x_%j.out
#SBATCH --error=%x_%j.err

# Real VLM 2AFC prototypicality-bias eval on the Alex GPU cluster.
# ONE model per job. Submit one job per model:
#   sbatch submit_eval.sh qwen7b
#   sbatch submit_eval.sh internvl8b
#   sbatch --gres=gpu:a40:2 submit_eval.sh qwen32b   # 32B needs ~2 A40s
#
# 32B note: bf16 32B (~64GB) does NOT fit one 48GB A40. Either request 2 GPUs
# (device_map="auto" shards automatically) or load 4-bit. 7B/8B fit one A40.
#
# Translation cache must already exist: run `python translate.py` on the LOGIN
# node first (compute nodes are offline). It is model-independent and shared.
#
# After ALL model jobs finish, run analysis once on the login node:
#   python analyze.py
set -e

MODEL="${1:-qwen7b}"

SCRIPT_DIR="${SLURM_SUBMIT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}"
cd "$SCRIPT_DIR"
echo "Running in: $SCRIPT_DIR  | model: $MODEL"
nvidia-smi || true

module load python/3.12-base 2>/dev/null || true   # tolerate module rename post-OS-upgrade
source .venv/bin/activate

# Reuse the cache the login node populated (model + dataset already there).
# Go offline so a network-less compute node never hangs reaching the Hub.
# Cache lives on $WORK (big FS); $HOME quota is too small for the model weights.
export HF_HOME="${HF_HOME:-$WORK/hf_cache}"
export HF_HUB_OFFLINE=1
export HF_DATASETS_OFFLINE=1
export TOKENIZERS_PARALLELISM=false

python -c "import torch; print('CUDA available:', torch.cuda.is_available(), torch.cuda.get_device_name(0) if torch.cuda.is_available() else '')"

echo "=== run_eval (model=$MODEL) ==="
python run_eval.py --model "$MODEL"

echo "Done. predictions_${MODEL}.jsonl in $SCRIPT_DIR/results/"
echo "When all models are done, run:  python analyze.py"
