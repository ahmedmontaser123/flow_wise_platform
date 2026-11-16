import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI

from helpers import get_settings
from models.db.connection_database import *
from models.db.flow_wise.schema import Base

from routes.job_router import router as job_router 

app = FastAPI(
    title="FloWise API",
    description="Backend Service for FloWise"
)

app.include_router(job_router)

@app.get("/", tags=["Health Check"])
async def root():
    return {"message": "Welcome to FloWise API! The server is running successfully."}