import sys
from fastapi.testclient import TestClient
# Add src to path if needed, assuming running from backend root
sys.path.append('.') 
from main import app

def test():
    print("INFO: Client starting...")
    with TestClient(app) as client:
        print("INFO: Testing Metadata...")
        response = client.get("/proposals/metadata")
        
        if response.status_code != 200:
            print(f"FAIL: Metadata status {response.status_code}")
            print(response.text)
            sys.exit(1)
            
        data = response.json()
        print("INFO: Metadata Keys:", data.keys())
        # Check integrity
        if not isinstance(data.get('products'), list):
             print("FAIL: Products is not a list")
             sys.exit(1)

        print(f"INFO: Products ({len(data['products'])}): {data['products'][:3]}")
        print(f"INFO: Statuses ({len(data['statuses'])}): {data['statuses']}")
        
        print("INFO: Testing Filter (Product)...")
        if data['products']:
            prod = data['products'][0]
            # Test filter param - note: controller expects 'product' as list query, simple getparam works
            r = client.get(f"/proposals/?product={prod}")
            print(f"INFO: Filter by product '{prod}': Found {len(r.json())} items")
            if r.status_code != 200:
                print(f"FAIL: Filter status {r.status_code}")

        print("SUCCESS.")

if __name__ == "__main__":
    test()
