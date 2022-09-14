import sqlalchemy
import databases 

from app.settings import config


database = databases.Database(config.DATABASE_URL)

metadata = sqlalchemy.MetaData()

engine = sqlalchemy.create_engine(
    config.DATABASE_URL,
)
