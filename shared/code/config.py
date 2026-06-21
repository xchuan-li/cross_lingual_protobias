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

RESULTS_DIR.mkdir(exist_ok=True)
FIGURES_DIR.mkdir(exist_ok=True)


def predictions_path(model_key):
    """Per-model predictions file, so multiple models (run as separate SLURM
    jobs) never clobber each other and each run stays resumable."""
    return RESULTS_DIR / f"predictions_{model_key}.jsonl"

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
    "hi": {
        "name": "Hindi",
        "code": "hi",
        "instruction": (
            "चित्र 1 और चित्र 2 देखें। कौन सा चित्र इस विवरण से बेहतर मेल खाता है: "
            "\"{desc}\"? केवल एक अंक 1 या 2 में उत्तर दें।"
        ),
    },
    # --- v3 additions (mentor request): resource x script design axis ---
    # NOTE: ru/bn/el instruction templates were drafted by an LLM and should get
    # a quick native-speaker / back-translation check (this is exactly the
    # translation-QA workstream). Digits are kept ASCII (1/2) so _parse_choice
    # works regardless of script, matching the zh/ar/hi templates.
    "ru": {  # Russian — high-resource, Cyrillic script
        "name": "Russian",
        "code": "ru",
        "instruction": (
            "Посмотрите на Изображение 1 и Изображение 2. Какое изображение "
            "лучше соответствует этому описанию: \"{desc}\"? "
            "Ответьте только одной цифрой: 1 или 2."
        ),
    },
    "bn": {  # Bengali — low-resource, Bengali (Brahmic) script, many speakers
        "name": "Bengali",
        "code": "bn",
        "instruction": (
            "চিত্র 1 এবং চিত্র 2 দেখুন। কোন চিত্রটি এই বিবরণের সাথে বেশি মেলে: "
            "\"{desc}\"? শুধুমাত্র একটি সংখ্যা দিয়ে উত্তর দিন: 1 বা 2।"
        ),
    },
    "el": {  # Greek — distinct script, mid-resource (clean script-isolation test)
        "name": "Greek",
        "code": "el",
        "instruction": (
            "Κοιτάξτε την Εικόνα 1 και την Εικόνα 2. Ποια εικόνα ταιριάζει "
            "καλύτερα με αυτήν την περιγραφή: \"{desc}\"; "
            "Απαντήστε μόνο με ένα ψηφίο: 1 ή 2."
        ),
    },
}

# Languages actually used in the current run.
# Ordered roughly high -> low resource, mixing scripts:
#   en/zh/ru high · ar/hi mid · bn/el lower / distinct-script.
ACTIVE_LANGUAGES = ["en", "zh", "ru", "ar", "hi", "bn", "el"]

# ----------------------------------------------------------------------------
# Models
# ----------------------------------------------------------------------------
# Registry of VLM judges. Run one model per SLURM job via `run_eval.py --model
# <key>`; each writes results/predictions_<key>.jsonl and analyze.py compares
# across all of them.
#   backend "qwen" -> QwenChooser (Qwen2_5_VLForConditionalGeneration)
#   backend "hf"   -> HFVLMChooser (AutoModelForImageTextToText, generic path)
#
# Three judges for PR II:
#   qwen7b    baseline (same as v1/v2; lets us reuse the established result)
#   qwen32b   same family, scaled up -> "does bias shrink with model size?"
#   internvl8b different family, size-matched -> "is attribute-bias Qwen-specific?"
#
# The different-family pick is swappable; size-matched HF-native alternates that
# also work with the generic backend (verify your transformers version on the
# cluster): "llava-hf/llava-onevision-qwen2-7b-ov-hf", "google/gemma-3-12b-it",
# "mistral-community/pixtral-12b".
MODELS = {
    "qwen7b":    {"hf": "Qwen/Qwen2.5-VL-7B-Instruct",  "backend": "qwen"},
    "qwen32b":   {"hf": "Qwen/Qwen2.5-VL-32B-Instruct", "backend": "qwen"},
    "internvl8b": {"hf": "OpenGVLab/InternVL2_5-8B",    "backend": "hf"},
}

# Default model for a run; override on the CLI: `run_eval.py --model qwen32b`.
ACTIVE_MODEL = "qwen7b"

# Back-compat alias (older scripts referenced config.QWEN_MODEL).
QWEN_MODEL = MODELS["qwen7b"]["hf"]

MAX_NEW_TOKENS = 8
# Resize long side of each image to this before sending (speed; 1024 originals).
IMAGE_MAX_SIDE = 512
