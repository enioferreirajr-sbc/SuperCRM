import sys
import os
import asyncio
from pprint import pprint
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.core.database import init_db
from src.modules.proposals.models import BusinessProposal

async def raw_fetch():
    await init_db()
    # Access collection directly
    coll = BusinessProposal.get_pymongo_collection()

    doc = await coll.find_one()
    print("Raw Document:")
    pprint(doc)
    
    if doc:
        lic = doc.get('license_of_use')
        print(f"License type: {type(lic)}")

if __name__ == "__main__":
    asyncio.run(raw_fetch())
