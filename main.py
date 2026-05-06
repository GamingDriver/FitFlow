from fastapi import FastAPI
from fastapi import Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, FileResponse
from jose import jwt, JWTError
from database.config import SessionLocal
from database.models import User
import os

app = FastAPI()

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"

# Mount static files (CSS, JS, images, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Import route modules
from routes import login, signup
app.include_router(login.router)
app.include_router(signup.router)

# Create tables at startup.
from database.config import init_database
init_database()

@app.get("/")
async def root():
    """Home page - redirect to login"""
    return RedirectResponse(url="/login-page")

@app.get("/dashboard")
async def dashboard(request: Request):
    """Main dashboard page after login"""
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/login-page", status_code=303)

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            response = RedirectResponse(url="/login-page", status_code=303)
            response.delete_cookie("access_token")
            return response

        db = SessionLocal()
        try:
            user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
        finally:
            db.close()

        if not user:
            response = RedirectResponse(url="/login-page", status_code=303)
            response.delete_cookie("access_token")
            return response
    except JWTError:
        response = RedirectResponse(url="/login-page", status_code=303)
        response.delete_cookie("access_token")
        return response

    return FileResponse(
        "templates/dashboard.html",
        media_type="text/html",
        headers={"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"},
    )


@app.post("/logout")
async def logout():
    """Terminate current session and clear auth cookie."""
    response = RedirectResponse(url="/login-page", status_code=303)
    response.delete_cookie("access_token")
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
