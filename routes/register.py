from fastapi import APIRouter, Depends
from db.models import RegisterModel, TokenModel
from db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from services.registerServices import createUser, create_access_token
registerR = APIRouter(prefix='/register')


@registerR.post('/')
async def register(data: RegisterModel, session: AsyncSession = Depends(get_session)):
    try:
        response = await createUser(data, session)
        if response["success"]:
            try:
                access_token = create_access_token(data={"user":data.username})
                return TokenModel(access_token=access_token, token_type="Bearer")
            except Exception as e:
                raise e
    except Exception as err:
        raise err
    


