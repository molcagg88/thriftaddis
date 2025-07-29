from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from db.models import User, RegisterModel, TokenModel
from datetime import timedelta, datetime, timezone
import copy
import jwt
from typing import Optional

# Constants
EXPIRY_MINUTES = 30
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"

# JWT Token Creator
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = copy.deepcopy(data)

    expiry = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=EXPIRY_MINUTES))
    to_encode.update({"exp": expiry.timestamp()})  # Unix timestamp is accepted by most JWT libs

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# User Registration
async def createUser(user_data: RegisterModel, session: AsyncSession):
    try:
        db_user = User(**user_data.model_dump())
        session.add(db_user)
        await session.commit()
        await session.refresh(db_user)

        return {"success": True}

    except IntegrityError as e:
        await session.rollback()
        error_msg = str(e.orig).lower()  # make lowercase to make checks more robust

        if "username" in error_msg:
            raise HTTPException(status_code=400, detail="Username already exists")
        elif "email" in error_msg:
            raise HTTPException(status_code=400, detail="Email already exists")
        else:
            raise HTTPException(status_code=500, detail="Database error (unknown constraint violation)")
