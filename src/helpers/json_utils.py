import json


def extract_json(raw: str) -> dict:
    """
    Extract the first complete JSON object from a raw model completion.

    Handles nested objects/arrays, braces inside quoted strings, escaped
    quotes, markdown code fences and any text the model writes before or
    after the object. Raises ValueError when no valid JSON object is found.

    ``JSONDecoder.raw_decode`` stops at the end of the first valid object,
    which is what makes it safe against the model appending extra text
    (the source of the old ``JSONDecodeError: Extra data`` failure).
    """

    if not isinstance(raw, str):
        raise ValueError("Model output must be a string")

    decoder = json.JSONDecoder()
    first_error = None
    index = raw.find("{")

    while index != -1:
        try:
            value, _end = decoder.raw_decode(raw, index)
        except json.JSONDecodeError as exc:
            if first_error is None:
                first_error = exc
        else:
            if isinstance(value, dict):
                return value

        index = raw.find("{", index + 1)

    if first_error is not None:
        raise ValueError(
            "Model output does not contain a valid JSON object: "
            f"{first_error.msg} at position {first_error.pos}"
        )

    raise ValueError("Model output does not contain a JSON object")
