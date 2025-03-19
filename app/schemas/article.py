from typing import Optional, List, Any
from datetime import datetime
from pydantic import BaseModel

from app.schemas.category import Category
from app.schemas.tag import Tag
from app.schemas.user import User


# Shared properties
class ArticleBase(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    body: Optional[str] = None
    is_published: Optional[int] = 0


# Properties to receive via API on creation
class ArticleCreate(ArticleBase):
    title: str
    body: str
    description: Optional[str] = None
    category_ids: List[int] = []
    tag_ids: List[int] = []


# Properties to receive via API on update
class ArticleUpdate(ArticleBase):
    category_ids: Optional[List[int]] = None
    tag_ids: Optional[List[int]] = None


# Properties shared by models in DB
class ArticleInDBBase(ArticleBase):
    id: int
    title: str
    body: str
    owner_id: int
    is_published: int
    publication_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Properties to return via API
class Article(ArticleInDBBase):
    author: Optional[User] = None
    categories: List[Category] = []
    tags: List[Tag] = []


# Properties stored in DB
class ArticleInDB(ArticleInDBBase):
    pass 