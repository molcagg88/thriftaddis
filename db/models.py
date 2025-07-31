from pydantic import BaseModel, field_validator, ValidationInfo
from sqlmodel import SQLModel, Field, Column, ForeignKey, Relationship
from uuid import UUID, uuid4
from typing import List, Union
import sqlalchemy.dialects.postgresql as pg
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from typing import Optional
from enum import Enum

class Conditions(str, Enum):
    new = "NEW"
    used = "USED"

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
    @field_validator('price')
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError("Price must be positive")
        return v
    name: str
    description: str
    price: float
    category: str
    condition: Conditions
    
class ItemUpdate(BaseModel):
    id: int
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    condition: Optional[Conditions] = None
    
class ItemPydantic(BaseModel):
    id: Optional[int] = None
    name: str
    description: str
    price: float
    category: str
    condition: Conditions
    seller_id: Optional[UUID] = None

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

    items: List["Item"] = Relationship(back_populates= "seller", sa_relationship=relationship("Item", lazy="select"))#type:ignore
    bids: List["Bid"] = Relationship(back_populates = "bidder", sa_relationship=relationship("Bid", lazy="select"))#type:ignore

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
    price: float = Field(index=True)
    category: str
    condition: Conditions 
    seller_id: UUID = Field(
        sa_column=Column(
            pg.UUID,
            ForeignKey("user.uid"),
            nullable=False,
            index=True
        )
    )

    seller: Optional[User] = Relationship(back_populates="items")#type: ignore
    auction: Optional["Auction"] = Relationship(back_populates="item")#type:ignore

class Status(str, Enum):
    upcoming = "UPCOMING"
    live = "LIVE"
    ended = "ENDED"

class Auction(SQLModel, table=True):
    auction_id: int = Field(primary_key=True)
    item: Optional[Item] = Relationship(back_populates="auction")#type:ignore
    item_id: int = Field(foreign_key="item.id", nullable=False)
    starting_time: datetime = Field(nullable=False)
    ending_time: datetime = Field(nullable=False)
    starting_price: float
    status: Status = Field(index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)

class Bid(SQLModel, table=True):
    id: int = Field(primary_key=True, index=True)
    bidder_id: UUID = Field(foreign_key="user.uid")
    amount: float
    bid_time: datetime = Field(default_factory= lambda: datetime.now(timezone.utc), nullable=False)
    auction_id: int = Field(foreign_key="auction.auction_id", nullable=False)
    bidder: Optional[User] = Relationship(back_populates="bids")#type:ignore

class AuctionReq(BaseModel):
    @field_validator("ending_time")
    def validate_times(cls, v: datetime, info: ValidationInfo) -> datetime:
        if "starting_time" in info.data and v <= info.data["starting_time"]:
            raise ValueError("End time must be after start time")
        return v
    item_id: Optional[int] = None
    name: str
    description: str
    price: float
    category: str
    condition: Conditions
    starting_time: datetime
    ending_time: datetime

class AuctionUpdate(BaseModel):
    @field_validator("ending_time")
    def validate_times(cls, v: datetime, info: ValidationInfo) -> datetime:
        if "starting_time" in info.data and v <= info.data["starting_time"]:
            raise ValueError("End time must be after start time")
        return v
    auction_id: int
    item_id: int
    name: str
    description: str
    price: float
    category: str
    condition: Conditions
    starting_time: datetime
    ending_time: datetime

class AucServe(BaseModel):
    starting_time: datetime
    ending_time: datetime

class AucServeUpdate(BaseModel):
    auction_id: int
    starting_time: Optional[datetime]
    ending_time: Optional[datetime]


class BidRequest(BaseModel):
    amount: float
    auction_id: int

class BidUpdate(BaseModel):
    amount: float



