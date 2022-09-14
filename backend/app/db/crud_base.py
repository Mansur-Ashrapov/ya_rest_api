import databases
import sqlalchemy

from pydantic import BaseModel


class CRUD():
    def __init__(self, db: databases.Database, model: sqlalchemy.Table) -> None:
        self.db = db
        self.model = model

    async def get(self, item_id):
        query = self.model.select().where(self.model.c.id.in_([item_id]))
        return await self.db.fetch_one(query=query)

    async def delete(self, item_id):
        query = self.model.delete().where(self.model.c.id.in_([item_id]))
        return await self.db.execute(query=query)
