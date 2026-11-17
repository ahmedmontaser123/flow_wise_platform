from enum import Enum

class ResponseSignal(str,Enum):
    FILE_TYPE_NOT_ALLOWED = "file type is not allowed"
    FILE_TOO_LARGE = "file size is too larg"
    FILE_SIZE_NOT_EXIST = "file size is not exist"
    FILE_UPLOADED_SUCCESSFULLY = "file uploaded successfully"
    FILE_CONTENT_EMPTY = "file content is empty"
    FILE_CONTENT_INVALID = "file content invalid"
    FILE_CONTENT_IMAGE_ONLY = "file content has image"
    FILE_UPLOAD_FAILED = "file uploaded failed"
    FILE_PROCESSED_SUCCESSFULLY = "file processed successfully"
    FILE_PARSED_SUCCESSFULLY = "file parsed successfully"
    FILE_PARSING_FAILED = "file parsing failed"
    MODEL_NOT_AVAILABLE = "generation model is not available"
    INVALID_FILE_ID = "invalid file id"
      