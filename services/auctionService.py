from db.models import (ItemPydantic, UserPydantic, 
                       Item, Auction, AucServe, Status, 
                       ItemCreate, AucServeUpdate, ItemUpdate,
                        AuctionDelReq, ItemUpdateAuc, 
                        ItemInAucCreate, PaginationModel)
from services.listingService import listItem
from db.main import get_db_session
from fastapi import HTTPException
from sqlmodel import select
from datetime import datetime, timezone
from sqlmodel.ext.asyncio.session import AsyncSession
from services.listingService import updateItem, delListing
from utils.auctionUtil import update_if_changed
from sqlalchemy.orm import selectinload
from typing import Optional

async def auction_mini_service(session: AsyncSession, item: Item, auc_serve: AucServe):
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
            
            return new_auc
        else:
            raise HTTPException(404, detail="Item referenced for auction not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(400, detail=f"Unexpected error during auction_mini_service: {e}")

async def auction_mini_service_NI(session: AsyncSession, item: Item, auc_serve: AucServe):
    try:
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
        
        return new_auc
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(400, detail=f"Unexpected error during auction_mini_service: {e}")

async def create_auction(item: ItemInAucCreate, auc_serve: AucServe, userData: UserPydantic):
    if item.price and item.price < 0:
        raise HTTPException(400, detail="price must be positive")
    try:
        async with get_db_session() as session:#type:ignore
            async with session.begin():
                if item.id:
                    target_item = await session.get(Item, item.id)
                    if target_item is None:
                        raise HTTPException(404, detail="Item referenced does not exist")
                    if target_item.seller_id != userData.uid:
                        raise HTTPException(403, detail="user not allowed to create auction")
                    if target_item.auction_id:
                        raise HTTPException(409, detail="Item is already listed on another auction")
                    response = await auction_mini_service(session, target_item, auc_serve)
                    await session.flush()
                    await session.refresh(response)
                    target_item.auction_id = response.auction_id
                    await session.flush()
                    await session.refresh(target_item)
                    return {"success": True, "data":response}

                elif not item.id:
                    data = ItemCreate(name=item.name, description=item.description, price=item.price, category=item.category, condition=item.condition)
                    try:
                        item_db_ = data.model_dump()
                        item_db_.update({"seller_id":userData.uid})
                        item_db = Item(**item_db_)
                        session.add(item_db)
                        await session.flush()
                        await session.refresh(item_db)
                        create_item = {'success':True, 'data':item_db}
                        response = await auction_mini_service_NI(session, item=item_db, auc_serve=auc_serve)
                        
                        await session.flush()
                        await session.refresh(response)
                        item_db.auction_id = response.auction_id
                        await session.flush()
                        await session.refresh(item_db)
                    except Exception as e:
                        raise e
                    if not create_item or not create_item["success"]:
                        raise HTTPException(500, detail="Unknown error in create item for create auction")
                    
                    return {"success":True, "data":response}

    except HTTPException:
        raise
        
    except Exception as e:
        raise HTTPException(500, detail=f"Unexpected error while create_auction: {e}")

async def update_auction(auc: ItemUpdateAuc, auc_serve_update: AucServeUpdate, userData: UserPydantic):
    if auc.price and auc.price < 0:
        raise HTTPException(400, detail="price must be positive")
    try:
        
        async with get_db_session() as session:#type:ignore
            async with session.begin():
                stmt = (
                    select(Auction)
                    .where(Auction.auction_id == auc_serve_update.auction_id)
                    .with_for_update()
                )
                
                result = await session.exec(stmt)
                to_update = result.one_or_none()

                if not to_update:
                    raise HTTPException(404, detail="Auction entry not found")
                item_ = await session.exec(select(Item).where(Item.auction_id==auc_serve_update.auction_id))
                item = item_.one_or_none()
                if item.seller_id != userData.uid:
                    raise HTTPException(403, detail="user not allowed to update auction")
                auct_update_ = auc_serve_update.model_dump(exclude_unset=True)
                auct_update = {k:v for k, v in auct_update_.items() if v is not None}
                update_if_changed(to_update, auct_update)
                
                item_update_res = await updateItem(update_data=ItemUpdate(id=item.id, name=auc.name, description=auc.description, price=auc.price, category=auc.category, condition=auc.condition), session=session, userData=userData)#type:ignore
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

async def delete_auction(del_req: AuctionDelReq, userData: UserPydantic):
    try:
        async with get_db_session() as session:
            async with session.begin():
                query = select(Auction).where(Auction.auction_id==del_req.auction_id).with_for_update()

                target_auc_= await session.exec(query)
                target_auc = target_auc_.one_or_none()

                if not target_auc:
                    raise HTTPException(404, detail="Auction to delete not found")
                
                
                try:
                    if not del_req.keep_item:
                        item_ = await session.exec(select(Item).where(Item.auction_id==del_req.auction_id).with_for_update())
                        item = item_.one_or_none()
                        if item.seller_id != userData.uid:
                            raise HTTPException(401, detail="Unauthorized to delete this auction")
                        await session.delete(item)
                    await session.delete(target_auc)
                    return {"success":True, "deleted":target_auc}
                except Exception as e:
                    raise HTTPException(500, detail=f"error while executing delete queries: {e}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, detail=f"Unknown error at delete_auction: {e}")

async def get_user_auctions(userData: UserPydantic):
    try:
        async with get_db_session() as session:
            query = (
                select(Item)
                .where(Item.seller_id == userData.uid, Item.auction_id.is_not(None))
                .options(selectinload(Item.auction)))                
            try:
                aucs = await session.exec(query)
                itms = aucs.all()
            except:
                raise HTTPException(500, detail="Error fetching auctions")
            data = [{**item.auction.model_dump(), **item.model_dump()} for item in itms if item.auction is not None]
            return {"auctions":data}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, detail=f"Unexpected error at get user auctions: {e}")
            
async def fetchAllAuctions(pagination: PaginationModel):
    async with get_db_session() as session:
        try:
            query = select(Auction).order_by(Auction.created_at.desc()).offset(pagination.offset).limit(pagination.limit)

            auctions_ = await session.exec(query)
            auctions = auctions_.all()

        except Exception as e:
            raise HTTPException(500, detail=f"Error fetching auctions from the database: {e}")

        return auctions
    
async def check_auction_status(auction_id: int):
    async with get_db_session() as session:
        auction = await session.get(Auction, auction_id)
        if auction is None:
            print("auction not found")
            raise HTTPException(404, detail="Auction not found")
        if auction.status!=Status.live:
            print("auction not live")
            raise HTTPException(400, detail="Auction is not live")
    return True
        