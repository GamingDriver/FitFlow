import os
import sys
from pathlib import Path

# Add project root to sys.path so we can import database and backend packages
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, FileResponse
from jose import jwt, JWTError

from database.config import SessionLocal, init_database
from database.models import User
from backend.routes import login, signup

BASE_DIR = PROJECT_ROOT
FRONTEND_DIR = BASE_DIR / "frontend"
STATIC_DIR = FRONTEND_DIR / "static"
TEMPLATE_DIR = FRONTEND_DIR / "templates"

app = FastAPI()

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

app.include_router(login.router)
app.include_router(signup.router)

init_database()

@app.get("/")
async def root():
    return RedirectResponse(url="/login-page")

@app.get("/dashboard")
async def dashboard(request: Request):
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
        str(TEMPLATE_DIR / "dashboard.html"),
        media_type="text/html",
        headers={"Cache-Control": "no-store, no-cache, must-revalidate, max-age=0"},
    )


@app.post("/logout")
async def logout():
    response = RedirectResponse(url="/login-page", status_code=303)
    response.delete_cookie("access_token")
    return response


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
