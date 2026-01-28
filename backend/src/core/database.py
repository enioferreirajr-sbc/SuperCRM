from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from src.core.config import settings

from src.modules.proposals.models import BusinessProposal, BusinessProposalItem

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
            BusinessProposal,
            BusinessProposalItem
        ], 
    )
