from pydantic import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str


config = Settings()
