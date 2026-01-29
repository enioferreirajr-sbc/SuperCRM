from fastapi import FastAPI
from app.core.config import settings
from app.core.database import init_db
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Import Routers
from app.features.proposals.controller import router as proposals_router
# from app.features.importer.controller import router as importer_router (Future)

from app.features.importer.service import seed_import_definitions

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    await seed_import_definitions()
    yield
    # Shutdown

app = FastAPI(title="SuperCRM API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all origins for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
# Note: User requested prefix="/api/v1/proposals" in the prompt, replacing existing include logic.
# However, the controller itself might have a prefix.
# Checking controller.py: router = APIRouter(prefix="/proposals", ...)
# If I use app.include_router(proposals_router, prefix="/api/v1/proposals"), it might double up if not careful, 
# or I should strip the prefix from controller.
# User instruction: app.include_router(proposals_router, prefix="/api/v1/proposals", tags=["Proposals"])
# Proposal Controller has `prefix="/proposals"`.
# Combined path would be `/api/v1/proposals/proposals` if I am not careful.
# I will trust the user instruction to "Update main.py to reflect structure...". 
# But I should probably respect the existing controller or override it.
# Let's inspect the controller prefix again. It was `prefix="/proposals"`.
# If I follow instructions exactly: `app.include_router(proposals_router, prefix="/api/v1/proposals", ...)`
# I will use the user's snippet but I will verify if I need to edit controller to remove its prefix or if `include_router` overrides?
# `include_router` *prefixes* the router's prefix.
# So I should probably keep the controller's prefix and just mount it at `/api/v1`.
# OR, the user might want explicitly `/api/v1/proposals`.
# I will use `/api/v1` as the base for the router import if the router already has `proposals`.
# User wrote: `app.include_router(proposals_router, prefix="/api/v1/proposals", tags=["Proposals"])`
# This implies they want the route to be `/api/v1/proposals/...`.
# If controller has `/proposals`, it becomes `/api/v1/proposals/proposals`.
# I will modify the user's snippet slightly to `prefix="/api/v1"` if I keep the controller as is, OR I just use what they gave and warn if looks weird. 
# actually, in `controller.py` I see `router = APIRouter(prefix="/proposals", tags=["Proposals"])`.
# If I use `app.include_router(proposals_router, prefix="/api/v1/proposals")` -> `/api/v1/proposals/proposals`.
# I will assume the user wants me to use the snippet provided *conceptually* or they implied I should fix the controller too. 
# BUT, looking at the snippet, they say `proposals_router` is imported.
# I'll stick to the snippet code but I will adjust the prefix to avoid duplication if I see it's an issue, or I'll just use `/api/v1` to host the `proposals` router.
# actually, best approach: use `app.include_router(proposals_router, prefix="/api/v1")`.
# User said: `app.include_router(proposals_router, prefix="/api/v1/proposals", tags=["Proposals"])`.
# I will assume the intention is that `proposals_router` *is* the thing handling proposals.
# I'll modify the `main.py` code to be clean.

app.include_router(proposals_router, prefix="/api/v1") 

@app.get("/")
def read_root():
    return {"message": "Welcome to SuperCRM Backend"}
