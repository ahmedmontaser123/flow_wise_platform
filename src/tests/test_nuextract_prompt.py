import json
import unittest
from unittest.mock import MagicMock, patch

import torch

from stores.LLM.providers.HuggingFaceProvider import (
    HuggingFaceProvider,
    NUEXTRACT_INPUT_MARKER,
    NUEXTRACT_OUTPUT_MARKER,
    NUEXTRACT_TEMPLATE,
    NUEXTRACT_TEXT_MARKER,
)


class CharTokenizer:
    """Minimal tokenizer: one token per character."""

    pad_token_id = 0
    eos_token_id = 1

    def __init__(self):
        self.calls = []

    def __call__(
        self,
        text,
        add_special_tokens=False,
        truncation=False,
        max_length=None
    ):
        self.calls.append({
            "text": text,
            "truncation": truncation,
            "max_length": max_length
        })

        ids = list(range(1, len(text) + 1))

        if truncation and max_length is not None:
            ids = ids[:max_length]

        return {"input_ids": ids}


class PromptConstructionTests(unittest.TestCase):

    def setUp(self):
        self.provider = HuggingFaceProvider(model_name="fake-model")

    def test_prompt_uses_nuextract_format(self):
        prompt = self.provider.construct_prompt(
            "Jane Doe\nPython developer",
            role=None
        )

        self.assertTrue(prompt.startswith(f"{NUEXTRACT_INPUT_MARKER}\n"))
        self.assertIn("### Template:\n", prompt)
        self.assertIn(
            f"{NUEXTRACT_TEXT_MARKER}Jane Doe\nPython developer",
            prompt
        )
        self.assertTrue(prompt.endswith(NUEXTRACT_OUTPUT_MARKER))

        template_text = prompt.split(
            "### Template:\n", 1
        )[1].split("\n### Text:\n", 1)[0]
        self.assertEqual(json.loads(template_text), NUEXTRACT_TEMPLATE)

        # No conversational instructions may be added to the prompt.
        lowered = prompt.lower()
        self.assertNotIn("you are", lowered)
        self.assertNotIn("please extract", lowered)
        self.assertNotIn("return json", lowered)

    def test_construct_prompt_is_idempotent(self):
        once = self.provider.construct_prompt("CV text", role=None)
        twice = self.provider.construct_prompt(once, role=None)

        self.assertEqual(once, twice)

    def test_construct_prompt_rejects_non_string(self):
        with self.assertRaises(TypeError):
            self.provider.construct_prompt(None)


class GenerationSettingsTests(unittest.TestCase):

    def setUp(self):
        self.provider = HuggingFaceProvider(model_name="fake-model")

        self.provider.tokenizer = MagicMock()
        self.provider.tokenizer.pad_token_id = 11
        self.provider.tokenizer.eos_token_id = 12
        self.provider.tokenizer.decode.return_value = '{"name": "Ada"}'

        self.provider.model = MagicMock()
        self.provider.model.generate.return_value = torch.tensor(
            [[1, 2, 3, 4, 5]]
        )

        self.provider._prepare_inputs = MagicMock(return_value={
            "input_ids": torch.tensor([[1, 2, 3]]),
            "attention_mask": torch.ones((1, 3), dtype=torch.long),
        })

    def test_generate_text_uses_deterministic_extraction_settings(self):
        result = self.provider.generate_text("CV text", max_output_tokens=600)

        self.assertEqual(result, '{"name": "Ada"}')

        kwargs = self.provider.model.generate.call_args.kwargs

        self.assertIs(kwargs["do_sample"], False)
        self.assertEqual(kwargs["max_new_tokens"], 600)
        self.assertEqual(kwargs["num_beams"], 1)
        self.assertEqual(kwargs["num_return_sequences"], 1)
        self.assertEqual(kwargs["repetition_penalty"], 1.0)
        self.assertIs(kwargs["use_cache"], True)
        self.assertEqual(kwargs["pad_token_id"], 11)
        self.assertEqual(kwargs["eos_token_id"], 12)
        self.assertNotIn("temperature", kwargs)

    def test_generate_text_decodes_only_new_tokens(self):
        self.provider.generate_text("CV text", max_output_tokens=600)

        decoded_ids = self.provider.tokenizer.decode.call_args.args[0]

        self.assertEqual(decoded_ids.tolist(), [4, 5])

    def test_generate_text_returns_none_without_model(self):
        provider = HuggingFaceProvider(model_name="fake-model")

        self.assertIsNone(provider.generate_text("CV text"))


