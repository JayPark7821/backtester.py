import logging
from fastapi import FastAPI, HTTPException
from asgi_correlation_id import CorrelationIdMiddleware
from fastapi.exception_handlers import http_exception_handler
from contextlib import asynccontextmanager
from app.api.WorkQueueRouter import router as patient_router
from app.models import mongodb
from app.LoggingConfig import configure_logging

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    mongodb.connect()
    logger.info("application started")
    yield
    mongodb.close()


app = FastAPI(lifespan=lifespan)
app.add_middleware(CorrelationIdMiddleware, validator=None)
app.include_router(patient_router)


@app.exception_handler(HTTPException)
async def http_exception_handle_logging(request, exc):
    logger.error(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    return await http_exception_handler(request, exc)
