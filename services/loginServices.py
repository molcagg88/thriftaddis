from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from fastapi import HTTPException
from db.models import User, LoginModel



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