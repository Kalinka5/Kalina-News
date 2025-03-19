from typing import Optional
from datetime import datetime
from pydantic import BaseModel

from app.schemas.user import User


# Shared properties
class CommentBase(BaseModel):
    text: Optional[str] = None


# Properties to receive via API on creation
class CommentCreate(CommentBase):
    text: str
    article_id: int


# Properties shared by models in DB
class CommentInDBBase(CommentBase):
    id: int
    text: str
    article_id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Properties to return via API
class Comment(CommentInDBBase):
    user: Optional[User] = None 