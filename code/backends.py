"""2AFC choosers. Each takes (img1, img2, instruction_text) and returns 1 or 2.

- MockChooser:  no model needed. Lets you smoke-test the whole pipeline on a
  laptop. It simulates a *prototypicality-biased* model so the plots look
  realistic, and even fakes a stronger bias in low-resource languages so you
  can verify the analysis end-to-end before touching the GPU.
- QwenChooser:  real Qwen2.5-VL inference (needs GPU + transformers).
"""
import random
import re


class MockChooser:
    """Fake chooser for plumbing tests. NOT a real result."""

    def __init__(self, seed=0):
        self.rng = random.Random(seed)
        # simulated P(pick adversarial) by language, just for testing plots
        self.bias = {"en": 0.35, "zh": 0.40, "ar": 0.55, "hi": 0.60}

    def choose(self, img1, img2, instruction, adv_position, lang="en", domain="animal"):
        p = self.bias.get(lang, 0.45)
        if domain == "demography":
            p += 0.10  # pretend sensitive domain is worse
        pick_adv = self.rng.random() < p
        return adv_position if pick_adv else (3 - adv_position)


class QwenChooser:
    """Real Qwen2.5-VL chooser."""

    def __init__(self, model_name, max_new_tokens=8):
        import torch
        from transformers import (
            Qwen2_5_VLForConditionalGeneration,
            AutoProcessor,
        )
        self.torch = torch
        self.max_new_tokens = max_new_tokens
        self.model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
            model_name, torch_dtype="auto", device_map="auto"
        )
        self.processor = AutoProcessor.from_pretrained(model_name)

    def choose(self, img1, img2, instruction, adv_position=None, lang=None, domain=None):
        from qwen_vl_utils import process_vision_info
        messages = [{
            "role": "user",
            "content": [
                {"type": "image", "image": img1},
                {"type": "image", "image": img2},
                {"type": "text", "text": instruction},
            ],
        }]
        text = self.processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        image_inputs, video_inputs = process_vision_info(messages)
        inputs = self.processor(
            text=[text], images=image_inputs, videos=video_inputs,
            padding=True, return_tensors="pt",
        ).to(self.model.device)
        with self.torch.no_grad():
            gen = self.model.generate(**inputs, max_new_tokens=self.max_new_tokens)
        trimmed = gen[:, inputs.input_ids.shape[1]:]
        out = self.processor.batch_decode(
            trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
        )[0]
        return _parse_choice(out)


def _parse_choice(text):
    """Return 1, 2, or None from raw model output."""
    m = re.search(r"[12]", text)
    return int(m.group()) if m else None
