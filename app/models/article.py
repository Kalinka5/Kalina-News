from sqlalchemy import Column, ForeignKey, String, Integer, Text, DateTime, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base

# Association tables for many-to-many relationships
article_categories = Table(
    "article_categories",
    Base.metadata,
    Column("article_id", Integer, ForeignKey("articles.id"), primary_key=True),
    Column("category_id", Integer, ForeignKey("categories.id"), primary_key=True)
)

article_tags = Table(
    "article_tags",
    Base.metadata,
    Column("article_id", Integer, ForeignKey("articles.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True)
)


class Article(Base):
    __tablename__ = "articles"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True, nullable=False)
    description = Column(String, nullable=True)
    body = Column(Text, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    is_published = Column(Integer, default=0, index=True)  # 0 for draft, 1 for published
    publication_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=True)
    
    # Relationships
    author = relationship("User", back_populates="articles", foreign_keys=[owner_id])
    comments = relationship("Comment", back_populates="article", cascade="all, delete-orphan")
    
    # Many-to-many relationships
    categories = relationship("Category", secondary=article_categories, backref="articles")
    tags = relationship("Tag", secondary=article_tags, backref="articles") 