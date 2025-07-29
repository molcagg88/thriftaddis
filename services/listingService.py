from db.models import ItemCreate, Item, ItemUpdate, DelItem, User, UserPydantic
from fastapi import HTTPException, Depends
from sqlmodel import select, and_
from typing import Annotated, Optional
from db.main import get_db_session
from sqlalchemy.orm import selectinload
from uuid import UUID

from sqlmodel.ext.asyncio.session import AsyncSession

async def listItem(data: ItemCreate, userData: UserPydantic):
    
    try:
        item_db_ = data.model_dump()
        item_db_.update({"seller_id":userData.uid})
        item_db = Item(**item_db_)
        async with get_db_session() as session:#type:ignore
            session.add(item_db)
            await session.commit()
            await session.refresh(item_db)
        return {'success':True, 'data':item_db}
    except Exception as e:
        raise e
    
async def updateItem(update_data: ItemUpdate, userData: UserPydantic):
    async with get_db_session() as session:#type:ignore
        matchR = await session.exec(select(Item).where(and_(Item.seller_id == userData.uid, Item.id == update_data.id)))
        match_ = matchR.first()
        if match_:
            itemUpdate_db = update_data.model_dump(exclude_unset=True)
            itemUpdate_db.update({"seller_id":userData.uid})
            for key, val in itemUpdate_db.items():
                setattr(match_, key, val)
            await session.commit()
            await session.refresh(match_)
            return match_
        else:
            raise HTTPException(404, detail="Item not found")
    
async def delListing(del_item: DelItem, userData: UserPydantic):
    async with get_db_session() as session:#type:ignore
        item_ = await session.exec(select(Item).where(and_(Item.id==del_item.iid, Item.seller_id == userData.uid)))
        item = item_.first()
        
        if not item:
            raise HTTPException(404, detail = "Item to be deleted not found!")
        
        await session.delete(item)    
        await session.commit()
        return {'success':True, 'deleted':item}

async def fetchUserItems(user_id: UUID):
    async with get_db_session() as session:#type:ignore
        statement = select(Item).where(Item.seller_id == user_id) #type:ignore
        items_ = await session.exec(statement)
        items = items_.all()
        
        if items:
            return items
        else:
            raise HTTPException(404, detail="No items listed")
    
