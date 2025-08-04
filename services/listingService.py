from db.models import (ItemCreate, Item, 
                       ItemUpdate, DelItem, 
                       User, UserPydantic, PaginationModel)
from fastapi import HTTPException, Depends
from sqlmodel import select, and_
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Annotated, Optional
from db.main import get_db_session
from sqlalchemy.orm import selectinload
from utils.auctionUtil import update_if_changed
from uuid import UUID

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
    
async def updateItem(
    update_data: ItemUpdate, 
    userData: UserPydantic, 
    session: Optional[AsyncSession] = None,
    item_instance: Optional[Item] = None
):
    if session is None:
        # fallback to creating a new session if none provided (legacy support)
        async with get_db_session() as session:
            return await updateItem(update_data, userData, session=session, item_instance=item_instance)

    # Use the passed item instance or fetch if not provided
    if item_instance is None:
        matchR = await session.exec(
            select(Item).where(and_(Item.seller_id == userData.uid, Item.id == update_data.id))
        )
        item_instance = matchR.first()
        if item_instance is None:
            raise HTTPException(404, detail="Item not found")

    # Clean the update data
    itemUpdate_db = update_data.model_dump(exclude_unset=True)
    cleaned_dict = {k: v for k, v in itemUpdate_db.items() if v is not None}
    cleaned_dict.update({"seller_id": userData.uid})

    try:
        update_if_changed(item_instance, cleaned_dict)
    except Exception as e:
        raise HTTPException(500, detail=f"Error occurred in update item(if changed): {e}")

    await session.flush()  # flush but do not commit; commit controlled by outer scope
    
    # Optionally refresh if you want fresh DB state
    await session.refresh(item_instance)
    if getattr(session, "_sa_initiator", None) is None:
        await session.commit()
    return {"success": True, "data": item_instance}

    
async def delListing(del_item: DelItem, userData: UserPydantic):
    async with get_db_session() as session:#type:ignore
        item_ = await session.exec(select(Item).where(and_(Item.id==del_item.id, Item.seller_id == userData.uid)))
        item = item_.first()
        
        if not item:
            raise HTTPException(404, detail = "Item to be deleted not found!")
        
        await session.delete(item)    
        await session.commit()
        return {'success':True, 'deleted':item}
    
#   
#Fetches items listed by user
#
async def fetchUserItems(user_id: UUID):
    async with get_db_session() as session:#type:ignore
        statement = select(Item).where(Item.seller_id == user_id) #type:ignore
        items_ = await session.exec(statement)
        items = items_.all()
        
        if items:
            return items
        else:
            raise HTTPException(404, detail="No items listed")
    
async def fetchAllListings(pagination: PaginationModel):
    try:
        async with get_db_session() as session:
            print(pagination)
            query = select(Item).order_by(Item.created_at.desc()).offset(pagination.offset).limit(pagination.limit)

            items_ = await session.exec(query)
            items = items_.all()
    except Exception as e:
        raise HTTPException(500, detail=f"Unexpected error in fetchAllListings service: {e}")
    return items