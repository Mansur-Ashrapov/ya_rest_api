from asyncpg.exceptions import NoDataFoundError, UniqueViolationError
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.db.main_items_crud import main_items_crud
from app.db.history_of_item_crud import history_of_item_crud
from app.db.schemas import (
    ItemImportRequest, ItemImportInBase, ItemExport, DateInBase, ItemExportResponse
)


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


@router.post('/imports', status_code=200)
async def create_or_update_item(items_in: ItemImportRequest):
    items = {item.id:item for item in items_in.items}
    date = items_in.updateDate
    
    id_items = []
    id_parents = []
    id_folders = []
    len_items = 0
    len_parents = 0
    for id, item in items.items():
        len_items += 1
        id_items.append(item.id)
        if item.type == 'FOLDER':
            id_folders.append(item.id)
        if item.parent_id != None:
            id_parents.append(item.parent_id)
            len_parents += 1
        if id == item.parent_id:
            return JSONResponse(status_code=400, content=responses[400])

    # проверяем на элементы с одинаковым id
    id_set = list(set(id_items))
    for idx in range(len_items):
        if id_items[idx] not in id_set:
            return JSONResponse(status_code=400, content=responses[400])
    
    # проверяем существование родителей в бд и в запросе
    try:
        id_existings_parents = await _get_existings_parents(id_parents=id_parents)
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content=responses[e.status_code])
    except Exception:
        raise HTTPException(500)

    if id_existings_parents != []:
        id_existings_parents.append([id for id in id_folders])
        for id, item in items.items():
            if item.parent_id not in id_existings_parents:
                return JSONResponse(status_code=400, content=responses[400])

        
    items_schemas = [ItemImportInBase(**item.dict(), date=date) for id, item in items.items()]
 
    try:    
        await main_items_crud.upsert(items_list=items_schemas)
    except UniqueViolationError:
        return JSONResponse(status_code=400, content=responses[400])
    except Exception as e:
        raise HTTPException(500)  

    try:
        # обновляем дату родителей 
        for id in id_parents:
            await _update_date_parents(date=date, id=id)
    except Exception as e:
        raise HTTPException(500)

@router.get('/nodes/{id}')
async def get_nodes(id: str) -> ItemExportResponse:

    try:
        _ = await main_items_crud.get(item_id=id)
        if _ is not None:
            item = ItemExport.from_orm(_)
        else: 
            return JSONResponse(status_code=404, content=responses[404])
    except Exception as e:
        raise HTTPException(500) 

    children = await _get_children_for_nodes(id=item.id, item=item)

    return ItemExportResponse(**children.dict())


@router.delete('/delete/{id}')
async def delete_node(id: str, date: str):
    dateIn = DateInBase(date=date)
    try:
        _ = await main_items_crud.get(id)
        if _ is not None:
            if _.type == "FOLDER":
                children = await _get_children_for_delete(_.id)
                for child in children:
                    await main_items_crud.delete(child.id)
            
            # обновляем дату родителей 
            if _.parent_id is not None:
                await _update_date_parents(dateIn, _.parent_id)

            await main_items_crud.delete(id)
        else:
            raise NoDataFoundError
    except NoDataFoundError:
        return JSONResponse(status_code=404, content=responses[404])
    except Exception as e:
        raise HTTPException(500) 

# функция для получения ветки родителей
async def _get_all_parents(id: str):
    try:
        parents = []
        all_finded = False
        parent_id = id
        while all_finded == False:
            _ = await main_items_crud.get(parent_id)
            if _ is None:
                all_finded = True
            else:
                parents.append(ItemImportInBase.from_orm(_))
                parent_id = _.parent_id
        return parents
    except Exception as e:
        raise HTTPException(500)


async def _get_existings_parents(id_parents: list[str]):
    existings_parents = await main_items_crud.check_existing_items(list_ids=id_parents)
    id_existings_parents = []
    for exist_parent in existings_parents:
        id_existings_parents.append(exist_parent.id)
        if 'FILE' == exist_parent.type:
            raise HTTPException(400)
    return id_existings_parents


async def _get_children_for_delete(id):
    children, len_children = await _get_all_items_in_current_folder(id=id)
    
    if len_children != 0:
        for child in children:
            if child.type == 'FOLDER':
                children_for_that_child = await _get_children_for_delete(child.id)
                for _ in children_for_that_child:
                    children.append(ItemExportResponse.from_orm(_))

    return children


async def _get_children_for_nodes(id: str, item: ItemExport):
    children, len_children = await _get_all_items_in_current_folder(id=id)
    
    if len_children != 0:
        for idx in range(len_children):
            if children[idx].type == 'FOLDER':
                children[idx].children = []
                children[idx].children.append(await _get_children_for_nodes(id=children[idx].id, item=children[idx]))

    item.children = children

    for idx in range(len_children):
        item.size += item.children[idx].size

    return item


async def _update_date_parents(date, id):
    all_parents_for_that_node = await _get_all_parents(id)
    for parent in all_parents_for_that_node:
        parent.date = date
    await main_items_crud.upsert(all_parents_for_that_node)

async def _get_all_items_in_current_folder(id: str):
    try:
        _ = await main_items_crud.get_all_items_in_current_folder(id)
        children = []
        len_children = 0
        for base_item in _:
            data_item = ItemExport.from_orm(base_item)
            len_children += 1
            children.append(data_item)
        return children, len_children
    except Exception as e:
        raise HTTPException(500)
