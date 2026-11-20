import unittest
from types import SimpleNamespace

from controllers.process_controller import ProcessController


class FakeGenerationClient:
    """Stands in for the Hugging Face provider in controller tests."""

    def __init__(self, response):
        self.response = response
        self.constructed_prompts = []
        self.generation_prompts = []
        self.max_output_tokens = []

    def construct_prompt(self, prompt, role=None):
        self.constructed_prompts.append(prompt)
        return (
            "<|input|>\n### Template:\n{}\n"
            f"### Text:\n{prompt}\n<|output|>"
        )

    def generate_text(self, prompt, max_output_tokens=None):
        self.generation_prompts.append(prompt)
        self.max_output_tokens.append(max_output_tokens)
        return self.response


class ProcessControllerExtractionTests(unittest.TestCase):

    def setUp(self):
        # Only app_settings is needed by extract_cv_data.
        self.controller = ProcessController.__new__(ProcessController)
        self.controller.app_settings = SimpleNamespace(
            MAX_OUTPUT_TOKENS=600
        )

    def test_valid_response_is_validated_and_returned_as_dict(self):
        response = """
        Here is the extracted data:
        {
            "name": "Ada Lovelace",
            "email": "ada@example.com",
            "skills": ["Python", "Mathematics"],
            "experience": [
                {"title": "Analyst", "company": "ACME", "duration": "1842-1843"},
                {"title": "Engineer", "company": "Other Ltd", "duration": "1844"}
            ],
            "education": [
                {"degree": "BSc", "institution": "University A", "year": "1830"},
                {"degree": "MSc", "institution": "University B", "year": "1832"}
            ]
        }
        I hope this helps!
        """
        client = FakeGenerationClient(response)

        data = self.controller.extract_cv_data("Ada Lovelace CV text", client)

        self.assertEqual(data["name"], "Ada Lovelace")
        self.assertEqual(data["email"], "ada@example.com")
        self.assertEqual(data["phone"], "")
        self.assertEqual(data["website"], "")
        self.assertEqual(data["skills"], ["Python", "Mathematics"])
        self.assertEqual(len(data["experience"]), 2)
        self.assertEqual(data["experience"][1]["company"], "Other Ltd")
        self.assertEqual(len(data["education"]), 2)
        self.assertEqual(data["education"][1]["year"], "1832")
        self.assertEqual(data["other_details"], [])

        # The controller hands the cleaned cv text to the prompt builder and
        # passes the constructed NuExtract prompt to the model.
        self.assertEqual(client.constructed_prompts, ["Ada Lovelace CV text"])
        self.assertIn("### Text:\nAda Lovelace CV text", client.generation_prompts[0])
        self.assertEqual(client.max_output_tokens, [600])

    def test_missing_fields_fall_back_to_schema_defaults(self):
        client = FakeGenerationClient(
            '{"name": null, "skills": null, "experience": null, "education": null}'
        )

        data = self.controller.extract_cv_data("CV text", client)

        self.assertEqual(data["name"], "")
        self.assertEqual(data["email"], "")
        self.assertEqual(data["skills"], [])
        self.assertEqual(data["experience"], [])
        self.assertEqual(data["education"], [])
        self.assertEqual(data["other_details"], [])

    def test_invalid_model_output_raises_value_error(self):
        client = FakeGenerationClient("I could not read this document.")

        with self.assertRaises(ValueError):
            self.controller.extract_cv_data("CV text", client)

    def test_empty_model_output_raises_value_error(self):
        client = FakeGenerationClient("   ")

        with self.assertRaises(ValueError):
            self.controller.extract_cv_data("CV text", client)

    def test_missing_model_returns_none(self):
        client = FakeGenerationClient(None)

        self.assertIsNone(
            self.controller.extract_cv_data("CV text", client)
        )

    def test_missing_generation_client_raises_runtime_error(self):
        with self.assertRaises(RuntimeError):
            self.controller.extract_cv_data("CV text", None)

    def test_empty_cv_text_raises_value_error(self):
        client = FakeGenerationClient("{}")

        with self.assertRaises(ValueError):
            self.controller.extract_cv_data("   ", client)

    def test_explicit_output_limit_overrides_settings(self):
        client = FakeGenerationClient('{"name": "Ada"}')

        self.controller.extract_cv_data("CV text", client, max_output_tokens=123)

        self.assertEqual(client.max_output_tokens, [123])


if __name__ == "__main__":
    unittest.main()
