from pydantic import BaseModel, validator, root_validator
from typing import (
    Optional
)

from app.utils import (
    isoformat_to_timestamp, timestamp_to_isoformat
)


class DateInBase(BaseModel):
    date: str|int

    @validator('date')
    def validate(cls, value: str|int):
        if value.__class__ is int:
            return timestamp_to_isoformat(value)
        return isoformat_to_timestamp(value)
    
    class Config:
        from_orm = True


class ItemBase(BaseModel):
    id: str
    type: str   
    parentId: str|None = None
    url: Optional[str] = None
    size: Optional[int] = None
    

class ItemImportInBase(ItemBase):
    date: int

    class Config:
        orm_mode = True

class ItemImport(ItemBase):
    @root_validator
    def validate_type(cls, values):
        type = values.get('type')
        url = values.get('url')
        size = values.get('size')


        if type != 'FILE' and type != 'FOLDER':
            raise ValueError()

        if type == 'FOLDER' and url != None:
            raise ValueError('У папки url должен быть равен null')
        elif type == "FILE" and url == None:
            raise ValueError('У файла url не должен быть равен null')
        elif url is str and len(url) > 255:
            raise ValueError('Количество символов в строке url не должно превышать 255')
        
        if type == 'FOLDER' and size != None:
            raise ValueError('У папки size при иморте должен быть равен null')
        elif type == "FILE" and (size == None or ( size is int and size <= 0)):
            raise ValueError('У файла, size должен быть больше нуля')
        
        return values


class ItemImportRequest(BaseModel):
    items: list[ItemImport]
    updateDate: DateInBase

class ItemExport(ItemBase):

    @validator('size')
    def validate_size(cls, value):
        if value == None:
            return 0
        return value


class ItemExportResponse(ItemExport):
    date: DateInBase
    children: list|None = []

    class Config:
        orm_mode = True


class ItemHistoryUnit(ItemExport):
    date: DateInBase

    class Config:
        from_orm = True


class ItemHistoryResponse(BaseModel):
    items: list[ItemHistoryUnit]

    class Config:
        from_orm = True
    