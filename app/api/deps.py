from typing import Generator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.schemas.token import TokenPayload

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/login")


def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    """
    Validate the access token and return the current user.
    
    Args:
        db: Database session
        token: JWT token from the Authorization header
        
    Returns:
        User: The current authenticated user
        
    Raises:
        HTTPException: If the token is invalid or the user does not exist
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.id == token_data.sub).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Get the current active user.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User: The current active user
        
    Raises:
        HTTPException: If the user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def get_current_active_author(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Get the current active user with author privileges.
    
    Args:
        current_user: Current authenticated active user
        
    Returns:
        User: The current active user with author privileges
        
    Raises:
        HTTPException: If the user does not have author privileges
    """
    if current_user.role not in ["author", "editor", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


def get_current_active_editor(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Get the current active user with editor privileges.
    
    Args:
        current_user: Current authenticated active user
        
    Returns:
        User: The current active user with editor privileges
        
    Raises:
        HTTPException: If the user does not have editor privileges
    """
    if current_user.role not in ["editor", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


def get_current_active_admin(
    current_user: User = Depends(get_current_active_user),
) -> User:
    """
    Get the current active user with admin privileges.
    
    Args:
        current_user: Current authenticated active user
        
    Returns:
        User: The current active user with admin privileges
        
    Raises:
        HTTPException: If the user does not have admin privileges
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user 