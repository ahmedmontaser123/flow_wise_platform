import os 
from .Base_controller import BaseController
from .project_controller import ProjectController
from models.enums import FileContent
from langchain_community.document_loaders import PyMuPDFLoader
import re
import unicodedata



class ProcessController(BaseController):

    def __init__(self , project_id:str):
        super().__init__()
        self.project = project_id
        self.project_path = ProjectController().get_project_path(project_id = project_id)


    def get_file_extension(self, file_path:str):
        return os.path.splitext(file_path)[-1]

    def get_file_loader(self, file_id:str):

        file_ext = self.get_file_extension(file_id)
        if self.project_path is None:
            return None
        file_path = os.path.join(self.project_path, file_id)


        if file_ext == FileContent.PDF.value:
            return PyMuPDFLoader(file_path)

        else:
            return None

    def clean_link(self,match):
        label = match.group(1).strip()
        url = match.group(2).strip()

        if url.lower().startswith("mailto:"):
           return url[7:]

        if label.rstrip("/") == url.rstrip("/"):
           return url

        return f"{label}: {url}"

    def preprocess_cv_text(self,text: str) -> str:

        if not isinstance(text, str):
           raise TypeError("CV text must be a string")

        # 1. Normalize Unicode
        text = unicodedata.normalize("NFKC", text)

        # 2. Remove null and invisible formatting characters
        text = text.replace("\x00", "")
        text = re.sub(r"[\u200b\u200c\u200d\ufeff]", "", text)

        # 3. Normalize line endings
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        # 4. Preserve Markdown link destinations
        text = re.sub(
            r"\[([^\]]+)\]\(([^)]+)\)",
            self.clean_link,
            text
        )

        # 5. Remove common Markdown heading markers
        text = re.sub(
            r"(?m)^[ \t]{0,3}#{1,6}[ \t]+",
            "",
            text
        )

        # 6. Normalize bullet characters
        text = re.sub(
            r"(?m)^[ \t]*[•●▪◦][ \t]*",
            "- ",
            text
        )

        # 7. Normalize horizontal whitespace
        text = re.sub(r"[ \t]+", " ", text)

        # 8. Remove unnecessary spaces around line breaks
        text = re.sub(r" *\n *", "\n", text)

        # 9. Reduce excessive empty lines
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()

    def get_text_cv(self, file_id: str) -> str:
        loader = self.get_file_loader(file_id)

        if loader is None:
            return None 

        docs = loader.load()

        text = docs[0].page_content if docs else ""

        # preprocess the text 

        cleaned_text = self.preprocess_cv_text(text)

        return cleaned_text









