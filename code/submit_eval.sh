#!/bin/bash
#SBATCH --job-name=protobias
#SBATCH --partition=a40
#SBATCH --gres=gpu:a40:1
#SBATCH --cpus-per-task=8
#SBATCH --time=02:00:00
#SBATCH --output=%x_%j.out
#SBATCH --error=%x_%j.err

# Real Qwen2.5-VL 2AFC prototypicality-bias eval on the Alex GPU cluster.
# Submit from the project dir:  cd ~/P5_histobias && sbatch submit_eval.sh
set -e

SCRIPT_DIR="${SLURM_SUBMIT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)}"
cd "$SCRIPT_DIR"
echo "Running in: $SCRIPT_DIR"
nvidia-smi || true

module load python/3.12-base
source .venv/bin/activate

# Reuse the cache the login node populated (model + dataset already there).
# Go offline so a network-less compute node never hangs reaching the Hub.
export HF_HOME="$HOME/hf_cache"
export HF_HUB_OFFLINE=1
export HF_DATASETS_OFFLINE=1
export TOKENIZERS_PARALLELISM=false

python -c "import torch; print('CUDA available:', torch.cuda.is_available(), torch.cuda.get_device_name(0) if torch.cuda.is_available() else '')"

echo "=== run_eval (real Qwen2.5-VL) ==="
python run_eval.py

echo "=== analyze ==="
python analyze.py

echo "Done. Results in $SCRIPT_DIR/results/ and figures in $SCRIPT_DIR/figures/"
