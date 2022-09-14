from typing_extensions import Self
from pydantic import BaseModel

from app.db.database import database
from app.db.crud_base import CRUD
from app.db.models import main_items
from app.utils import timestamp_minus_day
from app.db.schemas import DateInBase


class MainItemsCrud(CRUD):
    async def get_all_items_in_current_folder(self, folder_id: str):
        query = self.model.select().filter(self.model.c.parentId == folder_id)
        return await self.db.fetch_all(query)


    async def post_many_items(self, items_list: list[BaseModel]):
        query = self.model.insert()
        values = [item.dict() for item in items_list]
        return await self.db.execute_many(query=query, values=values)


    async def update_many_items(self, items_list: list[BaseModel]):
        n = len(items_list)
        updated_items_id = ['' for i in range(n)]
        for idx in range(n):
            query = (
                self.model
                .update()
                .filter(self.model.c.id == items_list[idx].id)
                .values(**items_list[idx].dict())
                .returning(self.model.c.id)
            )
            updated_items_id[idx] = await self.db.execute(query=query)
        return updated_items_id


    async def check_existing_items(self, list_ids: list[str]):
        query = self.model.select().filter(self.model.c.id.in_(list_ids))
        return await self.db.fetch_all(query=query)
    
    async def get_items_by_date(self, date: int):
        date_minus_day = timestamp_minus_day(date)
        query = self.model.select().filter(self.model.c.date <= date).filter(self.model.c.date >= date)
        return await self.db.fetch_all(query=query)

        

main_items_crud = MainItemsCrud(db=database, model=main_items)
