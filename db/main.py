from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import SQLModel
from config import settings

engine=create_async_engine(settings.DATABASE_URL, echo=True)
async_session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        from .models import User, Item
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_session()->AsyncSession:
    async with async_session() as session:
        yield session

def get_db_session():
    return async_session()