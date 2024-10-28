"""
Utility functions for generating short URLs. Uses a combination of 
letters and digits to create unique shortened URLs.
"""

import string
import random
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
import jwt, secrets
from pydantic import BaseModel
from sqlalchemy import select
from app.models import USER
from .db import async_session
from jose import JWTError, jwt

class TokenData(BaseModel):
    username: Optional[str] = None

# Generate a random key
SECRET_KEY  = secrets.token_urlsafe(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 100
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def generate_short_url(length) -> str:
    """Generates a random short URL."""
    # Choose random characters from ASCII letters and digits
    short_url = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    return short_url

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Define the function to decode the JWT token
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    # You might want to retrieve the user from the database here
    user = await get_user_name(token_data.username)  # Your function to fetch user
    if user is None:
        raise credentials_exception
    return user

# Make sure to implement the get_user_name function
async def get_user_name(username: str):
    async with async_session() as session:
        result = await session.execute(select(USER).filter_by(username=username))
        return result.scalar_one_or_none()