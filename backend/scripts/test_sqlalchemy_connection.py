import urllib.parse
from sqlalchemy import create_engine, text

def test_sqlalchemy_connection():
    params = urllib.parse.quote_plus(
        "Driver={ODBC Driver 17 for SQL Server};"
        "Server=localhost\\SQLEXPRESS;"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )

    engine = create_engine(
        f"mssql+pyodbc:///?odbc_connect={params}",
        echo=True,
        future=True
    )

    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("SQLAlchemy connection OK:", result.scalar())

if __name__ == "__main__":
    test_sqlalchemy_connection()
