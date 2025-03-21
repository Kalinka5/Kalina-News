from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.api.deps import get_db
from app.core.security import create_access_token, verify_password
from app.core.config import settings
from app.models.user import User
from app.schemas.token import Token

router = APIRouter()


@router.post("/login", response_model=Token, description="Use your **username or email** in the username field to log in")
def login_access_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    
    **Important**: Enter your username or email address in the username field.
    
    Args:
        db: Database session
        form_data: Form containing username (can be username or email) and password
        
    Returns:
        Token: Access token and token type
        
    Raises:
        HTTPException: If the username/email or password is incorrect
    """
    # Find the user by username or email (OAuth2 form uses username field for the login identifier)
    user = db.query(User).filter(
        or_(User.email == form_data.username, User.username == form_data.username)
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Verify the password
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if the user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Create the JWT token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    } 