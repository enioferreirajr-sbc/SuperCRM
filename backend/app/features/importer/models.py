from typing import Literal
from beanie import Document, Indexed

class ImportDefinition(Document):
    source_column: str
    target_field: Indexed(str, unique=True)
    target_location: Literal["root", "items"] # Validação estrita
    data_type: Literal["Int", "String", "Date", "Decimal"]
    required: bool = False
    is_unique_identifier: bool = False

    class Settings:
        name = "import_definitions"

