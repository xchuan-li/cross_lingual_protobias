"""Central configuration for the cross-lingual prototypicality-bias pipeline.

Edit values here; all scripts import from this file.
"""
from pathlib import Path

# ----------------------------------------------------------------------------
# Paths
# ----------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent
RESULTS_DIR = ROOT / "results"
FIGURES_DIR = ROOT / "figures"
TRANSLATIONS_PATH = RESULTS_DIR / "translations.json"
PREDICTIONS_PATH = RESULTS_DIR / "predictions.jsonl"

RESULTS_DIR.mkdir(exist_ok=True)
FIGURES_DIR.mkdir(exist_ok=True)

# ----------------------------------------------------------------------------
# Dataset
# ----------------------------------------------------------------------------
HF_DATASET = "subha-roy/dl4dh_data"
HF_SPLIT = "test"
DOMAINS = ["animal", "object", "demography"]  # 500 each in full data

# Sampling for the pilot. Set N_PER_DOMAIN = None to use ALL rows.
N_PER_DOMAIN = 300
SAMPLE_SEED = 42

# ----------------------------------------------------------------------------
# Languages
# ----------------------------------------------------------------------------
# code: ISO code used by the translator (deep-translator / Google).
# instruction: the 2AFC question template, in that language. {desc} is filled
#   with the translated `text`. The model is asked to answer with a digit so
#   parsing is language-neutral.
LANGUAGES = {
    "en": {
        "name": "English",
        "code": "en",
        "instruction": (
            "Look at Image 1 and Image 2. Which image better matches this "
            "description: \"{desc}\"? Answer with only the single digit 1 or 2."
        ),
    },
    "zh": {
        "name": "Chinese",
        "code": "zh-CN",
        "instruction": (
            "请看图1和图2。哪张图更符合下面这句描述:“{desc}”?"
            "只回答数字 1 或 2。"
        ),
    },
    "ar": {
        "name": "Arabic",
        "code": "ar",
        "instruction": (
            "انظر إلى الصورة 1 والصورة 2. أي صورة تطابق هذا الوصف بشكل أفضل: "
            "\"{desc}\"؟ أجب برقم واحد فقط 1 أو 2."
        ),
    },
    # Add for the next round (low-resource):
    "hi": {
        "name": "Hindi",
        "code": "hi",
        "instruction": (
            "चित्र 1 और चित्र 2 देखें। कौन सा चित्र इस विवरण से बेहतर मेल खाता है: "
            "\"{desc}\"? केवल एक अंक 1 या 2 में उत्तर दें।"
        ),
    },
}

# Languages actually used in the current run.
ACTIVE_LANGUAGES = ["en", "zh", "ar", "hi"]

# ----------------------------------------------------------------------------
# Model
# ----------------------------------------------------------------------------
# Qwen2.5-VL. Use 7B for a single mid-size GPU; 32B for stronger results.
QWEN_MODEL = "Qwen/Qwen2.5-VL-7B-Instruct"
MAX_NEW_TOKENS = 8
# Resize long side of each image to this before sending (speed; 1024 originals).
IMAGE_MAX_SIDE = 512
