import sys
import os
import asyncio
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from fastapi.testclient import TestClient
from main import app

# Synchronous test using TestClient
def test_list_proposals():
    print("INFO: Client starting...")
    with TestClient(app) as client:
        print("INFO: Sending GET /proposals/...")
        response = client.get("/proposals/")
        
    print(f"INFO: Response Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"INFO: Retrieved {len(data)} proposals.")
        if len(data) > 0:
            print(f"INFO: Sample: {data[0].get('business_proposal_id')} - {data[0].get('product_name')}")
        else:
            print("INFO: List is empty (expected if DB is empty, but we imported headers before).")
    else:
        print(f"FAILURE: {response.text}")
        sys.exit(1)

if __name__ == "__main__":
    test_list_proposals()
