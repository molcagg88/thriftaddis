from db.models import (ItemPydantic, UserPydantic, 
                       Item, Auction, AucServe, Status, 
                       ItemCreate, AucServeUpdate, ItemUpdate)
from services.listingService import listItem
from db.main import get_db_session
from fastapi import HTTPException
from sqlmodel import select
from datetime import datetime, timezone
from sqlmodel.ext.asyncio.session import AsyncSession
from services.listingService import updateItem
from typing import Optional

async def auction_mini_service(session: AsyncSession, item: ItemPydantic, auc_serve: AucServe):
    try:
        item_data_ = await session.exec(select(Item).where(Item.id==item.id))
        item_data = item_data_.first()

        if item_data:
            now = datetime.now(timezone.utc)
            if auc_serve.ending_time <= auc_serve.starting_time:
                raise HTTPException(400, "End time must be after start time")

            if auc_serve.ending_time <= now:
                raise HTTPException(400, "End time must be in the future")

            elif auc_serve.starting_time < now and auc_serve.ending_time > now:
                status = Status.live
            elif auc_serve.starting_time > now:
                status = Status.upcoming
            else:
                status = Status.ended 
            
            new_auc = Auction(item_id=item.id, starting_time=auc_serve.starting_time, ending_time=auc_serve.ending_time, status=status, starting_price=item.price)#type:ignore
            session.add(new_auc)
            try:
                await session.commit()
            except Exception as e:
                await session.rollback()
                #add logging
                raise HTTPException(500, detail="commit on auction creation failed")
            await session.refresh(new_auc)
            return new_auc
        else:
            raise HTTPException(404, detail="Item referenced for auction not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(400, detail=f"Unexpected error during auction_mini_service: {e}")

async def create_auction(item: ItemPydantic, auc_serve: AucServe, userData: UserPydantic):
    if item.price < 0:
        raise HTTPException(400, detail="price must be positive")
    try:
        async with get_db_session() as session:#type:ignore
            async with session.begin():
                if item.id:
                    if item.seller_id != userData.uid:
                        raise HTTPException(403, detail="user not allowed to create auction")
                    response = await auction_mini_service(session, item, auc_serve)
                    
                    return {"success":True, "data":response}
                elif not item.id:
                    create_item = await listItem(ItemCreate(name=item.name, description=item.description, price=item.price, category=item.category, condition=item.condition), userData)
                    if not create_item["success"]:
                        raise HTTPException(500, detail="Unknown error, check log")
                    response = await auction_mini_service(session, item=create_item["data"], auc_serve=auc_serve)
                    return {"success":True, "data":response}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, detail=f"Unexpected error while create_auction: {e}")
async def update_auction(auc: ItemPydantic, auc_serve_update: AucServeUpdate, userData: UserPydantic):
    if auc.price < 0:
        raise HTTPException(400, detail="price must be positive")
    try:
        async with get_db_session() as session:#type:ignore
            async with session.begin():
                if auc.seller_id != userData.uid:
                    raise HTTPException(403, detail="user not allowed to create auction")
                to_update = await session.get(Auction, id=auc_serve_update.auction_id, with_for_update=True)
                if not to_update:
                    raise HTTPException(404, detail="Auction entry not found")
                
                auct_update = auc_serve_update.model_dump(exclude_unset=True)
                for key, val in auct_update.items():
                    setattr(to_update, key, val)
                item_update_res = await updateItem(update_data=ItemUpdate(id=auc.id, name=auc.name, description=auc.description, price=auc.price, category=auc.category, condition=auc.condition), userData=userData)#type:ignore
                if not item_update_res["success"]:
                    await session.rollback()
                    raise HTTPException(400, detail="Unknown error, triggered at update item via auction update")
                
                return {"success":True, "data":{"auction":to_update, "item":item_update_res["data"]}}
                    
                
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error during auction update: {e}"
        )

