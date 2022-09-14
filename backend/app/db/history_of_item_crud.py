from pydantic import BaseModel

from app.db.crud_base import CRUD
from app.db.database import database
from app.db.models import history_of_item


class HistoryOfItemCrud(CRUD):
    
    async def get_history_of_item(self, id: str, dateFrom: int, dateTo: int):
        query = self.model.select().filter(self.model.c.id.in_([id])).filter(self.model.c.date <= dateTo).filter(self.model.c.date >= dateFrom)
        return await self.db.fetch_all(query=query)

    async def post_many_items(self, items_list: list[BaseModel]):
        query = self.model.insert()
        values = [item.dict() for item in items_list]
        return await self.db.execute_many(query=query, values=values)


history_of_item_crud = HistoryOfItemCrud(db=database, model=history_of_item)
