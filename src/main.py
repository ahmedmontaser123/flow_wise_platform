
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from sqlalchemy import text

from models.db.connection_database import engine
from routes import *

logger = logging.getLogger(__name__)


app = FastAPI()

app.include_router(hr_auth_router)
app.include_router(hr_admin_router)
app.include_router(hr_member_router)
app.include_router(candidate_apply_router)
app.include_router(candidate_router)
app.include_router(job_router)