class InputTruncationTests(unittest.TestCase):

    def setUp(self):
        self.provider = HuggingFaceProvider(model_name="fake-model")
        self.provider.tokenizer = CharTokenizer()
        self.provider.default_generation_max_input_tokens = 2048

    def test_long_cv_is_truncated_to_the_token_budget(self):
        cv_text = "x" * 5000
        prompt = self.provider.construct_prompt(cv_text, role=None)

        inputs = self.provider._prepare_inputs(prompt)

        self.assertEqual(inputs["input_ids"].shape[1], 2048)

    def test_template_and_output_marker_are_reserved(self):
        cv_text = "x" * 5000
        prompt = self.provider.construct_prompt(cv_text, role=None)

        self.provider._prepare_inputs(prompt)

        calls = self.provider.tokenizer.calls

        marker_call = next(
            call for call in calls if call["text"] == NUEXTRACT_OUTPUT_MARKER
        )
        self.assertFalse(marker_call["truncation"])

        prefix_call = next(
            call for call in calls if "### Template:" in call["text"]
        )
        self.assertIn(NUEXTRACT_TEXT_MARKER, prefix_call["text"])
        self.assertFalse(prefix_call["truncation"])

        cv_call = next(call for call in calls if call["text"] == cv_text)
        self.assertTrue(cv_call["truncation"])
        self.assertLess(cv_call["max_length"], 2048)

    def test_input_is_shortened_without_losing_the_text_section(self):
        cv_text = "y" * 3000
        prompt = self.provider.construct_prompt(cv_text, role=None)

        self.provider._prepare_inputs(prompt)

        cv_call = next(
            call for call in self.provider.tokenizer.calls
            if call["text"] == cv_text
        )

        # The budget accounts for the prompt template and the marker.
        self.assertGreater(cv_call["max_length"], 0)
        self.assertLess(cv_call["max_length"], 2048)


class GenerationModelLoadingTests(unittest.TestCase):

    @patch("stores.LLM.providers.HuggingFaceProvider.AutoTokenizer")
    @patch("stores.LLM.providers.HuggingFaceProvider.AutoModelForCausalLM")
    @patch("stores.LLM.providers.HuggingFaceProvider.PeftModel")
    def test_set_generation_model_uses_configured_base_model(
        self,
        peft_model,
        auto_model,
        auto_tokenizer
    ):
        provider = HuggingFaceProvider(
            model_name="org/adapter",
            base_model_name="org/base"
        )

        provider.set_generation_model("org/adapter")

        auto_tokenizer.from_pretrained.assert_called_once_with(
            "org/adapter",
            trust_remote_code=True
        )
        auto_model.from_pretrained.assert_called_once()
        self.assertEqual(
            auto_model.from_pretrained.call_args.args[0],
            "org/base"
        )
        peft_model.from_pretrained.assert_called_once()

    @patch("stores.LLM.providers.HuggingFaceProvider.AutoTokenizer")
    @patch("stores.LLM.providers.HuggingFaceProvider.AutoModelForCausalLM")
    @patch("stores.LLM.providers.HuggingFaceProvider.PeftModel")
    def test_set_generation_model_falls_back_to_configured_adapter(
        self,
        peft_model,
        auto_model,
        auto_tokenizer
    ):
        provider = HuggingFaceProvider(
            model_name="org/adapter",
            base_model_name="org/base"
        )

        provider.set_generation_model()

        auto_tokenizer.from_pretrained.assert_called_once_with(
            "org/adapter",
            trust_remote_code=True
        )
        self.assertEqual(provider.generation_model_id, "org/adapter")

    def test_set_generation_model_requires_base_model(self):
        provider = HuggingFaceProvider(model_name="org/adapter")

        with self.assertRaises(ValueError):
            provider.set_generation_model()

    def test_set_generation_model_requires_adapter(self):
        provider = HuggingFaceProvider(
            model_name=None,
            base_model_name="org/base"
        )

        with self.assertRaises(ValueError):
            provider.set_generation_model()


if __name__ == "__main__":
    unittest.main()
