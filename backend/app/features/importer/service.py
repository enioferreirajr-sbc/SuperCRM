import json
import os
from typing import List
from app.features.importer.models import ImportDefinition

async def seed_import_definitions():
    """
    Seeds the import_definitions collection from the JSON fixture if empty.
    """
    # Check if empty
    count = await ImportDefinition.count()
    if count > 0:
        print("INFO: ImportDefinition collection already populated. Skipping seed.")
        return

    # Path to fixture
    # We are in src/modules/importer/service.py
    # Fixtures are in src/modules/importer/fixtures/
    base_dir = os.path.dirname(os.path.abspath(__file__))
    fixture_path = os.path.join(base_dir, "fixtures", "import_definitions.json")
    
    if not os.path.exists(fixture_path):
        print(f"WARNING: Fixture file not found at {fixture_path}")
        return

    try:
        with open(fixture_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        if not data:
            print("WARNING: Import definitions fixture is empty.")
            return

        # Convert simple list of dicts to ImportDefinition objects
        definitions = [ImportDefinition(**item) for item in data]
        
        await ImportDefinition.insert_many(definitions)
        print(f"INFO: Successfully seeded {len(definitions)} import definitions.")
        
    except Exception as e:
        print(f"ERROR: Failed to seed import definitions: {e}")
