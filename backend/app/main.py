from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core import database
from app.core.mapping_service import ensure_active_mapping
from app.api.health import router as health_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    database.init_db()
    if database.SessionLocal is None:
        raise RuntimeError("Database session factory is not initialized.")
    session = database.SessionLocal()
    try:
        ensure_active_mapping(session)
    finally:
        session.close()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(health_router)
