from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from db.models import User, RegisterModel



async def createUser(user_data: RegisterModel, session: AsyncSession):
    try:
        db_user =  User(**user_data.model_dump())

        session.add(db_user)
        await session.commit()
        await session.refresh(db_user)
        return db_user
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

