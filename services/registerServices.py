from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from db.models import User, RegisterModel, TokenModel
from datetime import timedelta, datetime, timezone
from fastapi.security import OAuth2PasswordBearer
import copy
import jwt
# from jwt.exceptions import InvalidTokenError
from typing import Optional

expiry_time = 30
secret_key = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
oauth_scheme = OAuth2PasswordBearer('token')
algorithm = "HS256"

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None ):
    to_encode = copy.deepcopy(data)
    if expires_delta:
        expiry = expires_delta
    else:
        expiry = datetime.now(timezone.utc)+timedelta(minutes=expiry_time)
    to_encode.update({"exp":expiry.timestamp()}) #type:ignore
    encoded=jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded



async def createUser(user_data: RegisterModel, session: AsyncSession):
    try:
        db_user =  User(**user_data.model_dump())

        session.add(db_user)
        await session.commit()
        await session.refresh(db_user)
        return {"success":True}
        
    except IntegrityError as e:
        await session.rollback()  # Important to avoid transaction issues

        error_msg = str(e.orig)  # Get the original PostgreSQL error

        if "username" in error_msg:
            raise HTTPException(
                status_code=400,
                detail="Username already exists"
            )
        elif "email" in error_msg:
            raise HTTPException(
                status_code=400,
                detail="Email already exists"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Database error (unknown constraint violation)"
            )

