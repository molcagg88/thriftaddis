from db.models import ItemCreate, Item, ItemUpdate, DelItem
from fastapi import HTTPException 
from sqlmodel import select, and_
from sqlalchemy.orm import selectinload
from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession

async def listItem(data: ItemCreate, session: AsyncSession):
    try:
        item_db = Item(**data.model_dump())
        session.add(item_db)
        await session.commit()
        await session.refresh(item_db)
        return {'success':True, 'data':item_db}
    except Exception as e:
        raise e
    
async def updateItem(update_data: ItemUpdate, session: AsyncSession):
    matchR = await session.exec(select(Item).where(and_(Item.seller_id == update_data.seller_id, Item.id == update_data.id)))
    print(update_data.id)
    match_ = matchR.first()
    if match_:
        itemUpdate_db = update_data.model_dump(exclude_unset=True)
        for key, val in itemUpdate_db.items():
            setattr(match_, key, val)
        await session.commit()
        await session.refresh(match_)
        return match_
    else:
        raise HTTPException(404, detail="Item not found")
    
async def delListing(del_item: DelItem, session:AsyncSession):
    item_ = await session.exec(select(Item).where(and_(Item.id==del_item.iid, Item.seller_id == del_item.seller_id)))
    item = item_.first()
    
    if not item:
        raise HTTPException(404, detail = "Item to be deleted not found!")
    
    await session.delete(item)    
    await session.commit()
    return {'success':True, 'deleted':item}

async def fetchUserItems(user_id: UUID, session: AsyncSession):
    statement = select(Item).where(Item.seller_id == user_id).options(selectinload(Item.seller)) #type:ignore
    items_ = await session.exec(statement)
    items = items_.all()

    if items:
        return items
    else:
        raise HTTPException(404, detail="No items listed")
    
