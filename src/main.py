from fastapi import FastAPI
from helpers import get_settings
from models.db.connection_database import *
from models.db.flow_wise.schema import Base
from stores.LLM  import LLMProviderFactory
from routes import cv_router

import logging

logger = logging.getLogger(__name__)





app = FastAPI()

app.generation_client = None


async def startup_event():

    settings = get_settings()
    app.generation_client = None

    try:
        llm_provider_factory = LLMProviderFactory(settings)
        generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)

        if generation_client is None:
            logger.error(
                "Unknown generation backend: %s", settings.GENERATION_BACKEND
            )
            return

        generation_client.set_generation_model(settings.HUGGINGFACE_MODEL_NAME)
        app.generation_client = generation_client

    except Exception:
        app.generation_client = None
        logger.exception("Generation model could not be loaded")

    print("Application started")



app.router.on_startup.append(startup_event)

app.include_router(cv_router)