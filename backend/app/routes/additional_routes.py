from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.db.main_items_crud import main_items_crud
from app.db.history_of_item_crud import history_of_item_crud
# from app.db.history_of_item_crud
from app.db.schemas import (
    ItemHistoryResponse
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
            nodes = ItemHistoryResponse(items=[node for node in _]) 
            return nodes
        else: 
            raise HTTPException(404)
    except HTTPException as e: 
        return JSONResponse(status_code=e.status_code, content=responses[404])
    except ValueError:
        return JSONResponse(status_code=400, content=responses[400])


@router.get('/node/{id}/history')
async def history_node(id: str, dateStart: str, dateEnd: str):
    try:
        dateStart, dateEnd = isoformat_to_timestamp(dateStart), isoformat_to_timestamp(dateEnd)
        _ = await history_of_item_crud.get_history_of_item(id=id, dateFrom=dateStart, dateTo=dateEnd)
        if _ is not None:
            nodes = ItemHistoryResponse(items=[node for node in _])
            return nodes
        else:
            raise HTTPException(404)
    except HTTPException as e: 
        return JSONResponse(status_code=e.status_code, content=responses[404])
    except ValueError:
        return JSONResponse(status_code=400, content=responses[400])
