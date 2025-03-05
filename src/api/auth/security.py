from passlib.context import CryptContext
import datetime
from datetime import timedelta
from typing import Optional, Annotated, Dict
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
import secrets
from base64 import b64encode

from .database import get_user, is_token_blacklisted

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Generate secure random keys
def generate_secret_key() -> str:
    return b64encode(secrets.token_bytes(32)).decode()

# JWT settings
SECRET_KEY = generate_secret_key()  # For access tokens
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 5  # 5 minutes
REFRESH_TOKEN_EXPIRE_MINUTES = 5  # 5 minutes
REFRESH_SECRET_KEY = generate_secret_key()  # For refresh tokens

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: Dict) -> str:
    to_encode = data.copy()
    expire = datetime.datetime.now(datetime.UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: Dict) -> str:
    to_encode = data.copy()
    expire = datetime.datetime.now(datetime.UTC) + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, REFRESH_SECRET_KEY, algorithm=ALGORITHM)

def verify_refresh_token(token: str) -> Dict:
    try:
        # Decode and verify the token
        payload = jwt.decode(token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        
        # Check token type
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
            
        # Check expiration
        exp = payload.get("exp")
        if not exp:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has no expiration"
            )
            
        # Convert expiration time to datetime
        current_time = datetime.datetime.now(datetime.UTC).timestamp()
        # exp is already in epoch seconds, no need to convert
        time_difference = current_time - exp

        print(f"Current time: {current_time}")
        print(f"Expiration time: {exp}")
        print(f"Time difference: {time_difference} seconds")
        print(f"ACCESS_TOKEN_EXPIRE_MINUTES: {ACCESS_TOKEN_EXPIRE_MINUTES * 60} seconds")
        
        # Check if token has exceeded ACCESS_TOKEN_EXPIRE_MINUTES (in seconds)
        if time_difference > ACCESS_TOKEN_EXPIRE_MINUTES * 60:
            print("Token has expired. Exceeded ACCESS_TOKEN_EXPIRE_MINUTES")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token has expired. Exceeded {ACCESS_TOKEN_EXPIRE_MINUTES} minutes"
            )
            
        return payload
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate refresh token: {str(e)}"
        )

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)]
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if username is None or token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
            
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    user = get_user(username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user