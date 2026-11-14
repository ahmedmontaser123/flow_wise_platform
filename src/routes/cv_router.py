
import os
from fastapi import APIRouter, Depends, UploadFile, Form,status,Request
from fastapi.responses import JSONResponse
from helpers import get_settings,Settings
from controllers import CvController,ProjectController,ProcessController
from models.enums import ResponseSignal
import aiofiles

import logging



cv_router = APIRouter(
    prefix="/api/v1/cv",
    tags=["cv"]
)

@cv_router.post("/upload/{project_id}", response_class=JSONResponse)
async def upload_file(request:Request,project_id:str,file:UploadFile,app_settings:Settings = Depends(get_settings)):

    file_name = file.filename

    is_valid,message = await CvController().validate_cv(file)

    # validation file 
    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content = {"message": message}
        )

    # create path project
    project_path = ProjectController().get_project_path_and_create(project_id=project_id)
    file_path,file_id = await CvController().generate_unique_path(project_id=project_id,original_name=file_name)

    try:
          
       async with aiofiles.open(file_path, 'wb') as f:# write the file to the project path in chunks using aiofiles
           while chunk := await file.read(app_settings.CHUNK_SIZE):
                await f.write(chunk)

    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"signal": ResponseSignal.FILE_UPLOAD_FAILED.value}
        )


    return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content = {"message": message,
                       "file_id":file_id
                                     }
        )


@cv_router.post("/process/{project_id}",response_class=JSONResponse)
async def process_cv(project_id:str,file_id:str):
    # get file path 
    file_content = ProcessController(project_id=project_id).get_text_cv(file_id=file_id)

    # validate file 

    if file_content is None:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"signal": ResponseSignal.FILE_CONTENT_INVALID}
        )
    # go to process file 

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"signal": ResponseSignal.FILE_PROCESSED_SUCCESSFULLY.value, "file_content": file_content}
    )
     

    
    
    


