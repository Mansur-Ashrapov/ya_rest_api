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

    async def get_all(self):
        query = self.model.select()
        return await self.db.fetch_all(query=query)


    async def post(self, payload: BaseModel):
        query = self.model.insert().values(**payload.dict())
        return await self.db.execute(query=query)

    
    async def put(self, payload: BaseModel):
        query = self.model.update().where(payload.id == self.model.c.id).values(**payload.dict()).returning(self.model.c.id)
        return await self.db.execute(query=query)
    

    async def delete(self, item_id):
        query = self.model.delete().where(self.model.c.id.in_([item_id]))
        return await self.db.execute(query=query)
