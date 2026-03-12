from fastapi import APIRouter, Form
from fastapi.responses import FileResponse

router = APIRouter()

@router.get("/signup-page")
async def signup_page():
    """Serve signup page from template"""
    return FileResponse("templates/signup.html", media_type="text/html")

@router.post("/signup")
async def signup(fullname: str = Form(...), email: str = Form(...), password: str = Form(...), confirm_password: str = Form(...)):
    """
    Signup endpoint - STUB LOGIC (not connected to DB yet)
    """
    # TODO: Validate password match
    # TODO: Check email uniqueness
    # TODO: Hash password
    # TODO: Create user in database
    # TODO: Session/JWT management
    
    return {
        "status": "signup_attempted",
        "fullname": fullname,
        "email": email,
        "message": "Signup logic not connected yet"
    }
