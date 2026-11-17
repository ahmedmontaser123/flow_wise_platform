
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI

from helpers import get_settings
from models.db.connection_database import *
from models.db.flow_wise.schema import Base

from routes.cv_file_route import router as cv_file_router
from routes.candidate_route import router as candidate_router
from routes.job_router import router as job_router

from routes import cv_router
from routes.hr_auth_router import hr_auth_router
from routes.hr_admin_router import hr_admin_router
from routes.hr_member_router import hr_member_router


app = FastAPI(
    title="FloWise API",
    description="Backend Service for FloWise"
)

# CV & Candidate
app.include_router(cv_file_router)
app.include_router(candidate_router)
app.include_router(cv_router)

# HR
app.include_router(hr_auth_router)
app.include_router(hr_admin_router)
app.include_router(hr_member_router)

# Jobs
app.include_router(job_router)


@app.get("/", tags=["Health Check"])
async def root():
    return {
        "message": "Welcome to FloWise API! "
                   "The server is running successfully."
    }
