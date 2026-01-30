from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.database import init_db
from app.api.health import router as health_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(health_router)
