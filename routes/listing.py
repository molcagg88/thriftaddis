from fastapi import APIRouter, Depends, HTTPException
from db.models import ItemCreate, ItemUpdate, User, DelItem
from uuid import UUID
from sqlmodel.ext.asyncio.session import AsyncSession
from db.main import get_session
from services.listingService import listItem, updateItem, delListing, fetchUserItems

listingR = APIRouter(prefix='/listing')

@listingR.get('/')
async def getUserListings(user_id: UUID, session: AsyncSession= Depends(get_session)):
    response = await fetchUserItems(user_id, session)
    if response:
        return {'success':True, "data":response}
    else:
        raise HTTPException(404, "Fetch user listings returned empty")
    

@listingR.post('/')
async def createListing(listing_data: ItemCreate, session: AsyncSession = Depends(get_session)):
    print("we are in createList")
    
    response = await listItem(listing_data, session)
    if response["success"]:
        return response
    else:
        return {'status':'HOUSTON WE HAVE A PROBLEM'}
    
@listingR.put('/')
async def updateListing(update_data: ItemUpdate, session: AsyncSession = Depends(get_session)):
    try:
        response = await updateItem(update_data, session)
        return response
    except Exception as e:
        raise e
    
@listingR.delete('/')
async def deleteListing(del_Item: DelItem, session: AsyncSession=Depends(get_session)):
    try:
        response = await delListing(del_Item, session)
        if response['success']:
            return response
    except Exception as e:
        raise e