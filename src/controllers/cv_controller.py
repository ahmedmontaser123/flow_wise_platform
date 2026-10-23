from .Base_controller import BaseController
from models.enums import FileContent, ResponseSignal
from .project_controller import ProjectController
from fastapi import UploadFile
from langchain_community.document_loaders.parsers import PyMuPDFParser
from langchain_core.documents.base import Blob
import pymupdf
import re
import os


class CvController(BaseController):

    def __init__(self):
        super().__init__()
        self.scale_size = 1024 * 1024

    def validate_file_metadata(self, file: UploadFile):

        # Validate file type
        if file.content_type != FileContent.FILE_EXTENSION_PDF.value:
            return False, ResponseSignal.FILE_TYPE_NOT_ALLOWED.value

        # Validate file size
        if file.size is None:
            return False, ResponseSignal.FILE_SIZE_NOT_EXIST.value

        if file.size == 0:
            return False, ResponseSignal.FILE_CONTENT_EMPTY.value

        if file.size > FileContent.FILE_SIZE.value * self.scale_size:
            return False, ResponseSignal.FILE_TOO_LARGE.value

        return True, ResponseSignal.FILE_UPLOADED_SUCCESSFULLY.value

    async def validate_file_content(self, file: UploadFile):

        content = await file.read()
        await file.seek(0)

        try:
            # Check if PDF contains images
            with pymupdf.open(stream=content, filetype="pdf") as pdf:
                has_images = any(
                    page.get_image_info()
                    for page in pdf
                )

                extracted_text = "\n".join(
                       page.get_text() for page in pdf
                    ).strip()

            if has_images:
               return False, ResponseSignal.FILE_CONTENT_IMAGE_ONLY.value


            if not extracted_text:
               return False, ResponseSignal.FILE_CONTENT_EMPTY.value

            
        except Exception:
            return False, ResponseSignal.FILE_CONTENT_INVALID.value

        

        return True, ResponseSignal.FILE_UPLOADED_SUCCESSFULLY.value



    async def validate_cv(self, file: UploadFile):

            is_valid, message = self.validate_file_metadata(file)

            if not is_valid:
                return False, message

            is_valid, message = await self.validate_file_content(file)

            if not is_valid:
                return False, message

            return True, ResponseSignal.FILE_UPLOADED_SUCCESSFULLY.value
    

    async def generate_unique_path(self,original_name,project_id):
        # generate random key 
        random_key = self.generate_random_key()
        # get file in project
        project_path = ProjectController().get_project_path(project_id=project_id)

        # clean file name 
        cleaned_file_name = self.clean_file_name(original_name)

        # make join if path exist
        new_file_path = os.path.join(
            project_path,
            random_key + "_" + cleaned_file_name
        )


        #if same cv passed again 
        while os.path.exists(new_file_path):
            random_key = self.generate_random_key()
            new_file_path = os.path.join(
                project_path,
                random_key + "_" + cleaned_file_name
            )

        return new_file_path , random_key + "_" + cleaned_file_name



    def clean_file_name(self, file_name):
       # remove any special characters except . and underscore from the file name using regex
       return re.sub(r'[^\w.]', '_', file_name)

