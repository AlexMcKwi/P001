import os
from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # --- Application ---
    APP_NAME: str = "Python API"
    APP_ENV: str = Field(default="development")  # development | production

    # --- Database ---
    POSTGRES_USER: str = Field(default="postgres")
    POSTGRES_PASSWORD: str = Field(default="maxou")
    POSTGRES_DB: str = Field(default="dbP001")
    POSTGRES_HOST: str = Field(default="db")
    POSTGRES_PORT: int = Field(default=5432)

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql://{self.POSTGRES_USER}:"
            f"{self.POSTGRES_PASSWORD}@"
            f"{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/"
            f"{self.POSTGRES_DB}"
        )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()