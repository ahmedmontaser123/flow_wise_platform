from abc import ABC,abstractmethod

class LLmInterface(ABC):

    @abstractmethod
    def set_generation_model(self, model_id:str): # set generative model 
        pass

    @abstractmethod
    def generate_text(self,prompt:str,chat_history:list = None, max_output_tokens:int = 1000,temperature:float = 0.1): # generate text
        pass

    @abstractmethod
    def construct_prompt(self,prompt:str , role:str): # reconstruct prompt to suitable 
        pass


    
