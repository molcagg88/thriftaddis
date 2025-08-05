from fastapi import APIRouter, Depends, HTTPException
from db.main import get_session, get_db_session
from sqlmodel import select
from db.models import UserPydantic, BidRequest, Bids, BidUpdate, BidBroadcast, UserPublic
from typing import Annotated
import copy
from pydantic import create_model
from utils.websockets import manager

async def create_bid(bidData: BidRequest, userData: UserPydantic):
    to_add = Bids(user_id=userData.uid, amount=bidData.amount, auction_id=bidData.auction_id)
    async with get_db_session() as session:
        try:
            load_bids_query = select(Bids).where(Bids.auction_id==bidData.auction_id)
            res = await session.exec(load_bids_query)
            existing_bids = res.all()
            for bid in existing_bids:
                if bid.amount>=bidData.amount:
                    raise HTTPException(400, detail="New bid is lower than current highest bid")
            
            session.add(to_add)
            await session.commit()
            await session.flush()
            await session.refresh(to_add)
            creator = UserPublic(username = userData.username, fname=userData.fname, lname = userData.lname)
            to_broad = BidBroadcast(id = to_add.id, auction_id=to_add.auction_id, user=creator, amount = to_add.amount, created_at=str(to_add.created_at))
            await manager.broadcast({"new":to_broad.model_dump()})
            print("broadcasted")
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(500, detail=f"Unexpected error at create bid: {e}")

        return to_add

async def update_bid(bidUpdate: BidUpdate, userData: UserPydantic):
    async with get_db_session() as session:
        try:
            users_bid= await session.get(Bids, bidUpdate.bid_id)
            if not users_bid:
                raise HTTPException(404, detail="bid not found")
            res2 = await session.exec(select(Bids).order_by(Bids.created_at.desc()).where(Bids.user_id==userData.uid))
            users_bids = res2.all()
            if users_bid != users_bids[0]:
                raise HTTPException(403, detail="Only user's latest bid can be updated")
            if users_bid.user_id != userData.uid:
                raise HTTPException(401, detail="User not allowed to edit this bid")
            
            load_bids_query = select(Bids).where(Bids.auction_id==users_bid.auction_id, Bids.user_id!=userData.uid)
            res = await session.exec(load_bids_query)
            existing_bids = res.all()
            
            for bid in existing_bids:
                if bid.amount>=bidUpdate.amount:
                    raise HTTPException(400, detail="Updated bid is lower than or equal to auction's current highest bid")

            users_bid.amount = bidUpdate.amount
            await session.commit()
            await session.refresh(users_bid)
            creator = UserPublic(username = userData.username, fname=userData.fname, lname = userData.lname)
            to_broad = BidBroadcast(id = users_bid.id, auction_id=users_bid.auction_id, user=creator, amount = users_bid.amount, created_at=str(users_bid.created_at))
            await manager.broadcast({"update":to_broad.model_dump()})
            print("broadcasted")
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(500, detail=f"Unknown error in update bid: {e}")
        return users_bid
    
async def delete_bid(bid_id: int, userData: UserPydantic):
    async with get_db_session() as session:
        try:
            target = await session.get(Bids, bid_id)
            if not target:
                raise HTTPException(404, detail="Bid not found")
            if target.user_id != userData.uid:
                raise HTTPException(401, detail="User unauthorized to delete this bid")
            
            session.delete(target)
            await session.commit()
            await manager.broadcast({"delete":bid_id})
            print("broadcasted")
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(500, detail=f"Unexpected error in delete bid: {e}")

async def fetch_bids(auction_id: int):
    async with get_db_session() as session:
        try:
            query = select(Bids).order_by(Bids.created_at.desc()).where(Bids.auction_id==auction_id)
            res = await session.exec(query)
            bids = res.all()
        except Exception as e:
            raise HTTPException(500, detail=f"Unknown error occured in fetch_bids service: {e}")
        return bids
        