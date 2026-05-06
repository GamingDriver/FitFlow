from fastapi import APIRouter, Form, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import jwt
from database.config import get_db
from database.models import User
from database.security import verify_password
import os

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# JWT configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7

def create_access_token(user_id: str):
    """Create JWT access token"""
    expire = datetime.utcnow() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode = {"sub": user_id, "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.get("/login-page")
async def login_page(request: Request):
    """Serve login page from template"""
    response = templates.TemplateResponse(
        "login.html",
        {"request": request, "error": None, "email": ""},
    )
    response.delete_cookie("access_token")
    return response

@router.post("/login")
async def login(
    request: Request,
    email: str = Form(...), 
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Login endpoint with full validation and database integration
    """
    # TODO 1: Database validation
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid email or password", "email": email},
            status_code=401,
        )
    
    # Check if user is active
    if not user.is_active:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "User account is inactive", "email": email},
            status_code=403,
        )
    
    # TODO 2: Password verification
    if not verify_password(password, user.password_hash):
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid email or password", "email": email},
            status_code=401,
        )
    
    # TODO 3: Session management
    access_token = create_access_token(str(user.id))
    
    # Redirect to dashboard
    response = RedirectResponse(url="/dashboard", status_code=303)
    response.set_cookie(key="access_token", value=access_token, httponly=True, max_age=604800)
    return response
