from fastapi import APIRouter, Depends, HTTPException
from db.models import AuctionReq, UserPydantic, ItemPydantic, AucServe, AucServeUpdate, AuctionUpdate, ItemUpdateAuc
from typing import Annotated
from services.authService import get_current_user
from services.auctionService import create_auction, update_auction

auctionR = APIRouter(prefix="/auction")

@auctionR.post("/")
async def createAuction(data: AuctionReq, userData: Annotated[UserPydantic, Depends(get_current_user)]):
    to_auc = ItemPydantic(id=getattr(data, 'item_id', None), name=data.name, seller_id=userData.uid, description=data.description, price=data.price, category=data.category, condition=data.condition)
    response = await create_auction(item=to_auc, auc_serve=AucServe(starting_time=data.starting_time, ending_time=data.ending_time), userData=userData)
    if response["success"]:#type:ignore
        return response
    else:
        raise HTTPException(400, detail="Unknwon error, check log")
    
@auctionR.put("/")
async def updateAuction(data: AuctionUpdate, userData: Annotated[UserPydantic, Depends(get_current_user)]):
    to_upd = ItemUpdateAuc(name=getattr(data, "name", None), description=getattr(data, "description", None), price=getattr(data, "price", None), category=getattr(data, "category", None), condition=getattr(data, "condition", None))
    try:
        response = await update_auction(auc=to_upd, auc_serve_update=AucServeUpdate(auction_id=data.auction_id, starting_time=getattr(data, "starting_time", None), ending_time=getattr(data, "ending_time", None)), userData=userData)
        if not response["success"]:
            raise HTTPException(500, detail="Unknown error during update_auction")
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, detail=f"Unexpected exception triggered in updateAuction, {e}")
    