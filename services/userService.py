from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from db.models import User, UserPydantic
from typing import Optional, Annotated
from uuid import UUID
from fastapi import HTTPException, status, Depends
from db.main import get_db_session



async def get_user(username:Optional[str]=None, uid:Optional[UUID]=None):
    if not username and not uid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either username or uid must be provided."
        )
    try:
        query = None
        if username:
            query = select(User).where(User.username==username)
            
        elif uid:
            query = select(User).where(User.uid==uid)

        async with get_db_session() as session:
            response_ = await session.exec(query)
            response = response_.first()
        if response:
            user = UserPydantic.model_validate(response.model_dump())
            
    except HTTPException:
        raise
    except Exception as e:
        raise e
    return user