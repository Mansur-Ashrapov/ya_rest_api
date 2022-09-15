from pydantic import BaseModel

from app.db.database import database
from app.db.crud_base import CRUD
from app.db.models import main_items
from app.utils import timestamp_minus_day


class MainItemsCrud(CRUD):
    async def get_all_items_in_current_folder(self, folder_id: str):
        query = self.model.select().filter(self.model.c.parent_id == folder_id)
        return await self.db.fetch_all(query)

    async def upsert(self, items_list: list[BaseModel]):
        values = [item.dict() for item in items_list]
        query = (
            "INSERT INTO main_items (id, url, date, parent_id, size, type) "
            "VALUES (:id, :url, :date, :parent_id, :size, :type) "
            "ON CONFLICT (id) DO UPDATE " 
            "SET url = excluded.url,"
            "date = excluded.date,"
            "parent_id = excluded.parent_id,"
            "size = excluded.size,"
            "type = excluded.type"
        )
        return await database.execute_many(query=query, values=values)

    async def check_existing_items(self, list_ids: list[str]):
        query = self.model.select().filter(self.model.c.id.in_(list_ids))
        return await self.db.fetch_all(query=query)
    
    async def get_items_by_date(self, date: int):
        date_minus_day = timestamp_minus_day(date)
        query = self.model.select().filter(self.model.c.date >= date_minus_day).filter(self.model.c.date <= date)
        return await self.db.fetch_all(query=query)

        

main_items_crud = MainItemsCrud(db=database, model=main_items)
