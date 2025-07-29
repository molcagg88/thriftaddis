from fastapi import APIRouter, Depends, HTTPException
from db.models import ItemCreate, ItemUpdate, User, DelItem, UserPydantic
from uuid import UUID
from typing import Annotated
from sqlmodel.ext.asyncio.session import AsyncSession
from db.main import get_session
from services.authService import get_current_user
from services.listingService import listItem, updateItem, delListing, fetchUserItems
from pydantic import BaseModel

listingR = APIRouter(prefix='/listing')

# userData = UserPydantic(uid= "879d8009-d7c0-44f5-9b20-9dc39fbe5706", username="user2", fname="user", lname="one", email="user2@gmail.com", password="str")

@listingR.get('/')
async def getUserListings(userData: Annotated[UserPydantic, Depends(get_current_user)]):
    response = await fetchUserItems(userData.uid)
    if response:
        return {'success':True, "data":response}
    else:
        raise HTTPException(404, "Fetch user listings returned empty")
    

@listingR.post('/')
async def createListing(listing_data: ItemCreate, userData: Annotated[UserPydantic, Depends(get_current_user)]):
    
    response = await listItem(listing_data, userData)
    if response["success"]:
        return response
    else:
        raise HTTPException(400, detail="Failed to create listing")
    
@listingR.put('/')
async def updateListing(update_data: ItemUpdate, userData: Annotated[UserPydantic, Depends(get_current_user)]):
    try:
        response = await updateItem(update_data, userData)
        return response
    except Exception as e:
        raise e
    
@listingR.delete('/')
async def deleteListing(del_Item: DelItem, userData: Annotated[UserPydantic, Depends(get_current_user)]):
    try:
        response = await delListing(del_Item, userData)
        if response['success']:
            return response
    except Exception as e:
        raise e