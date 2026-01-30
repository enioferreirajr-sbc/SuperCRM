from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core import database
from app.core.mapping_service import ensure_active_mapping
from app.api.imports import router as imports_router
from app.api.proposals import router as proposals_router
from app.api.health import router as health_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    database.init_db()
    if database.engine is None:
        raise RuntimeError("Database engine is not initialized.")
    ensure_active_mapping(database.engine)
    yield


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(health_router)
app.include_router(imports_router)
app.include_router(proposals_router)
