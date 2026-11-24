
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from sqlalchemy import text

from models.db.connection_database import engine
from routes import hr_auth_router

logger = logging.getLogger(__name__)


app = FastAPI()

app.include_router(hr_auth_router)