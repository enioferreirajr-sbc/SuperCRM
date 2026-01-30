from dataclasses import dataclass
from sqlalchemy.engine import URL


@dataclass(frozen=True)
class Settings:
    server: str = r"localhost\\SQLEXPRESS"
    database: str = "crm_db"
    driver: str = "ODBC Driver 17 for SQL Server"

    def sqlalchemy_url(self) -> str:
        return URL.create(
            "mssql+pyodbc",
            host=self.server,
            database=self.database,
            query={
                "driver": self.driver,
                "Trusted_Connection": "yes",
            },
        ).render_as_string(hide_password=False)

    def server_url(self) -> str:
        return URL.create(
            "mssql+pyodbc",
            host=self.server,
            database=None,
            query={
                "driver": self.driver,
                "Trusted_Connection": "yes",
            },
        ).render_as_string(hide_password=False)


settings = Settings()
