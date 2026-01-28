import asyncio
import sys
sys.path.append('.')
from src.core.database import init_db
from src.modules.proposals.models import BusinessProposal

async def reset():
    await init_db()
    print("Deleting all BusinessProposals...")
    await BusinessProposal.find_all().delete()
    print("Deleted.")

if __name__ == "__main__":
    asyncio.run(reset())
