from fastapi import FastAPI
from helpers import get_settings
from models.db.connection_database import *
from models.db.flow_wise.schema import Base
from routes import cv_router
from routes.hr_auth_router import hr_auth_router
from routes.hr_admin_router import hr_admin_router
from routes.hr_member_router import hr_member_router

app = FastAPI()

app.include_router(cv_router)
app.include_router(hr_auth_router)
app.include_router(hr_admin_router)
app.include_router(hr_member_router)

