from fastapi import (APIRouter, Depends, 
                     HTTPException, WebSocket, 
                     WebSocketDisconnect)
from db.models import (AuctionReq, UserPydantic, ItemPydantic, 
                        AucServe, AucServeUpdate, AuctionUpdate,
                         AuctionDelReq, ItemUpdateAuc, 
                         ItemInAucCreate, PaginationModel, 
                         Fetch_ended_truth, RenewReq, AucClose)
from typing import Annotated
from utils.pagination import getPaginationParams
from utils.auctionUtil import fetchEnded, generate_auction_times
from services.authService import get_current_user
from tasks.auction_status import update_auction_statuses_once
from services.auctionService import (create_auction, update_auction, 
                                     delete_auction, get_user_auctions, 
                                     fetchAllAuctions, check_auction_status, 
                                     loadAuction, close_auction, check_auction_not_ended, check_auction_closed)
from utils.websockets import manager

auctionR = APIRouter(prefix="/auction")

@auctionR.get('/')
async def getAllAuctions(pagination: Annotated[PaginationModel, Depends(getPaginationParams)], 
                         fetch: Annotated[Fetch_ended_truth, Depends(fetchEnded)],
                         userData: Annotated[UserPydantic, Depends(get_current_user)]):
    try: 
        response = await fetchAllAuctions(pagination=pagination, fetch_ended=fetch.truth)
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

    response = await create_auction(item=to_auc, auc_serve=AucServe(starting_time=data.starting_time, ending_time=data.ending_time, starting_price=data.starting_price), userData=userData)
    if response["success"]:#type:ignore
        return response
    else:
        raise HTTPException(400, detail="Unknwon error, check log")
    
@auctionR.put("/")
async def updateAuction(data: AuctionUpdate, userData: Annotated[UserPydantic, Depends(get_current_user)]):
    to_upd = ItemUpdateAuc(name=getattr(data, "name", None), description=getattr(data, "description", None), price=getattr(data, "price", None), category=getattr(data, "category", None), condition=getattr(data, "condition", None))
    try:
        response = await update_auction(auc=to_upd, auc_serve_update=AucServeUpdate(auction_id=data.auction_id, starting_time=getattr(data, "starting_time", None), ending_time=getattr(data, "ending_time", None), starting_price=data.price), userData=userData)
        if not response["success"]:
            raise HTTPException(500, detail="Unknown error during update_auction")
        await update_auction_statuses_once()
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, detail=f"Unexpected exception triggered in updateAuction, {e}")
    
'''
Broadcasts a {"update_auction":{"auction":<auction data>, "item": <item data>}}
'''

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

@auctionR.websocket("/{auction_id}")
async def websocket_endpoint(auction_id: int, websocket: WebSocket):
    await check_auction_status(auction_id)
    await websocket.accept()
    try:
        # Expect auth message immediately
        auth_data = await websocket.receive_json()
        token = auth_data.get("token")
        if not token:
            await websocket.close(code=1008)  # Policy Violation
            return

        try:
            userData = await get_current_user(token)
            manager.userData = userData
        except:
            await websocket.close(code=1008)
            return

        await manager.connect(websocket)

        while True:
            await websocket.receive_text()  # Keeps alive
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@auctionR.get('/{auction_id}')
async def load_auction(auction_id: int, userData: Annotated[UserPydantic, Depends(get_current_user)]):
    try:
        response = await loadAuction(auction_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, detail=f"Unexpected error at load auction route: {e}")
    return response

@auctionR.put("/renew")
async def renewAuction(data: RenewReq, userData: Annotated[UserPydantic, Depends(get_current_user)]):
    await check_auction_closed(data.auction_id)
    try:
        to_upd = ItemUpdateAuc(name=None, description=None, price= None, category=None, condition=None)
        if (not data.starting_time and data.ending_time) or \
        (data.starting_time and not data.ending_time):
            raise HTTPException(
                400,
                detail="Either both starting and ending time have to be provided or both have to be not provided")
        if not data.starting_time and not data.ending_time:
            times = await generate_auction_times(1440)
            data.starting_time = times.starting_time
            data.ending_time = times.ending_time
        response = await update_auction(auc=to_upd, auc_serve_update=AucServeUpdate(auction_id=data.auction_id, starting_time=data.starting_time, ending_time=data.ending_time, starting_price=data.new_starting_price), userData=userData)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, detail=f"Unexpected error in renewAuction: {e}")
    return response

@auctionR.put('/close')
async def closeAuction(data: AucClose, userData: Annotated[UserPydantic, Depends(get_current_user)]):
    await check_auction_not_ended(data.auction_id)
    try:
        response = await close_auction(data, userData)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, detail=f"Unexpected error in close auction: {e}")
    return {"success":True, "auction":response}

@auctionR.get('/send')
async def sendd():
    bih = 45
    await manager.broadcast({"update":bih})
