from typing import Optional
from datetime import datetime
from pydantic import BaseModel


# Shared properties
class CategoryBase(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


# Properties to receive via API on creation
class CategoryCreate(CategoryBase):
    name: str
    description: Optional[str] = None


# Properties to receive via API on update
class CategoryUpdate(CategoryBase):
    pass


# Properties shared by models in DB
class CategoryInDBBase(CategoryBase):
    id: int
    name: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Properties to return via API
class Category(CategoryInDBBase):
    pass 