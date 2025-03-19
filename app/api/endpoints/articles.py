from typing import Any, List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import (
    get_db,
    get_current_active_user,
    get_current_active_author,
    get_current_active_editor,
)
from app.models.article import Article
from app.models.category import Category
from app.models.tag import Tag
from app.models.user import User
from app.schemas.article import Article as ArticleSchema, ArticleCreate, ArticleUpdate

router = APIRouter()


@router.get("/", response_model=List[ArticleSchema])
def read_articles(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    is_published: Optional[int] = 1,  # Default to published articles only
) -> Any:
    """
    Get list of articles.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        is_published: Filter by publication status (1 for published, 0 for drafts)
        
    Returns:
        List[ArticleSchema]: List of articles
    """
    # Query articles with filter
    articles = (
        db.query(Article)
        .filter(Article.is_published == is_published)
        .order_by(Article.publication_date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return articles


@router.post("/", response_model=ArticleSchema)
def create_article(
    *,
    db: Session = Depends(get_db),
    article_in: ArticleCreate,
    current_user: User = Depends(get_current_active_author),
) -> Any:
    """
    Create a new article.
    
    This endpoint allows authors, editors, and admins to create new articles.
    
    - **title**: Required. The title of the article.
    - **description**: Optional. A brief description or summary of the article.
    - **body**: Required. The main content of the article.
    - **is_published**: Optional. Publication status (0=draft, 1=published). Defaults to 0 (draft).
    - **category_ids**: Optional. List of category IDs to associate with the article.
    - **tag_ids**: Optional. List of tag IDs to associate with the article.
    
    When an article is published (is_published=1), the publication_date is automatically set.
    The created_at and updated_at fields are automatically set on creation.
    
    Permissions:
      - Authors: Can create articles
      - Editors: Can create articles
      - Admins: Can create articles
    
    Returns:
      - The created article with author, categories and tags information
    """
    # Create the article
    db_article = Article(
        title=article_in.title,
        description=article_in.description,
        body=article_in.body,
        owner_id=current_user.id,
        is_published=article_in.is_published,
    )
    
    # Set publication date if published
    if article_in.is_published == 1:
        db_article.publication_date = datetime.now()
    
    # Add categories
    if article_in.category_ids:
        categories = db.query(Category).filter(Category.id.in_(article_in.category_ids)).all()
        db_article.categories = categories
    
    # Add tags
    if article_in.tag_ids:
        tags = db.query(Tag).filter(Tag.id.in_(article_in.tag_ids)).all()
        db_article.tags = tags
    
    db.add(db_article)
    db.commit()
    db.refresh(db_article)
    return db_article


@router.get("/{article_id}", response_model=ArticleSchema)
def read_article(
    *,
    db: Session = Depends(get_db),
    article_id: int,
) -> Any:
    """
    Get an article by ID.
    
    This endpoint retrieves an article by its ID.
    
    - Published articles (is_published=1) are accessible to all users
    - Unpublished articles (is_published=0) are only accessible to:
      - The article author
      - Editors
      - Admins
    
    Returns:
      - The article with author, categories and tags information
        
    Raises:
      - 404: If article not found or user not authorized to view unpublished article
    """
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    
    # Check if article is published
    if article.is_published != 1:
        # Only allow access to unpublished articles for authenticated users
        try:
            current_user = get_current_active_user(db=db)
            # Check if user is author, editor, or admin
            if (current_user.id != article.owner_id and 
                current_user.role not in ["editor", "admin"]):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions"
                )
        except HTTPException:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Article not found"
            )
    
    return article


@router.put("/{article_id}", response_model=ArticleSchema)
def update_article(
    *,
    db: Session = Depends(get_db),
    article_id: int,
    article_in: ArticleUpdate,
    current_user: User = Depends(get_current_active_author),
) -> Any:
    """
    Update an article.
    
    This endpoint allows the article author, editors, and admins to update an existing article.
    
    - **title**: Optional. The title of the article.
    - **description**: Optional. A brief description or summary of the article.
    - **body**: Optional. The main content of the article.
    - **is_published**: Optional. Publication status (0=draft, 1=published).
    - **category_ids**: Optional. List of category IDs to associate with the article.
    - **tag_ids**: Optional. List of tag IDs to associate with the article.
    
    When an article is published (is_published=1), the publication_date is automatically set if not already set.
    The updated_at field is automatically updated.
    
    Permissions:
      - Authors: Can update their own articles
      - Editors: Can update any article
      - Admins: Can update any article
    
    Returns:
      - The updated article with author, categories and tags information
      
    Raises:
      - 404: If article not found
      - 403: If user not authorized
    """
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    
    # Check if user is authorized to update the article
    if (current_user.id != article.owner_id and 
        current_user.role not in ["editor", "admin"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Update article fields
    if article_in.title is not None:
        article.title = article_in.title
    if article_in.description is not None:
        article.description = article_in.description
    if article_in.body is not None:
        article.body = article_in.body
    
    # Handle publication status change
    if article_in.is_published is not None and article_in.is_published != article.is_published:
        article.is_published = article_in.is_published
        if article_in.is_published == 1 and not article.publication_date:
            article.publication_date = datetime.now()
    
    # Update categories if provided
    if article_in.category_ids is not None:
        categories = db.query(Category).filter(Category.id.in_(article_in.category_ids)).all()
        article.categories = categories
    
    # Update tags if provided
    if article_in.tag_ids is not None:
        tags = db.query(Tag).filter(Tag.id.in_(article_in.tag_ids)).all()
        article.tags = tags
    
    db.add(article)
    db.commit()
    db.refresh(article)
    return article


@router.delete("/{article_id}", response_model=ArticleSchema)
def delete_article(
    *,
    db: Session = Depends(get_db),
    article_id: int,
    current_user: User = Depends(get_current_active_editor),
) -> Any:
    """
    Delete an article.
    
    This endpoint allows editors and admins to delete an article.
    
    The deletion is permanent and will also remove all associated data like:
    - Category associations
    - Tag associations
    - Comments
    
    Permissions:
      - Editors: Can delete any article
      - Admins: Can delete any article
    
    Returns:
      - The deleted article with author, categories and tags information
        
    Raises:
      - 404: If article not found
    """
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    
    db.delete(article)
    db.commit()
    return article 