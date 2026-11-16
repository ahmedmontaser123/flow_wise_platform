from helpers import get_settings
from models.db.connection_database import *
from models.db.flow_wise.schema import Base
from routes.cv_file_route import router as cv_file_router
from src.routes.candidate_route import router as candidate_router

from fastapi import FastAPI


app = FastAPI(
    title="Flow-wise API",
)
app.include_router(cv_file_router)
app.include_router(candidate_router)

print("Base metadata:", Base)


app_settings = get_settings()
print(app_settings.PGADMIN_DEFAULT_PASSWORD)
print(DATABASE_URL)