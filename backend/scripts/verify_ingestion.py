import sys
import os
import pandas as pd
import io

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from fastapi.testclient import TestClient
from main import app
from src.modules.proposals.models import BusinessProposal
from src.core.config import settings
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

# We need to manually initialize DB for direct model access if we want to check DB state
# But TestClient with lifespan should handle app startup (which runs init_db)
# However, to check the DB *after* the request, we might want to connect directly or trust the response.
# Let's trust the response first, and maybe query if possible. 
# Since existing init_db is async, and we are in sync script, we can't easily await beanie calls 
# unless we wrap in asyncio.run, but that conflicts with TestClient's event loop if not careful.
# For now, let's just rely on the Endpoint response.

def test_ingestion():
    
    # Create a dummy Excel file
    data = {
        "Business Proposal ID": [101, 101, 102],
        "Product Name": ["Consulting", "Training", "License"],
        "R$ License of Use": [0, 0, 5000],
        "R$ Total Sales": [1000, 2000, 5000]
    }
    df = pd.DataFrame(data)
    
    # Save to bytes buffer
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False) # Defaults to Sheet1 usually
    buffer.seek(0)
    
    files = {
        "file": ("test.xlsx", buffer, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    }

    print("INFO: Client starting...")
    with TestClient(app) as client:
        print("INFO: Sending POST /proposals/import...")
        response = client.post("/proposals/import", files=files)
        
    print(f"INFO: Response Status: {response.status_code}")
    
    print(f"INFO: Response Status: {response.status_code}")
    print(f"INFO: Response Body: {response.json()}")
    
    if response.status_code == 200:
        json_resp = response.json()
        if json_resp.get("processed_count") == 3:
            print("SUCCESS: ✅ Ingestion processed 3 records.")
        else:
            print(f"FAILURE: ❌ Expected 3 processed, got {json_resp.get('processed_count')}")
            sys.exit(1)
            
        if json_resp.get("status") == "success":
             print("SUCCESS: ✅ Status is success.")
        else:
             print("FAILURE: ❌ Status is not success.")
             sys.exit(1)
    else:
        print("FAILURE: ❌ Endpoint returned error.")
        sys.exit(1)

if __name__ == "__main__":
    # Ensure dependencies are installed (pandas, openpyxl, etc)
    test_ingestion()
