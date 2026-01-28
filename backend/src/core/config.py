from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import MongoDsn

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore"
    )

    MONGODB_URL: str = "mongodb://localhost:27017" # kept as str to avoid pydantic validation issues with motor if simple generic Dsn
    # OR use MongoDsn and cast to str when using with motor. Let's use string for simplicity or str(MongoDsn)
    # The requirement said MONGODB_URL: MongoDsn. Let's stick to that but handle string conversion if needed.
    # Actually Motor accepts string. Pydantic MongoDsn might need 'str(settings.MONGODB_URL)' usage.
    
    DATABASE_NAME: str = "crm_db"

settings = Settings()
