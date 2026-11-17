import os 
from helpers import get_settings
import string
import random


class BaseController:

    def __init__(self):
        self.app_settings = get_settings()
        self.base_dir = os.path.dirname(os.path.dirname(__file__)) 
        self.files_dir = os.path.join(
            self.base_dir,
            "assets/files", #files directory  ---> file
        )

    def generate_random_key(self, length=12):
        """Generate a random string of letters and digits."""
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for i in range(length))

