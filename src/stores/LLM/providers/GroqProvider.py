from ..LLMInterface import LLmInterface
from ..LLMEnums import RoleGroqEnum
from groq import Groq
import logging

class GroqProvider(LLmInterface):

    def __init__(self,api_key:str,api_url:str=None,default_generation_input_max_character:int=1000, 
                 default_generation_max_output_of_tokens:int=1000,
                 default_generation_temperature:float=0.1):

        # add key and url 
        self.api_key = api_key
        self.api_url = api_url


        # set generation constrains in input and output 
        self.default_generation_input_max_character = default_generation_input_max_character
        self.default_generation_max_output_of_tokens = default_generation_max_output_of_tokens
        self.default_generation_temperature = default_generation_temperature

        self.generation_model_id = None

        # connect to qrok

        self.client = Groq(
            api_key=self.api_key,
            base_url=self.api_url
        )

        self.logger = logging.getLogger(__name__)

    def process_text(self,text:str):
        return text[:self.default_generation_input_max_character].strip()

    def set_generation_model(self,model_id:str):
        self.generation_model_id = model_id


    def generate_text(self,prompt:str,max_output_tokens: int = None ,chat_history:list = [] ,temperature: float = None):

        if not self.client:
            self.logger.error("Grok client is not set")
            return None

        if not self.generation_model_id:
            self.logger.error("generation model was not set")
            return None 

        max_output_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_output_of_tokens
        temperature = temperature if temperature else self.default_generation_temperature
        chat_history.append(
            self.construct_prompt(prompt=prompt , role=RoleGroqEnum.USER.value)
        )
        response = self.client.chat.completions.create(
              model= self.generation_model_id,
              temperature= temperature,
              messages=chat_history,
              max_completion_tokens=max_output_tokens

        )


        if not response or len(response) == 0 or not response.choices[0].message or len(response.choices[0].message.content) == 0:
            self.logger.error("something wrong in generation text")
            return None


        return response.choices[0].message.content

    def construct_prompt(self, prompt, role):
        return {
            'role':role,
            'content': self.process_text(prompt)
        }

