from fastapi import APIRouter, Depends, HTTPException
from db.models import ItemCreate, ItemUpdate, DelItem, UserPydantic, PaginationModel
from typing import Annotated
from services.authService import get_current_user
from services.listingService import listItem, updateItem, delListing, fetchUserItems, fetchAllListings
from utils.pagination import getPaginationParams

listingR = APIRouter(prefix='/listing')

# userData = UserPydantic(uid= "879d8009-d7c0-44f5-9b20-9dc39fbe5706", username="user2", fname="user", lname="one", email="user2@gmail.com", password="str")

@listingR.get('/')
async def getAllListings(pagination: Annotated[PaginationModel, Depends(getPaginationParams)], 
                         userData: Annotated[UserPydantic, Depends(get_current_user)]):
    try:
        response = await fetchAllListings(pagination) 
    except Exception as e:
        raise HTTPException(500, detail=f"Unexpected error in getAllListings route: {e}")
    return response
@listingR.get('/user-listings')
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
        if response["success"]:
            return response
        else:
            raise HTTPException(400, detail="Unknown error, triggered at update listing")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, detail=f"Unhandled error: {e}")
    
@listingR.delete('/')
async def deleteListing(del_Item: DelItem, userData: Annotated[UserPydantic, Depends(get_current_user)]):
    try:
        response = await delListing(del_Item, userData)
        if response['success']:
            return response
    except Exception as e:
        raise e