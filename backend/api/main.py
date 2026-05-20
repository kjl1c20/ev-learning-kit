import logging

from fastapi import FastAPI

from backend.api.routes import router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)

app = FastAPI(
    title="EV Learning Kit API",
    description="RAG-powered API for answering EV technical questions.",
    version="1.0.0",
)

app.include_router(router, prefix="/api/v1")
