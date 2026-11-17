from enum import Enum

class LLMType(Enum):
    GROQ = "groq"
    HUGGINGFACE = "huggingface"
    COHERE = "cohere"

class RoleGroqEnum(str,Enum):
   SYSTEM = "system",
   USER = "user"


class RoleCohereEnum(str,Enum):
    USER = "USER"
    CHATBOT = "CHATBOT"
