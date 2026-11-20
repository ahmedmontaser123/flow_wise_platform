import unittest

from helpers.json_utils import extract_json


class ExtractJsonTests(unittest.TestCase):

    def test_plain_object(self):
        self.assertEqual(extract_json('{"a": 1}'), {"a": 1})

    def test_trailing_text_after_object(self):
        # This is the case that used to raise "JSONDecodeError: Extra data".
        raw = '{"name": "Ada Lovelace"}\n\nI hope this helps!'

        self.assertEqual(extract_json(raw), {"name": "Ada Lovelace"})

    def test_text_before_and_after_object(self):
        raw = 'Here is the result:\n{"name": "Ada"}\nEnd of output'

        self.assertEqual(extract_json(raw), {"name": "Ada"})

    def test_nested_objects_and_arrays(self):
        raw = (
            'prefix {"experience": ['
            '{"title": "Engineer", "tags": ["python", "math"]},'
            '{"title": "Analyst", "tags": []}'
            '], "meta": {"ok": true}} suffix'
        )

        data = extract_json(raw)

        self.assertEqual(len(data["experience"]), 2)
        self.assertEqual(data["experience"][0]["tags"], ["python", "math"])
        self.assertEqual(data["meta"], {"ok": True})

    def test_braces_inside_quoted_strings(self):
        raw = '{"summary": "handles {curly} braces } without breaking"}'

        self.assertEqual(
            extract_json(raw),
            {"summary": "handles {curly} braces } without breaking"}
        )

    def test_escaped_quotes(self):
        raw = '{"summary": "he said \\"hello\\" and left"}'

        self.assertEqual(
            extract_json(raw),
            {"summary": 'he said "hello" and left'}
        )

    def test_markdown_code_fence(self):
        raw = '```json\n{"name": "Ada"}\n```'

        self.assertEqual(extract_json(raw), {"name": "Ada"})

    def test_hallucinated_text_and_second_object_after_first(self):
        # Observed with the real NuExtract adapter: extra "### Text:" content
        # and a second JSON object after the first completion.
        raw = (
            ':\n{"name": "Adel"}\n'
            '### Text:\nAnother CV\n<|output|>{"name": "Other"}'
        )

        self.assertEqual(extract_json(raw), {"name": "Adel"})

    def test_missing_json_raises(self):
        with self.assertRaises(ValueError):
            extract_json("The model did not return any structured data.")

    def test_json_array_is_rejected(self):
        with self.assertRaises(ValueError):
            extract_json("[1, 2, 3]")

    def test_non_string_input_raises(self):
        with self.assertRaises(ValueError):
            extract_json(None)


if __name__ == "__main__":
    unittest.main()
