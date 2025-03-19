from typing import Optional
from datetime import datetime
from pydantic import BaseModel


# Shared properties
class TagBase(BaseModel):
    name: Optional[str] = None


# Properties to receive via API on creation
class TagCreate(TagBase):
    name: str


# Properties to receive via API on update
class TagUpdate(TagBase):
    pass


# Properties shared by models in DB
class TagInDBBase(TagBase):
    id: int
    name: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Properties to return via API
class Tag(TagInDBBase):
    pass 