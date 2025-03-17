from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_admin
from app.models.tag import Tag
from app.schemas.tag import Tag as TagSchema, TagCreate, TagUpdate

router = APIRouter()


@router.get("/", response_model=List[TagSchema])
def read_tags(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Get list of tags.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List[TagSchema]: List of tags
    """
    tags = db.query(Tag).offset(skip).limit(limit).all()
    return tags


@router.post("/", response_model=TagSchema)
def create_tag(
    *,
    db: Session = Depends(get_db),
    tag_in: TagCreate,
    current_user: Any = Depends(get_current_active_admin),
) -> Any:
    """
    Create a new tag. Only admins can access this endpoint.
    
    Args:
        db: Database session
        tag_in: Tag data to create
        current_user: Current authenticated active admin user
        
    Returns:
        TagSchema: Created tag
        
    Raises:
        HTTPException: If tag with same name already exists
    """
    # Check if tag already exists
    tag = db.query(Tag).filter(Tag.name == tag_in.name).first()
    if tag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tag already exists"
        )
    
    # Create the tag
    db_tag = Tag(name=tag_in.name)
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag


@router.get("/{tag_id}", response_model=TagSchema)
def read_tag(
    *,
    db: Session = Depends(get_db),
    tag_id: int,
) -> Any:
    """
    Get a tag by ID.
    
    Args:
        db: Database session
        tag_id: Tag ID
        
    Returns:
        TagSchema: Tag information
        
    Raises:
        HTTPException: If tag not found
    """
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
    return tag


@router.put("/{tag_id}", response_model=TagSchema)
def update_tag(
    *,
    db: Session = Depends(get_db),
    tag_id: int,
    tag_in: TagUpdate,
    current_user: Any = Depends(get_current_active_admin),
) -> Any:
    """
    Update a tag. Only admins can access this endpoint.
    
    Args:
        db: Database session
        tag_id: Tag ID
        tag_in: Tag data to update
        current_user: Current authenticated active admin user
        
    Returns:
        TagSchema: Updated tag
        
    Raises:
        HTTPException: If tag not found
    """
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
    
    # Check if updated name already exists in another tag
    if tag_in.name and tag_in.name != tag.name:
        existing_tag = db.query(Tag).filter(Tag.name == tag_in.name).first()
        if existing_tag:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Tag name already exists"
            )
    
    # Update the tag
    if tag_in.name:
        tag.name = tag_in.name
    
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


@router.delete("/{tag_id}", response_model=TagSchema)
def delete_tag(
    *,
    db: Session = Depends(get_db),
    tag_id: int,
    current_user: Any = Depends(get_current_active_admin),
) -> Any:
    """
    Delete a tag. Only admins can access this endpoint.
    
    Args:
        db: Database session
        tag_id: Tag ID
        current_user: Current authenticated active admin user
        
    Returns:
        TagSchema: Deleted tag
        
    Raises:
        HTTPException: If tag not found
    """
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
    
    db.delete(tag)
    db.commit()
    return tag 