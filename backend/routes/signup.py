from datetime import datetime, timedelta
import os
import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import APIRouter, Form, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from jose import jwt
from sqlalchemy.orm import Session

from database.config import get_db
from database.models import User
from database.security import hash_password

router = APIRouter()
BASE_DIR = PROJECT_ROOT
TEMPLATES_DIR = BASE_DIR / "frontend" / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

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


@router.get("/signup-page")
async def signup_page(request: Request):
    """Serve the signup page from the frontend templates."""
    response = templates.TemplateResponse(
        "signup.html",
        {"request": request, "error": None, "fullname": "", "email": ""},
    )
    response.delete_cookie("access_token")
    return response


@router.post("/signup")
async def signup(
    request: Request,
    fullname: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db),
):
    """
    Signup endpoint with validation, hashing, and database persistence.
    """
    if password != confirm_password:
        return templates.TemplateResponse(
            "signup.html",
            {"request": request, "error": "Passwords do not match", "fullname": fullname, "email": email},
            status_code=400,
        )

    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return templates.TemplateResponse(
            "signup.html",
            {"request": request, "error": "Email already registered", "fullname": fullname, "email": email},
            status_code=400,
        )

    if not fullname or len(fullname) < 2:
        return templates.TemplateResponse(
            "signup.html",
            {"request": request, "error": "Full name must be at least 2 characters", "fullname": fullname, "email": email},
            status_code=400,
        )

    if "@" not in email:
        return templates.TemplateResponse(
            "signup.html",
            {"request": request, "error": "Invalid email format", "fullname": fullname, "email": email},
            status_code=400,
        )

    if len(password) < 6:
        return templates.TemplateResponse(
            "signup.html",
            {"request": request, "error": "Password must be at least 6 characters", "fullname": fullname, "email": email},
            status_code=400,
        )

    password_hash = hash_password(password)
    try:
        new_user = User(fullname=fullname, email=email, password_hash=password_hash)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception:
        db.rollback()
        return templates.TemplateResponse(
            "signup.html",
            {"request": request, "error": "Error creating user account", "fullname": fullname, "email": email},
            status_code=500,
        )

    access_token = create_access_token(str(new_user.id))
    response = RedirectResponse(url="/dashboard", status_code=303)
    response.set_cookie(key="access_token", value=access_token, httponly=True, max_age=604800)
    return response
