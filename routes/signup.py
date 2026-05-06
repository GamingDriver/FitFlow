from fastapi import APIRouter, Form, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import jwt
from database.config import get_db
from database.models import User
from database.security import hash_password
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

@router.get("/signup-page")
async def signup_page(request: Request):
    """Serve signup page from template"""
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
    db: Session = Depends(get_db)
):
    """
    Signup endpoint with full validation and database integration
    """
    # TODO 1: Validate password match
    if password != confirm_password:
        return templates.TemplateResponse(
            "signup.html",
            {"request": request, "error": "Passwords do not match", "fullname": fullname, "email": email},
            status_code=400,
        )
    
    # TODO 2: Check email uniqueness
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return templates.TemplateResponse(
            "signup.html",
            {"request": request, "error": "Email already registered", "fullname": fullname, "email": email},
            status_code=400,
        )
    
    # Validate fullname
    if not fullname or len(fullname) < 2:
        return templates.TemplateResponse(
            "signup.html",
            {"request": request, "error": "Full name must be at least 2 characters", "fullname": fullname, "email": email},
            status_code=400,
        )
    
    # Validate email format
    if "@" not in email:
        return templates.TemplateResponse(
            "signup.html",
            {"request": request, "error": "Invalid email format", "fullname": fullname, "email": email},
            status_code=400,
        )
    
    # Validate password strength
    if len(password) < 6:
        return templates.TemplateResponse(
            "signup.html",
            {"request": request, "error": "Password must be at least 6 characters", "fullname": fullname, "email": email},
            status_code=400,
        )
    
    # TODO 3: Hash password
    password_hash = hash_password(password)
    
    # TODO 4: Create user in database
    try:
        new_user = User(
            fullname=fullname,
            email=email,
            password_hash=password_hash
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception as e:
        db.rollback()
        return templates.TemplateResponse(
            "signup.html",
            {"request": request, "error": "Error creating user account", "fullname": fullname, "email": email},
            status_code=500,
        )
    
    # TODO 5: Session/JWT management
    access_token = create_access_token(str(new_user.id))
    
    # Redirect to dashboard
    response = RedirectResponse(url="/dashboard", status_code=303)
    response.set_cookie(key="access_token", value=access_token, httponly=True, max_age=604800)
    return response
