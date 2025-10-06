from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+psycopg2://ledger:ledger@localhost:5432/ledgerdb"
    APP_NAME: str = "FinBuddy Pipeline API"

settings = Settings()
