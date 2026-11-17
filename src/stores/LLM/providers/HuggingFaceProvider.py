
import torch
import logging
import json
from transformers import AutoTokenizer, AutoModelForCausalLM
from ..LLMInterface import LLmInterface
from peft import PeftModel


# Template expected by nimendraai/NuExtract-tiny-Resume-Data-Extractor.
# Its shape matches models.cv_parsed_schema.ParsedCvData.
NUEXTRACT_TEMPLATE = {
    "name": "",
    "email": "",
    "phone": "",
    "website": "",
    "skills": [""],
    "experience": [
        {
            "title": "",
            "company": "",
            "duration": ""
        }
    ],
    "education": [
        {
            "degree": "",
            "institution": "",
            "year": ""
        }
    ],
    "other_details": [""]
}

NUEXTRACT_INPUT_MARKER = "<|input|>"
NUEXTRACT_OUTPUT_MARKER = "<|output|>"
NUEXTRACT_TEXT_MARKER = "### Text:\n"

DEFAULT_MAX_INPUT_TOKENS = 2048
DEFAULT_MAX_NEW_TOKENS = 600


class HuggingFaceProvider(LLmInterface):

    def __init__(
        self,
        model_name: str,
        default_generation_input_max_character: int = 1000,
        default_generation_max_output_of_tokens: int = DEFAULT_MAX_NEW_TOKENS,
        default_generation_temperature: float = 0.1,
        default_generation_max_input_tokens: int = DEFAULT_MAX_INPUT_TOKENS
    ):

        self.model_name = model_name

        # Generation constraints
        self.default_generation_input_max_character = default_generation_input_max_character
        self.default_generation_max_output_of_tokens = default_generation_max_output_of_tokens
        self.default_generation_temperature = default_generation_temperature
        self.default_generation_max_input_tokens = default_generation_max_input_tokens

        # Device configuration
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        self.dtype = (
            torch.float16 if self.device == "cuda"
            else torch.float32
        )

        self.generation_model_id = None

        self.tokenizer = None
        self.model = None

        self.logger = logging.getLogger(__name__)


    def set_generation_model(self, model_id: str):

        self.generation_model_id = model_id

        try:
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_id,
                trust_remote_code=True
            )

            # Load base model
            base_model_id = "numind/NuExtract-tiny-v1.5"

            base_model = AutoModelForCausalLM.from_pretrained(
                base_model_id,
                torch_dtype=self.dtype,
                trust_remote_code=True
            ).to(self.device)

            # Load LoRA adapter
            self.model = PeftModel.from_pretrained(
                base_model,
                model_id
            )

            self.model.eval()

            self.logger.info(
                f"Model loaded successfully: {model_id}"
            )

        except Exception as e:
            self.logger.error(f"Error loading model: {e}")
            self.model = None
            self.tokenizer = None
            raise

    def construct_prompt(self, prompt: str, role: str = None) -> str:
        """Build the NuExtract prompt for a cleaned CV text.

        NuExtract expects a template-based format, not a chat prompt, so the
        ``role`` argument is accepted only for interface compatibility.
        """

        if not isinstance(prompt, str):
            raise TypeError("prompt must be a string")

        # Avoid wrapping a prompt that was already built by this method.
        stripped = prompt.lstrip()
        if (
            stripped.startswith(NUEXTRACT_INPUT_MARKER)
            and NUEXTRACT_TEXT_MARKER in stripped
        ):
            return prompt

        template = json.dumps(NUEXTRACT_TEMPLATE, indent=4)

        return (
            f"{NUEXTRACT_INPUT_MARKER}\n"
            f"### Template:\n{template}\n"
            f"{NUEXTRACT_TEXT_MARKER}{prompt}\n"
            f"{NUEXTRACT_OUTPUT_MARKER}"
        )

    def _prepare_inputs(self, prompt: str) -> dict:
        """Tokenize the prompt without cutting the template or the marker.

        The input limit applies to the whole prompt. Only the CV text itself
        is truncated so the NuExtract template and the closing ``<|output|>``
        marker always reach the model.
        """

        max_input_tokens = (
            self.default_generation_max_input_tokens
            or DEFAULT_MAX_INPUT_TOKENS
        )

        prompt = prompt.rstrip()

        suffix_ids = self.tokenizer(
            NUEXTRACT_OUTPUT_MARKER,
            add_special_tokens=False
        )["input_ids"]

        body = prompt
        if body.endswith(NUEXTRACT_OUTPUT_MARKER):
            body = body[:-len(NUEXTRACT_OUTPUT_MARKER)].rstrip()

        prefix, separator, cv_text = body.partition(NUEXTRACT_TEXT_MARKER)

        if separator:
            prefix = prefix + NUEXTRACT_TEXT_MARKER
            prefix_ids = self.tokenizer(
                prefix,
                add_special_tokens=False
            )["input_ids"]
        else:
            cv_text = body
            prefix_ids = []

        text_budget = max_input_tokens - len(prefix_ids) - len(suffix_ids)

        if text_budget <= 0:
            raise ValueError(
                "The NuExtract prompt template does not fit inside the "
                f"{max_input_tokens} token input limit"
            )

        text_ids = self.tokenizer(
            cv_text,
            add_special_tokens=False,
            truncation=True,
            max_length=text_budget
        )["input_ids"]

        input_ids = prefix_ids + text_ids + suffix_ids

        return {
            "input_ids": torch.tensor(
                [input_ids],
                dtype=torch.long,
                device=self.device
            ),
            "attention_mask": torch.ones(
                (1, len(input_ids)),
                dtype=torch.long,
                device=self.device
            )
        }

    def generate_text(
        self,
        prompt: str,
        chat_history: list = None,
        max_output_tokens: int = None,
        temperature: float = None
    ):

        if self.model is None or self.tokenizer is None:
            self.logger.error("Generation model not loaded")
            return None

        max_output_tokens = (
            max_output_tokens
            or self.default_generation_max_output_of_tokens
            or DEFAULT_MAX_NEW_TOKENS
        )

        # temperature and chat_history are accepted for interface
        # compatibility. Resume extraction always runs deterministically.
        prompt = self.construct_prompt(prompt)
        inputs = self._prepare_inputs(prompt)

        pad_token_id = (
            self.tokenizer.pad_token_id
            if self.tokenizer.pad_token_id is not None
            else self.tokenizer.eos_token_id
        )

        try:
            with torch.inference_mode():

                outputs = self.model.generate(
                    **inputs,
                    do_sample=False,
                    max_new_tokens=max_output_tokens,
                    num_beams=1,
                    num_return_sequences=1,
                    repetition_penalty=1.0,
                    use_cache=True,
                    pad_token_id=pad_token_id,
                    eos_token_id=self.tokenizer.eos_token_id
                )

        except Exception as e:
            self.logger.exception("Error generating text")
            raise RuntimeError("Text generation failed") from e

        # Decode only the newly generated tokens, never the prompt.
        generated_tokens = outputs[
            :, inputs["input_ids"].shape[1]:
        ]

        response = self.tokenizer.decode(
            generated_tokens[0],
            skip_special_tokens=True
        ).strip()

        # Some checkpoints repeat the output marker at the start.
        if response.startswith(NUEXTRACT_OUTPUT_MARKER):
            response = response[len(NUEXTRACT_OUTPUT_MARKER):].strip()

        return response
