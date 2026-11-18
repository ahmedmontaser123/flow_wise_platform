from helpers import Settings
from .providers import CohereProvider,GroqProvider,HuggingFaceProvider
from .LLMEnums import LLMType
class LLMProviderFactory:
    def __init__(self, setting:Settings):
        self.setting = setting



    def create(self,provider:str):

        if provider == LLMType.GROQ.value:

            return GroqProvider(
                api_key=self.setting.GROQ_API_KEY,
                api_url= self.setting.GROQ_API_URL,
                default_generation_input_max_character= self.setting.INPUT_MAX_CHARACTER,
                default_generation_max_output_of_tokens=self.setting.MAX_OUTPUT_TOKENS,
                default_generation_temperature=self.setting.TEMPERATURE

            )


        if provider == LLMType.COHERE.value:

           return CohereProvider(
                api_key=self.setting.COHERE_API_KEY,
                api_url= self.setting.COHERE_URL_KEY,
                default_generation_input_max_character= self.setting.INPUT_MAX_CHARACTER,
                default_generation_max_output_of_tokens=self.setting.MAX_OUTPUT_TOKENS,
                default_generation_temperature=self.setting.TEMPERATURE  
           )


        if provider == LLMType.HUGGINGFACE.value:

           return HuggingFaceProvider(
                model_name=self.setting.HUGGINGFACE_MODEL_NAME,
                base_model_name=self.setting.HUGGINGFACE_BASE_MODEL_NAME,
                default_generation_input_max_character= self.setting.INPUT_MAX_CHARACTER,
                default_generation_max_output_of_tokens=self.setting.MAX_OUTPUT_TOKENS,
                default_generation_temperature=self.setting.TEMPERATURE  
           )

        


    