import asyncio
import sys
import os

# Add the backend directory to sys.path to allow imports from src
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from motor.motor_asyncio import AsyncIOMotorClient
from src.core.config import settings
from pymongo.errors import ServerSelectionTimeoutError

async def main():
    print("INFO:    Loading environment configuration...")
    print(f"INFO:    Attempting connection to MongoDB at {settings.MONGODB_URL}...")
    
    try:
        client = AsyncIOMotorClient(str(settings.MONGODB_URL), serverSelectionTimeoutMS=5000)
        # Force a connection verification
        await client.server_info()
        print(f"SUCCESS: ✅ Connected to MongoDB. Database target: {settings.DATABASE_NAME}")
        sys.exit(0)
    except ServerSelectionTimeoutError:
        print(f"ERROR:   ❌ Could not connect to MongoDB at {settings.MONGODB_URL}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR:   ❌ An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        if sys.platform == 'win32':
             asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
