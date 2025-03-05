from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from typing import Annotated
import sqlite3
import logging
from pydantic import BaseModel

from ..auth.models import Token, UserCreate, User
from ..auth.security import (
    verify_password, get_password_hash, 
    create_access_token, create_refresh_token,
    verify_refresh_token, get_current_user
)
from ..auth.database import get_user, create_user, blacklist_token

router = APIRouter(
    prefix="/auth",
    tags=["authentication"]
)

# Create a model for refresh token request
class RefreshRequest(BaseModel):
    refresh_token: str

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    user = get_user(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create both access and refresh tokens
    access_token = create_access_token(data={"sub": user["username"]})
    refresh_token = create_refresh_token(data={"sub": user["username"]})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_request: RefreshRequest):
    try:
        # Verify the refresh token from request body
        payload = verify_refresh_token(refresh_request.refresh_token)
        username = payload.get("sub")
        
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
            
        # Get user from database
        user = get_user(username)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
            
        # Create new tokens
        new_access_token = create_access_token(data={"sub": username})
        new_refresh_token = create_refresh_token(data={"sub": username})
        
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error refreshing token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not refresh token"
        )

@router.post("/register", response_model=User)
async def register_user(user: UserCreate):
    try:
        # Check if user exists
        if get_user(user.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        # Hash password
        hashed_password = get_password_hash(user.password)
        
        # Create user
        success = create_user(user.username, user.email, hashed_password)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not create user"
            )
        
        # Return user data
        return {
            "username": user.username,
            "email": user.email,
            "full_name": None,
            "disabled": False
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error creating user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@router.post("/logout")
async def logout(
    current_user: Annotated[User, Depends(get_current_user)],
    request: Request
):
    try:
        # Get the token from the authorization header
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid authorization header"
            )
        
        token = auth_header.split(" ")[1]
        
        # Add token to blacklist
        if blacklist_token(token):
            return {"message": "Successfully logged out"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token already invalidated"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error during logout: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )