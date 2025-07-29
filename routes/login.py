from fastapi import APIRouter, Depends, HTTPException
from db.models import LoginModel, TokenModel
from db.main import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from services.loginServices import authUser, create_access_token
loginR = APIRouter(prefix='/login')


@loginR.post('/')
async def login(data: LoginModel, session: AsyncSession = Depends(get_session)):
    try:
        response = await authUser(data, session)
        if response==True:
            access_token = create_access_token(data={"sub":data.username})
            return {"access_token":access_token, "token_type":"Bearer"}
        else:
            raise HTTPException(401, detail="Login unsuccessful")
    except Exception as err:
        raise err