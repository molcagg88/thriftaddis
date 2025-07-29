import jwt
from typing import Annotated
from fastapi import Depends
from db.models import TokenData
from fastapi.security import OAuth2PasswordBearer
from sqlmodel.ext.asyncio.session import AsyncSession
from .userService import get_user
from typing import Optional
from db.models import User

oauth2_scheme = OAuth2PasswordBearer('token')
algorithm = 'HS256'
secret_key='09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7'
async def decode_token(token: str):
    payload=jwt.decode(token, secret_key, algorithms=algorithm)
    username = payload['sub']
    user = TokenData(username=username)
    return user

async def get_current_user(token: Optional[str]= Depends(oauth2_scheme)):
    try:
        userToken = await decode_token(token)
        user = await get_user(userToken.username)
        return user
    
    except Exception as e:
        raise e
    

    