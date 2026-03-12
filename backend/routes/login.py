from fastapi import APIRouter, Form
from fastapi.responses import FileResponse

router = APIRouter()

@router.get("/login-page")
async def login_page():
    """Serve login page from template"""
    return FileResponse("templates/login.html", media_type="text/html")

@router.post("/login")
async def login(email: str = Form(...), password: str = Form(...)):
    """
    Login endpoint - STUB LOGIC (not connected to DB yet)
    """
    # TODO: Database validation
    # TODO: Password verification
    # TODO: Session management
    
    return {
        "status": "login_attempted",
        "email": email,
        "message": "Login logic not connected yet"
    }
