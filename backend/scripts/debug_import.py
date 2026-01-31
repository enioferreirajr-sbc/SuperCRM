# scripts/debug_import.py

from app.db.session import SessionLocal
from app.core.import_context import ImportContext

def main():
    session = SessionLocal()
    try:
        ctx = ImportContext(session)
        ctx.run("dados.xlsx")
        print("Importação finalizada com sucesso")
    finally:
        session.close()

if __name__ == "__main__":
    main()
