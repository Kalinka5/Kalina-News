from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_admin
from app.models.category import Category
from app.schemas.category import Category as CategorySchema, CategoryCreate, CategoryUpdate

router = APIRouter()


@router.get("/", response_model=List[CategorySchema])
def read_categories(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Get list of categories.
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return
        
    Returns:
        List[CategorySchema]: List of categories
    """
    categories = db.query(Category).offset(skip).limit(limit).all()
    return categories


@router.post("/", response_model=CategorySchema)
def create_category(
    *,
    db: Session = Depends(get_db),
    category_in: CategoryCreate,
    current_user: Any = Depends(get_current_active_admin),
) -> Any:
    """
    Create a new category. Only admins can access this endpoint.
    
    Args:
        db: Database session
        category_in: Category data to create
        current_user: Current authenticated active admin user
        
    Returns:
        CategorySchema: Created category
        
    Raises:
        HTTPException: If category with same name already exists
    """
    # Check if category already exists
    category = db.query(Category).filter(Category.name == category_in.name).first()
    if category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category already exists"
        )
    
    # Create the category
    db_category = Category(name=category_in.name)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


@router.get("/{category_id}", response_model=CategorySchema)
def read_category(
    *,
    db: Session = Depends(get_db),
    category_id: int,
) -> Any:
    """
    Get a category by ID.
    
    Args:
        db: Database session
        category_id: Category ID
        
    Returns:
        CategorySchema: Category information
        
    Raises:
        HTTPException: If category not found
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return category


@router.put("/{category_id}", response_model=CategorySchema)
def update_category(
    *,
    db: Session = Depends(get_db),
    category_id: int,
    category_in: CategoryUpdate,
    current_user: Any = Depends(get_current_active_admin),
) -> Any:
    """
    Update a category. Only admins can access this endpoint.
    
    Args:
        db: Database session
        category_id: Category ID
        category_in: Category data to update
        current_user: Current authenticated active admin user
        
    Returns:
        CategorySchema: Updated category
        
    Raises:
        HTTPException: If category not found
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # Check if updated name already exists in another category
    if category_in.name and category_in.name != category.name:
        existing_category = db.query(Category).filter(Category.name == category_in.name).first()
        if existing_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category name already exists"
            )
    
    # Update the category
    if category_in.name:
        category.name = category_in.name
    
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.delete("/{category_id}", response_model=CategorySchema)
def delete_category(
    *,
    db: Session = Depends(get_db),
    category_id: int,
    current_user: Any = Depends(get_current_active_admin),
) -> Any:
    """
    Delete a category. Only admins can access this endpoint.
    
    Args:
        db: Database session
        category_id: Category ID
        current_user: Current authenticated active admin user
        
    Returns:
        CategorySchema: Deleted category
        
    Raises:
        HTTPException: If category not found
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    db.delete(category)
    db.commit()
    return category 