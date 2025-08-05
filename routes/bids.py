from fastapi import APIRouter, Depends, HTTPException, Response
from services.authService import get_current_user
from db.models import UserPydantic, BidRequest, BidUpdate
from services.bidsService import create_bid, update_bid, delete_bid, fetch_bids
from typing import Annotated


bidsR = APIRouter(prefix="/bids", tags=["Bids"])

@bidsR.post('/')
async def createBid(bid_req: BidRequest, userData: Annotated[UserPydantic, Depends(get_current_user)]):
    try:
        response = await create_bid(bid_req, userData)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, detail=f"Error in create bid route: {e}")
    
    return {"success":True, "data":response}
""" 
Broadcasts a {"new":<created bid data>} to the websocket
"""

@bidsR.put('/')
async def updateBid(bid_upd: BidUpdate, userData: Annotated[UserPydantic, Depends(get_current_user)]):
    try:
        response = await update_bid(bid_upd, userData)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, detail=f"Unexpected error in update bid call: {e}")
    
    return {"success": True, "data":response}
"""
Broadcasts a {"update":<updated bid data>} to the websocket
"""

@bidsR.delete("/{bid_id}", status_code=204)
async def deleteBid(bid_id: int, userData: Annotated[UserPydantic, Depends(get_current_user)]):
    await delete_bid(bid_id, userData)
    return Response(status_code=204)
"""
Broadcasts a {"delete":<bid_id>} to the websocket
"""


@bidsR.get('/{auction_id}')
async def getAllBids(auction_id: int, userData: Annotated[UserPydantic, Depends(get_current_user)]):
    return await fetch_bids(auction_id)


