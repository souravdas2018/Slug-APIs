"""
CRUD functions for URL shortener service. Includes functions to create
and retrieve shortened URLs with appropriate error handling and logging.
"""
import logging
from fastapi import HTTPException
from sqlalchemy.future import select
from .models import URL, URL_TRACKING, USER
from .db import async_session
from .utils import *


async def sign_up(sign_up_data):
    try:
        # Check if username or email already exists in the database
        async with async_session() as session:
            result = await session.execute(select(USER).filter_by(username=sign_up_data.username))
            existing_url = result.scalar_one_or_none()
            if existing_url:
                logging.info(f"{sign_up_data.username} already exists.")
                raise HTTPException(status_code=409, detail="User with this username already exists")
            
            result = await session.execute(select(USER).filter_by(email=sign_up_data.email))
            existing_url = result.scalar_one_or_none()
            if existing_url:
                logging.info(f"{sign_up_data.email} already exists.")
                raise HTTPException(status_code=409, detail="User with this email already exists")

            # Insert new user data
            new_user = USER(
                username=sign_up_data.username,
                email=sign_up_data.email,
                hashed_password=get_password_hash(sign_up_data.password),
            )
            session.add(new_user)
            await session.commit()
    except Exception as e:
        logging.error(f"Error creating short URL: {e}")
        raise

async def get_user_name(name: str):
    try:
        async with async_session() as session:
            result = await session.execute(select(USER).filter_by(username=name))
            existing_user = result.scalar_one_or_none()
            return existing_user
    except Exception as e:
        logging.error(f"Error retrieving user: {e}")
        raise


async def create_short_url(original_url: str, id: int = None, custom_slug: str = None) -> tuple:
    """Creates and stores a shortened URL. Supports custom or auto-generated slugs, 
    with dynamic length adjustment."""
    try:
        # Check if the original URL already exists
        async with async_session() as session:
            result = await session.execute(select(URL).filter_by(original_url=original_url))
            existing_url = result.scalar_one_or_none()
            if existing_url:
                logging.info(f"Original URL {original_url} already exists with short URL {existing_url.slug_url}.")
                return existing_url.slug_url, True if custom_slug else False

        # If a custom slug is provided, check for its uniqueness
        if custom_slug:
            async with async_session() as session:
                result = await session.execute(select(URL).filter_by(slug_url=custom_slug))
                if result.scalar_one_or_none():
                    logging.warning(f"Custom slug '{custom_slug}' already exists")
                    raise HTTPException(status_code=409, detail="Custom slug already exists.")
            short_url = custom_slug
            async with async_session() as session:
                result = await session.execute(select(URL).filter_by(slug_url=short_url))
            is_custom = True
        else:
            # Generate a unique short URL with a dynamic length increase if needed
            slug_length = 10
            while True:
                short_url = generate_short_url(slug_length)
                async with async_session() as session:
                    result = await session.execute(select(URL).filter_by(slug_url=short_url))
                    if not result.scalar_one_or_none():  # Unique slug
                        break  # Exit loop if the short_url is unique
                slug_length += 1  # Increment slug length if no unique slug is found in this iteration
                logging.info(f"Increasing slug length to {slug_length} and retrying.")
            is_custom = False

        # Set the expiration date to 1 hour from now
        exp_at = datetime.utcnow() + timedelta(hours=1)
        # exp_at = datetime.utcnow() + timedelta(minutes=10)

        # Store the new short URL in the database
        async with async_session() as session:
            async with session.begin():
                new_url = URL(
                    original_url=original_url, 
                    slug_url=short_url, owner_id=id, expires_at=exp_at
                    )
                session.add(new_url)
                await session.commit()
            logging.info(f"Short URL created for {original_url} as {short_url} (Custom: {is_custom})")
        return short_url, is_custom

    except Exception as e:
        logging.error(f"Error creating short URL: {e}")
        raise


async def get_original_url(short_url: str):
    """Retrieves the original URL based on the shortened URL."""
    try:
        async with async_session() as session:
            result = await session.execute(select(URL).filter_by(slug_url=short_url))
            original_url = result.scalar_one_or_none()
            if original_url:
                logging.info(f"Original URL retrieved for {short_url}: {original_url.original_url}")
                return original_url.original_url  
            else:
                logging.warning(f"Short URL {short_url} not found")
                return None  
    except Exception as e:
        logging.error(f"Error retrieving original URL for {short_url}: {e}")
        raise

async def get_slud_id(short_url: str):
    try:
        async with async_session() as session:
            result = await session.execute(select(URL).filter_by(slug_url=short_url))
            existing_user = result.scalar_one_or_none()
            print(existing_user.id)
            return existing_user.id
    except Exception as e:
        logging.error(f"Error retrieving user: {e}")
        raise

async def get_expires_at(short_url: str):
    try:
        async with async_session() as session:
            result = await session.execute(select(URL).filter_by(slug_url=short_url))
            existing_user = result.scalar_one_or_none()
            return existing_user.expires_at
    except Exception as e:
        logging.error(f"Error retrieving user: {e}")
        raise

async def track_url_access(id: int):
    """Inserts a tracking record for the accessed URL."""
    try:
        async with async_session() as session:
            async with session.begin():
                tracking_entry = URL_TRACKING(url_id=id)  # Create a new tracking entry
                session.add(tracking_entry)  # Add it to the session
                await session.commit()  # Commit the transaction
                logging.info(f"Tracking entry created for URL ID: {id} at {datetime.utcnow()}")
    except Exception as e:
        logging.error(f"Error tracking URL access for URL ID {id}: {e}")
        raise