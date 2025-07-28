from fastapi import APIRouter, Depends
from db.models import LoginModel
from db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from services.loginServices import authUser
loginR = APIRouter(prefix='/login')


@loginR.post('/')
async def login(data: LoginModel, session: AsyncSession = Depends(get_session)):
    try:
        response = await authUser(data, session)
        if response==True:
            return True
        else:
            return response
    except Exception as err:
        raise err