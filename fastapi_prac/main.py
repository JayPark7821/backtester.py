import logging
from contextlib import asynccontextmanager

from asgi_correlation_id import CorrelationIdMiddleware
from fastapi.exception_handlers import http_exception_handler

from fastapi import FastAPI, HTTPException
from fastapi_prac.database import database
from fastapi_prac.logging_conf import configure_logging
from fastapi_prac.routers.post import router as post_router
from fastapi_prac.routers.user import router as user_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    logger.info("start application <<<<=========")
    await database.connect()
    yield
    await database.disconnect()


app = FastAPI(lifespan=lifespan)

app.include_router(post_router)
app.include_router(user_router)
app.add_middleware(CorrelationIdMiddleware)


@app.exception_handler(HTTPException)
async def http_exception_handle_logger(request, exc):
    logger.error(f"HTTPException: {exc.status_code} - {exc.detail}")
    return await http(request, exc)
