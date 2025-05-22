from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import RedirectResponse
from jose import jwt
from datetime import datetime, timedelta, UTC
import httpx
from .config import get_settings
import secrets
import urllib.parse

router = APIRouter()
settings = get_settings()

def generate_state():
    return secrets.token_urlsafe(32)

def create_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.now(UTC) + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

@router.get("/login")
async def login():
    state = generate_state()
    params = {
        "client_id": settings.CLIENT_ID,
        "redirect_uri": settings.REDIRECT_URI,
        "response_type": "code",
        "scope": " ".join(settings.SCOPES),
        "state": state,
        "access_type": "offline",
        "prompt": "consent"  # Force Google to show consent screen to get refresh token
    }
    
    # Construct the authorization URL
    auth_url = f"{settings.AUTH_URL}?{urllib.parse.urlencode(params)}"
    return RedirectResponse(url=auth_url)

@router.get("/callback")
async def callback(code: str, state: str):
    # Exchange code for tokens
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            settings.TOKEN_URL,
            data={
                "client_id": settings.CLIENT_ID,
                "client_secret": settings.CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": settings.REDIRECT_URI
            }
        )
        
        if token_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get access token")
        
        token_data = token_response.json()
        
        # Get user info from Google
        user_response = await client.get(
            settings.USER_INFO_URL,
            headers={"Authorization": f"Bearer {token_data['access_token']}"}
        )
        
        if user_response.status_code != 200:
            raise HTTPException(status_code=400, detail="Failed to get user info")
        
        user_data = user_response.json()
        
        # Create our own tokens
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        # Use Google's sub as our user identifier
        access_token = create_token(
            data={
                "sub": user_data["sub"],
                "type": "access",
                "email": user_data.get("email"),
                "name": user_data.get("name")
            },
            expires_delta=access_token_expires
        )
        
        refresh_token = create_token(
            data={
                "sub": user_data["sub"],
                "type": "refresh",
                "email": user_data.get("email")
            },
            expires_delta=refresh_token_expires
        )
        
        # Store Google's refresh token if provided
        google_refresh_token = token_data.get("refresh_token")
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user_info": {
                "sub": user_data["sub"],
                "email": user_data.get("email"),
                "name": user_data.get("name"),
                "picture": user_data.get("picture")
            }
        }

@router.post("/refresh")
async def refresh_token(refresh_token: str):
    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=400, detail="Invalid refresh token")
        
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=400, detail="Invalid refresh token")
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_token(
            data={
                "sub": user_id,
                "type": "access",
                "email": payload.get("email")
            },
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    except jwt.JWTError:
        raise HTTPException(status_code=400, detail="Invalid refresh token") 