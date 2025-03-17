from typing import Any, List

from fastapi import APIRouter, Depends, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.article import Article
from app.models.user import User
from app.schemas.article import Article as ArticleSchema

router = APIRouter()


@router.get("/", response_model=List[ArticleSchema])
def search_articles(
    *,
    db: Session = Depends(get_db),
    q: str = Query(..., min_length=1, description="Search query"),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Search articles by keyword in title, body, or author.
    
    Args:
        db: Database session
        q: Search query
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List[ArticleSchema]: List of matching articles
    """
    # Search in published articles only
    articles = (
        db.query(Article)
        .join(User, Article.author_id == User.id)
        .filter(
            Article.is_published == 1,
            or_(
                Article.title.ilike(f"%{q}%"),
                Article.body.ilike(f"%{q}%"),
                User.username.ilike(f"%{q}%"),
            ),
        )
        .order_by(Article.publication_date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return articles 