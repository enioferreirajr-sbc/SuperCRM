import pyodbc

def test_pyodbc_connection():
    connection_string = (
        "Driver={ODBC Driver 17 for SQL Server};"
        "Server=localhost\\SQLEXPRESS;"
        "Trusted_Connection=yes;"
        "TrustServerCertificate=yes;"
    )

    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    cursor.execute("SELECT 1")
    result = cursor.fetchone()

    print("pyodbc connection OK:", result)

    cursor.close()
    conn.close()

if __name__ == "__main__":
    test_pyodbc_connection()
