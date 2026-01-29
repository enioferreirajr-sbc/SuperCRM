from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.core.config import settings

from app.features.proposals.models import Proposal
from app.features.importer.models import ImportDefinition

async def init_db():
    # Instantiate the client
    # MONGODB_URL in settings is a pydantic type or string. 
    # If it is MongoDsn, we should convert to str.
    client = AsyncIOMotorClient(str(settings.MONGODB_URL))
    
    # Initialize Beanie
    print("INFO: Initializing Beanie...")
    await init_beanie(
        database=client[settings.DATABASE_NAME],
        document_models=[
            ImportDefinition,
            Proposal
        ], 
    )
