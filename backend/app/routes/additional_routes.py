from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.db.main_items_crud import main_items_crud
from app.db.history_of_item_crud import history_of_item_crud
from app.db.schemas import (
    ItemHistoryResponse, ItemHistoryUnit, ItemExport
)
from app.utils import isoformat_to_timestamp


responses={
    400: {
        'code': 400,
        'message': 'Validation Failed'
    },
    404: {
        'code': 404,
        'message': 'Item not found'
    }
}

router = APIRouter()


@router.get('/updates')
async def updates(date: str) -> ItemHistoryResponse:
    try:
        date = isoformat_to_timestamp(date)
        _ = await main_items_crud.get_items_by_date(date)
        if _ != []:
            units = [ItemExport.from_orm(node) for node in _]
            return ItemHistoryResponse(items=[ItemHistoryUnit(**unit.dict()) for unit in units])
        return {'items':[]}
    except ValueError:
        return JSONResponse(status_code=400, content=responses[400])
    except Exception:
        raise HTTPException(500)


@router.get('/node/{id}/history')
async def history_node(id: str, dateStart: str, dateEnd: str):
    try:
        dateStart, dateEnd = isoformat_to_timestamp(dateStart), isoformat_to_timestamp(dateEnd)
        _ = await history_of_item_crud.get_history_of_item(id=id, dateFrom=dateStart, dateTo=dateEnd)
        if _ != []:
            units = [ItemExport.from_orm(node) for node in _]
            return ItemHistoryResponse(items=[ItemHistoryUnit(**unit.dict()) for unit in units])
        else:
            raise HTTPException(404)
    except HTTPException as e: 
        return JSONResponse(status_code=e.status_code, content=responses[404])
    except ValueError:
        return JSONResponse(status_code=400, content=responses[400])


# async def _get_folder_size(id: str, item: ItemExport):
#     children, len_children = await _get_all_items_in_current_folder(id=id)
    
#     if len_children != 0:
#         for idx in range(len_children):
#             if children[idx].type == 'FOLDER':
#                 children[idx].children = []
#                 children[idx].children.append(await _get_folder_size(id=children[idx].id, item=children[idx]))

#     item.children = children

#     for idx in range(len_children):
#         item.size += item.children[idx].size

#     return item.size

# async def _get_all_items_in_current_folder(id: str):
#     try:
#         _ = await main_items_crud.get_all_items_in_current_folder(id)
#         children = []
#         len_children = 0
#         for base_item in _:
#             data_item = ItemExport.from_orm(base_item)
#             len_children += 1
#             children.append(data_item)
#         return children, len_children
#     except Exception as e:
#         raise HTTPException(500)
