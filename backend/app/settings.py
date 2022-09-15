from pydantic import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = 'postgresql://user_db:pswd_db@0.0.0.0:5432/dev'


config = Settings()
