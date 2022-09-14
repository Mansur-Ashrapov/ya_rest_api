from this import s
from asyncpg.exceptions import UndefinedColumnError, DuplicateColumnError, NoDataFoundError, UniqueViolationError
from fastapi import APIRouter, HTTPException

from app.db.main_items_crud import main_items_crud
from app.db.history_of_item_crud import history_of_item_crud
from app.db.schemas import (
    ItemImportRequest, ItemImportInBase, ItemExport, ItemExportResponse, DateInBase
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

router = APIRouter(responses=responses)


@router.post('/imports', status_code=200)
async def create_or_update_item(items_in: ItemImportRequest):
    items = items_in.items
    date = items_in.updateDate


    id_items = []
    len_items = 0
    url_items = []
    id_parents = []
    id_items_with_parents = []
    type_parents = []
    len_parents = 0
    for item in items:
        id_items.append(item.id) 
        url_items.append(item.url)
        len_items += 1
        if item.parentId != None:
            id_parents.append(item.parentId)
            id_items_with_parents.append(item.id)
            type_parents.append(item.type)
            len_parents += 1

    # проверяем на элементы с одинаковым id и с одинаковыми url
    id_set = list(set(id_items))
    url_set = list(set(url_items))

    for idx in range(len_items):
        if id_items[idx] not in id_items or url_items[idx] not in url_set:
            raise HTTPException(400, detail='50')


    # проверяем наличие родителей в бд и в запросе
    try:
        existings_parents = await main_items_crud.check_existing_items(list_ids=id_parents)
        
        id_existings_parents = []
        type_existings_parents = []
        for exist_parent in existings_parents:
            id_existings_parents.append(exist_parent.id)
            type_existings_parents.append(exist_parent.type)
        if 'FILE' in type_existings_parents:
            raise HTTPException(400, detail='64')
    except UndefinedColumnError:
        id_existings_parents = None
    except HTTPException as e:
        raise HTTPException(400, detail=e.detail)
    except Exception as e:
        raise Exception(e, '78')

    for idx in range(len_parents):
        if (id_parents[idx] not in id_existings_parents and id_parents[idx] not in id_items and id_parents[idx] not in id_items_with_parents):
            raise HTTPException(400, detail='74')
        
    # выбираем существующие item в базе для последующего обновления
    try:
        id_items_to_update = await main_items_crud.check_existing_items(list_ids=id_items)
        id_items_to_update = [item.id for item in id_items_to_update]
    except UndefinedColumnError:
        id_items_to_update = None
    except Exception as e:
        raise Exception(e, '91')
        
    # разделяем записи на те которые обновляются и на те которые создаются
    items_to_create = [ItemImportInBase(**item.dict(), date=date) for item in items if item.id not in id_items_to_update]
    items_to_update = [ItemImportInBase(**item.dict(), date=date) for item in items if item.id in id_items_to_update] 
    items_to_create = items_to_create if items_to_create != [] else None
    items_to_update = items_to_update if items_to_update != [] else None

    

    try:    
        if items_to_create != None:
            await main_items_crud.post_many_items(items_to_create)
        if items_to_update != None:
            await main_items_crud.update_many_items(items_to_update)
        
        # обновляем дату родителей 
        for id in id_parents:
            all_parents_for_that_id = await _get_all_parents(id)
            for parent in all_parents_for_that_id:
                parent.date = date
            await main_items_crud.update_many_items(all_parents_for_that_id)
            await history_of_item_crud.post_many_items(all_parents_for_that_id)
            

    except DuplicateColumnError:
        raise HTTPException(400, detail='97')
    except UniqueViolationError:
        raise HTTPException(400, detail='98')
    except Exception as e:
        raise Exception(e, '120')
    finally:
        if items_to_create != None:
            await history_of_item_crud.post_many_items(items_to_create)
        if items_to_update != None:
            await history_of_item_crud.post_many_items(items_to_update)


@router.get('/nodes/{id}')
async def get_nodes(id: str) -> ItemExportResponse:

    try:
        _ = await main_items_crud.get(item_id=id)
        if _ is not None:
            item = ItemExportResponse.from_orm(_)
        else: 
            raise HTTPException(404)
    except TypeError as e:
        raise Exception(e)
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail, headers=e.headers)
    except Exception as e:
        raise Exception(e)

    children = await _get_children_for_nodes(id=item.id, item=item)

    return children


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
            if _.parentId is not None:
                all_parents_for_that_node = await _get_all_parents(_.parentId)
                for parent in all_parents_for_that_node:
                    parent.date = dateIn
                await main_items_crud.update_many_items(all_parents_for_that_node)

            await main_items_crud.delete(id)
        else:
            raise NoDataFoundError
    except NoDataFoundError:
        raise HTTPException(404)
    except Exception as e:
        raise Exception(e, '159')


async def _get_all_parents(id: str):
    try:
        parents = []
        all_finded = False
        parent_id = id
        while all_finded == False:
            _ = await main_items_crud.get(parent_id)
            parents.append(ItemImportInBase.from_orm(_))
            if _.parentId is None:
                all_finded = True
            else:
                parent_id = _.parentId
        return parents
    except Exception:
        raise HTTPException(500)



async def _get_children_for_delete(id):
    try:
        _ = await main_items_crud.get_all_items_in_current_folder(id)
        children = []
        len_children = 0
        for base_item in _:
            data_item = ItemImportInBase.from_orm(base_item)
            len_children += 1
            children.append(data_item)
    except TypeError as e:
        raise Exception(e)
    except Exception as e:
        raise HTTPException(e)
    
    if len_children != 0:
        for child in children:
            if child.type == 'FOLDER':
                children_for_that_child = await _get_children_for_delete(child.id)
                for _ in children_for_that_child:
                    children.append(ItemImportInBase.from_orm(_))

    return children


async def _get_children_for_nodes(id: str, item: ItemExportResponse):
    try:
        _ = await main_items_crud.get_all_items_in_current_folder(id)
        children = []
        len_children = 0
        for base_item in _:
            data_item = ItemExportResponse.from_orm(base_item)
            len_children += 1
            children.append(data_item)
    except TypeError as e:
        raise Exception(e)
    except Exception as e:
        raise HTTPException(e)

    if len_children != 0:
        for idx in range(len_children):
            if children[idx].type == 'FOLDER':
                children[idx].children = []
                children[idx].children.append(await _get_children_for_nodes(id=children[idx].id, item=children[idx]))

    item.children = children

    for idx in range(len_children):
        item.size += item.children[idx].size

    return item
