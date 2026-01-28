from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.core.database import init_db
from src.modules.proposals.controller import router as proposals_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown (if needed) works here too

app = FastAPI(title="SuperCRM API", lifespan=lifespan)

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(proposals_router)

@app.get("/")
def read_root():
    return {"message": "Welcome to SuperCRM Backend"}
