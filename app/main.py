from contextvars import Token
from datetime import timedelta
import logging
from fastapi import Depends, FastAPI, HTTPException,  Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel  # Import BaseModel for request validation
from requests import request
from sqlalchemy.exc import IntegrityError
from .crud import (create_short_url, get_expires_at, 
                   get_original_url, get_slud_id, 
                   get_user_name, sign_up, track_url_access)
from .utils import *
from .db import init_db

app = FastAPI()

class URLRequest(BaseModel):
    """Pydantic model for URL request."""
    url: str
    slug: str | None = None

class SIGNUPRequest(BaseModel):
    """Pydantic model for SIGNUP request."""
    username: str
    email: str
    password: str

class LoginRequest(BaseModel):
    """Pydantic model for Login request."""
    username: str
    password: str

class Token(BaseModel):
    """Pydantic model for Token request."""
    access_token: str
    token_type: str

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    await init_db()

@app.post("/url/signup")
async def register(sign_request: SIGNUPRequest):       
        if not sign_request.username or not sign_request.email or not sign_request.password:
            raise HTTPException(status_code=400, detail="Username, email, and password cannot be empty.")
        signup_response = await sign_up(sign_request)
        return {"message": f"{sign_request.username} User created successfully"}

@app.post("/url/login/", response_model=Token)
async def login(request: Request, login_request: LoginRequest):
    username = login_request.username
    # Call the get_user_name function with the extracted username
    user = await get_user_name(username)
    if not verify_password(login_request.password, user.hashed_password):  # Assuming hashed_password is an attribute of user
        logging.warning("Password verification failed for user: %s", username)
        raise HTTPException(status_code=401, detail="Incorrect username or password.")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/url/shorten")
async def shorten_url(
    url_request: URLRequest, 
    request: Request,
    current_user: str = Depends(get_current_user)  # This ensures the user is authenticated
):  
    """API endpoint to shorten a URL with optional custom slug support."""
    try:
        if not url_request.url:
            logging.warning("Empty URL provided")
            raise HTTPException(status_code=400, detail="URL is required.")
        owner_id = current_user.id
        # Check for a custom slug or generate a unique one if slug is None or empty
        short_url, is_custom = await create_short_url(
            url_request.url, owner_id,
            url_request.slug if url_request.slug not in (None, "") else None
        )
        return {
            "short_url": f"http://{request.client.host}:{request.url.port}/r/{short_url}",
            "slug_type": "custom" if is_custom else "auto-generated"
        }
    except IntegrityError:
        logging.error("Database integrity error during URL shortening")
        raise HTTPException(status_code=409, detail="Failed to shorten URL due to a conflict in URL generation.")
    
    except Exception as e:
        logging.error(f"Failed to shorten URL: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred while shortening the URL.")


@app.get("/r/{short_url}")
async def redirect_url(
    request: Request, short_url: str 
    ):
    """API endpoint to resolve a short URL to its original form."""
    try:
        logging.info(f"Received request for short_url: {short_url}")
        original_url = await get_original_url(short_url)
        slug_id = await get_slud_id(short_url)
        if original_url is None:
            logging.warning(f"Short URL {short_url} not found")
            raise HTTPException(status_code=404, detail="URL not found.")
        # Log the access in the table
        await track_url_access(slug_id)
         # Check if the URL has expired
        expires_at=await get_expires_at(short_url)
        if expires_at < datetime.utcnow():
            logging.warning(f"Short URL {short_url} has expired")
            raise HTTPException(status_code=410, detail="This URL has expired.")
        
        return RedirectResponse(original_url, status_code=302)
    except HTTPException as e:
        raise e 
    except Exception as e:
        logging.error(f"Failed to resolve short URL {short_url}: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred while resolving the short URL.")


