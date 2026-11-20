import os
import unittest

RUN_E2E = os.getenv("RUN_E2E") == "1"

SAMPLE_PROJECT_ID = "1"
SAMPLE_PDF = "nE97aRH1PG31_Adel_Ahmed_Gad_CV.pdf"


@unittest.skipUnless(
    RUN_E2E,
    "set RUN_E2E=1 to run the real model end-to-end test"
)
class RealModelEndToEndTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        from helpers import get_settings
        from stores.LLM import LLMProviderFactory

        cls.settings = get_settings()
        cls.client = LLMProviderFactory(cls.settings).create(
            provider=cls.settings.GENERATION_BACKEND
        )

        if cls.client is None:
            raise RuntimeError(
                f"Unknown generation backend: {cls.settings.GENERATION_BACKEND}"
            )

        cls.client.set_generation_model(cls.settings.HUGGINGFACE_MODEL_NAME)

    def test_extract_real_cv(self):
        from controllers import ProcessController

        controller = ProcessController(project_id=SAMPLE_PROJECT_ID)
        text = controller.get_text_cv(SAMPLE_PDF)

        self.assertTrue(text)
        self.assertGreater(len(text), 500)

        captured = {}
        original_generate = self.client.generate_text

        def capture_generate(*args, **kwargs):
            response = original_generate(*args, **kwargs)
            captured["raw"] = response
            return response

        # Capture the raw completion while running the real controller flow.
        self.client.generate_text = capture_generate
        try:
            data = controller.extract_cv_data(
                text,
                self.client,
                max_output_tokens=600
            )
        finally:
            self.client.generate_text = original_generate

        raw = captured["raw"]

        self.assertTrue(raw)
        # Only newly generated tokens are decoded: the prompt starts with
        # <|input|> and the full cv text must not be echoed back.
        self.assertFalse(raw.lstrip().startswith("<|input|>"))
        self.assertNotIn(text, raw)

        self.assertIsInstance(data, dict)

        for key in (
            "name",
            "email",
            "phone",
            "website",
            "skills",
            "experience",
            "education",
            "other_details",
        ):
            self.assertIn(key, data)

        self.assertTrue(
            data["name"] or data["email"] or data["skills"],
            "The model returned no usable cv data"
        )


if __name__ == "__main__":
    unittest.main()
