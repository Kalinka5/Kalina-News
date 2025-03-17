from sqlalchemy import Column, ForeignKey, String, Integer, Text, DateTime, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base

# Junction table for Article and Category (many-to-many)
article_category = Table(
    "article_category",
    Base.metadata,
    Column("article_id", Integer, ForeignKey("article.id"), primary_key=True),
    Column("category_id", Integer, ForeignKey("category.id"), primary_key=True)
)

# Junction table for Article and Tag (many-to-many)
article_tag = Table(
    "article_tag",
    Base.metadata,
    Column("article_id", Integer, ForeignKey("article.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tag.id"), primary_key=True)
)


class Article(Base):
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True, nullable=False)
    body = Column(Text, nullable=False)
    author_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    publication_date = Column(DateTime(timezone=True), nullable=True)  # null until published
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_published = Column(Integer, default=0)  # 0: draft, 1: published
    
    # Relationships
    author = relationship("User", back_populates="articles")
    categories = relationship("Category", secondary=article_category, back_populates="articles")
    tags = relationship("Tag", secondary=article_tag, back_populates="articles")
    comments = relationship("Comment", back_populates="article", cascade="all, delete-orphan") 