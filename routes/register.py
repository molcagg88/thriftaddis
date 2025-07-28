from fastapi import APIRouter, Depends
from db.models import RegisterModel
from db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from services.registerServices import createUser
registerR = APIRouter(prefix='/register')


@registerR.post('/')
async def login(data: RegisterModel, session: AsyncSession = Depends(get_session)):
    try:
        response = await createUser(data, session)
        return {'success':'true'}
    except Exception as err:
        raise err
    


