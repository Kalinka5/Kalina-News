from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user, get_current_active_admin
from app.models.article import Article
from app.models.comment import Comment
from app.models.user import User
from app.schemas.comment import Comment as CommentSchema, CommentCreate

router = APIRouter()


@router.get("/articles/{article_id}/comments", response_model=List[CommentSchema])
def read_article_comments(
    *,
    db: Session = Depends(get_db),
    article_id: int = Path(..., gt=0),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Get comments for a specific article.
    
    Args:
        db: Database session
        article_id: Article ID
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List[CommentSchema]: List of comments
        
    Raises:
        HTTPException: If article not found
    """
    # Check if article exists
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    
    # Get comments for the article
    comments = (
        db.query(Comment)
        .filter(Comment.article_id == article_id)
        .order_by(Comment.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return comments


@router.post("/articles/{article_id}/comments", response_model=CommentSchema)
def create_comment(
    *,
    db: Session = Depends(get_db),
    article_id: int = Path(..., gt=0),
    comment_in: CommentCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Create a new comment for an article. Only authenticated users can access this endpoint.
    
    Args:
        db: Database session
        article_id: Article ID
        comment_in: Comment data to create
        current_user: Current authenticated active user
        
    Returns:
        CommentSchema: Created comment
        
    Raises:
        HTTPException: If article not found or not published
    """
    # Check if article exists and is published
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    
    # Check if article is published (only allow comments on published articles)
    if article.is_published != 1:
        # Allow authors, editors, and admins to comment on unpublished articles
        if (current_user.id != article.author_id and 
            current_user.role not in ["editor", "admin"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot comment on unpublished articles"
            )
    
    # Create the comment
    db_comment = Comment(
        content=comment_in.content,
        article_id=article_id,
        user_id=current_user.id,
    )
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


@router.delete("/{comment_id}", response_model=CommentSchema)
def delete_comment(
    *,
    db: Session = Depends(get_db),
    comment_id: int = Path(..., gt=0),
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Delete a comment. Only the comment owner, editors, and admins can access this endpoint.
    
    Args:
        db: Database session
        comment_id: Comment ID
        current_user: Current authenticated active user
        
    Returns:
        CommentSchema: Deleted comment
        
    Raises:
        HTTPException: If comment not found or user not authorized
    """
    # Get the comment
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    # Check if user is authorized to delete the comment
    if (comment.user_id != current_user.id and 
        current_user.role not in ["editor", "admin"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    db.delete(comment)
    db.commit()
    return comment 