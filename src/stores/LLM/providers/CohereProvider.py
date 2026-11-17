from ..LLMInterface import LLmInterface
from ..LLMEnums import RoleCohereEnum
from groq import Groq
import logging
import cohere

class CohereProvider(LLmInterface):

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

        self.client = cohere.Client(
            api_key=self.api_key,
            api_url=self.api_url
        )

        self.logger = logging.getLogger(__name__)

   def set_generation_model(self, model_id):
       self.generation_model_id = model_id

   def process_text(self,text:str):
       return text[:self.default_generation_input_max_character]

   def generate_text(self, prompt:str, chat_history:list= [], max_output_tokens:int=1000, temperature:float= 0.1):

       # validate if client exist 

      if not self.client:
           self.logger.error("client not set ")
           return None

      if not self.generation_model_id:
          self.logger.error("generation model not set")
          return None 

      chat_history.append(
          self.construct_prompt(prompt=prompt, role =RoleCohereEnum.USER.value)
      )

      response = self.client.chat(
         model= self.generation_model_id,
         chat_history=chat_history,
         temperature=temperature,
         max_tokens = max_output_tokens
      )

      if not response or len(response) == 0 or not response.chat_history[0].message or len(response.chat_history[0].message) == 0 :
         self.logger.error("error in response")

      return response.text

   def construct_prompt(self, prompt, role):
       return {
           "role": role,
           "message":self.process_text(prompt)
       }

     

      


        
