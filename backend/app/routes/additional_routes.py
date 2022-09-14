from platform import node
from fastapi import APIRouter

from app.db.schemas import DateInBase
from app.db.main_items_crud import main_items_crud
from app.db.history_of_item_crud import history_of_item_crud
# from app.db.history_of_item_crud
from app.db.schemas import (
    ItemHistoryUnit, ItemHistoryResponse
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

router = APIRouter(responses=responses)

@router.get('/updates')
async def updates(date: str) -> ItemHistoryResponse:
    try:
        date = isoformat_to_timestamp(date)
        _ = await main_items_crud.get_items_by_date(date)
        nodes = ItemHistoryResponse(items=[node for node in _])
        return nodes
    except Exception as e:
        raise Exception(e)

@router.get('/node/{id}/history')
async def history_node(id: str, dateStart: str, dateEnd: str):
    # try:
    dateStart, dateEnd = isoformat_to_timestamp(dateStart), isoformat_to_timestamp(dateEnd)
    _ = await history_of_item_crud.get_history_of_item(id=id, dateFrom=dateStart, dateTo=dateEnd)
    nodes = ItemHistoryResponse(items=[node for node in _])
    return nodes
