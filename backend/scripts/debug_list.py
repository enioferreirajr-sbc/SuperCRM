import sys
import os
import asyncio
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.core.database import init_db
from src.modules.proposals.models import BusinessProposal

async def debug_fetch():
    await init_db()
    
    props = await BusinessProposal.find_all().limit(1).to_list()
    if not props:
        print("No proposals found.")
        return

    props = await BusinessProposal.find_all().to_list()
    if not props:
        print("No proposals found.")
        return

    print(f"Check {len(props)} proposals.")
    for p in props:
        print(f"Checking ID: {p.business_proposal_id}")
        try:
            data = p.model_dump()
            # print("Model dump success.")
        except Exception as e:
            print(f"FAILED ID {p.business_proposal_id}: {e}")
            import traceback
            traceback.print_exc()
            return

    print("ALL OK.")

if __name__ == "__main__":
    asyncio.run(debug_fetch())
