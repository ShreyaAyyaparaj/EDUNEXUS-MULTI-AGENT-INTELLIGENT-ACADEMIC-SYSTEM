import os
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = "C:/Users/shreya/Desktop/educamp"
DB_PATH = f"{ROOT_DIR}/database/edunexus.db"
CHROMA_PATH = f"{ROOT_DIR}/database/chroma_db"

class Settings(BaseSettings):
    PROJECT_NAME: str = "EduNexus Academic Decision-Support System"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = "edunexus_super_secret_jwt_key_change_in_production_2026"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    DATABASE_URL: str = f"sqlite:///{DB_PATH}"
    GEMINI_API_KEY: str = ""
    CHROMA_PERSIST_DIR: str = CHROMA_PATH

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
