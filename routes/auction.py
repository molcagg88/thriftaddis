from fastapi import APIRouter, Depends, HTTPException
from db.models import (AuctionReq, UserPydantic, ItemPydantic, 
                        AucServe, AucServeUpdate, AuctionUpdate,
                         AuctionDelReq, ItemUpdateAuc, 
                         ItemInAucCreate, PaginationModel)
from typing import Annotated
from utils.pagination import getPaginationParams
from services.authService import get_current_user
from services.auctionService import create_auction, update_auction, delete_auction, get_user_auctions, fetchAllAuctions

auctionR = APIRouter(prefix="/auction")

@auctionR.get('/')
async def getAllAuctions(pagination: Annotated[PaginationModel, Depends(getPaginationParams)],
                         userData: Annotated[UserPydantic, Depends(get_current_user)]):
    try: 
        response = await fetchAllAuctions(pagination)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, detail=f"Unexpected error while fetchAllAuctions: {e}")
    
    return response

@auctionR.get("/user-auctions")
async def get_user_aucs(userData: Annotated[UserPydantic, Depends(get_current_user)]):
    try: 
        response = await get_user_auctions(userData)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, detail=f"Unexpected error in get user auctions: {e}")
    return response

@auctionR.post("/")
async def createAuction(data: AuctionReq, userData: Annotated[UserPydantic, Depends(get_current_user)]):
    if not data.item_id:
        to_auc = ItemInAucCreate(name=data.name, seller_id=userData.uid, description=data.description, price=data.price, category=data.category, condition=data.condition)
    elif data.item_id:
        to_auc = ItemInAucCreate(id=data.item_id)

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
    
@auctionR.delete('/')    
async def delete_auc(del_request: AuctionDelReq, userData: Annotated[UserPydantic, Depends(get_current_user)]):
    try:
        response = await delete_auction(del_request, userData)
        if not response["success"]:
            raise HTTPException(500, detail="Error in response from delete auction")
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, detail="Unexpected error in delete auction route: {e}")