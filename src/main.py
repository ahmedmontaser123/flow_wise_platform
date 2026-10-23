from fastapi import FastAPI
from helpers import get_settings
from models.db.connection_database import *
from models.db.flow_wise.schema import Base
from routes import cv_router

app = FastAPI()

app.include_router(cv_router)

