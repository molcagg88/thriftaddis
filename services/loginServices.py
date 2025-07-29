from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from fastapi import HTTPException
from db.models import User, LoginModel
from typing import Optional
from datetime import timedelta, datetime, timezone
import copy
import jwt

secret_key = '09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7'
algorithm = "HS256"
expiry_time=30


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None ):
    to_encode = copy.deepcopy(data)
    if expires_delta:
        expiry = expires_delta
    else:
        expiry = datetime.now(timezone.utc)+timedelta(minutes=expiry_time)
    to_encode.update({"exp":expiry.timestamp()}) #type:ignore
    print(to_encode)
    encoded=jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded

async def authUser(user_data: LoginModel, session: AsyncSession):
    try:
        matchesR = await session.exec(select(User).where(User.username==user_data.username))
        matches = matchesR.first()
        if matches and matches.password == user_data.password:
            print (f'{matches.password}, {user_data.password}')
            return True
        elif matches and matches.password != user_data.password:
            return {'status':'Incorrect password'}
        else:
            return {'status':'user not found'}
       
    except Exception as e:
        raise e