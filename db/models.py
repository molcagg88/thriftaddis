from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Column, ForeignKey
from uuid import UUID, uuid4
import sqlalchemy.dialects.postgresql as pg
from sqlalchemy.orm import Relationship
from typing import Optional, Annotated


class TokenModel(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str

class RegisterModel(BaseModel):
    username: str
    fname: str
    lname: str
    email: str
    password: str
    
class LoginModel(BaseModel):
    username: str
    password: str

class ItemCreate(BaseModel):
    name: str
    description: str
    price: float
    category: str
    condition: str
    
class ItemUpdate(BaseModel):
    id: int
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    condition: Optional[str] = None
    

class DelItem(BaseModel):
    id: int

class User(SQLModel, table=True):
    uid: UUID = Field(
        default_factory=uuid4,
        sa_column=Column(pg.UUID, primary_key=True)
    )
    username: str = Field(unique=True)
    fname: str
    lname: str
    email: str = Field(unique=True)
    password: str

    # items: Annotated[List["Item"], relationship(back_populates= "seller")]

class UserPydantic(BaseModel):
    class Config:
        from_attributes = True
    uid: UUID
    username: str
    fname: str
    lname: str
    email: str 
    password: str

class Item(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str
    description: str
    price: float
    category: str
    condition: str 
    seller_id: UUID = Field(
        sa_column=Column(
            pg.UUID,
            ForeignKey("user.uid"),
            nullable=False
        )
    )

    # seller: Annotated[Optional["User"],  relationship(back_populates="items")]