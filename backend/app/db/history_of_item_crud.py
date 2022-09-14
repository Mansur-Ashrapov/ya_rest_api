from pydantic import BaseModel

from app.db.crud_base import CRUD
from app.db.database import database
from app.db.models import history_of_item


class HistoryOfItemCrud(CRUD):
    
    async def get_history_of_item(self, id: str, dateFrom: int, dateTo: int):
        query = self.model.select().filter(self.model.c.id.in_([id])).filter(self.model.c.date <= dateTo).filter(self.model.c.date >= dateFrom)
        return await self.db.fetch_all(query=query)


history_of_item_crud = HistoryOfItemCrud(db=database, model=history_of_item)
