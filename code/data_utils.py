"""Load and sample the ProtoBias dataset; decode image pairs."""
import io
from functools import lru_cache

from datasets import load_dataset
from PIL import Image

import config


@lru_cache(maxsize=1)
def load_full():
    """Load the full HF dataset split (cached)."""
    return load_dataset(config.HF_DATASET)[config.HF_SPLIT]


def sample_rows():
    """Return a list of row dicts: balanced sample across domains.

    Each item keeps only the metadata we need plus row index, so we can lazily
    decode images later (avoids holding 1500 PIL images in memory).
    """
    ds = load_full()
    by_domain = {d: [] for d in config.DOMAINS}
    for i, dom in enumerate(ds["domain"]):
        if dom in by_domain:
            by_domain[dom].append(i)

    import random
    rng = random.Random(config.SAMPLE_SEED)
    rows = []
    for dom, idxs in by_domain.items():
        if config.N_PER_DOMAIN is not None and len(idxs) > config.N_PER_DOMAIN:
            idxs = rng.sample(idxs, config.N_PER_DOMAIN)
        for i in idxs:
            rows.append({
                "row_index": i,
                "id": ds["id"][i],
                "domain": ds["domain"][i],
                "subcategory": ds["subcategory"][i],
                "socio_attr": ds["socio_attr"][i],
                "gender": ds["gender"][i],
                "knob": ds["knob"][i],
                "text": ds["text"][i],
                "correct": ds["correct"][i],
                "adversarial": ds["adversarial"][i],
            })
    return rows


def _decode(field_value):
    im = Image.open(io.BytesIO(field_value["bytes"])).convert("RGB")
    if config.IMAGE_MAX_SIDE:
        im.thumbnail((config.IMAGE_MAX_SIDE, config.IMAGE_MAX_SIDE))
    return im


def get_image_pair(row_index):
    """Return (correct_image, adversarial_image) as PIL.Image for a row."""
    ds = load_full()
    row = ds[row_index]
    return _decode(row["correct_image"]), _decode(row["adversarial_image"])
