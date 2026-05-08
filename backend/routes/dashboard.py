import os
import sys
from datetime import datetime
from pathlib import Path

# Add project root to sys.path so imports work from any directory
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import APIRouter, Form, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from database.config import get_db
from database.models import User, Workout, WorkoutHistory, ExerciseRecord

router = APIRouter()
BASE_DIR = PROJECT_ROOT
TEMPLATES_DIR = BASE_DIR / "frontend" / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"


def get_current_user(request: Request, db: Session):
    token = request.cookies.get("access_token")
    if not token:
        return None

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            return None

        return db.query(User).filter(User.id == user_id, User.is_active == True).first()
    except JWTError:
        return None


@router.get("/dashboard")
async def dashboard(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        response = RedirectResponse(url="/login-page", status_code=303)
        response.delete_cookie("access_token")
        return response

    workout_count = db.query(Workout).filter(Workout.user_id == user.id).count()
    completion_count = db.query(WorkoutHistory).filter(WorkoutHistory.user_id == user.id).count()
    exercise_count = db.query(ExerciseRecord).filter(ExerciseRecord.user_id == user.id).count()

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "user": user,
            "workout_count": workout_count,
            "completion_count": completion_count,
            "exercise_count": exercise_count,
        },
    )


@router.get("/workouts")
async def workouts(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        response = RedirectResponse(url="/login-page", status_code=303)
        response.delete_cookie("access_token")
        return response

    workouts = (
        db.query(Workout)
        .filter(Workout.user_id == user.id)
        .order_by(Workout.created_at.desc())
        .all()
    )

    return templates.TemplateResponse(
        "workouts.html",
        {"request": request, "user": user, "workouts": workouts},
    )


@router.get("/create-workout")
async def create_workout_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        response = RedirectResponse(url="/login-page", status_code=303)
        response.delete_cookie("access_token")
        return response

    return templates.TemplateResponse(
        "create_workout.html",
        {"request": request, "user": user, "error": None, "title": "", "description": "", "exercises": ""},
    )


@router.post("/create-workout")
async def create_workout(
    request: Request,
    title: str = Form(...),
    description: str = Form(""),
    exercises: str = Form(...),
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    if not user:
        response = RedirectResponse(url="/login-page", status_code=303)
        response.delete_cookie("access_token")
        return response

    if not title.strip() or not exercises.strip():
        return templates.TemplateResponse(
            "create_workout.html",
            {
                "request": request,
                "user": user,
                "error": "Title and exercises are required.",
                "title": title,
                "description": description,
                "exercises": exercises,
            },
            status_code=400,
        )

    new_workout = Workout(
        user_id=user.id,
        title=title.strip(),
        description=description.strip(),
        exercises_text=exercises.strip(),
    )
    db.add(new_workout)
    db.commit()
    db.refresh(new_workout)

    return RedirectResponse(url="/workouts", status_code=303)


@router.post("/complete-workout")
async def complete_workout(
    request: Request,
    workout_id: str = Form(...),
    notes: str = Form(""),
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    if not user:
        response = RedirectResponse(url="/login-page", status_code=303)
        response.delete_cookie("access_token")
        return response

    workout = (
        db.query(Workout)
        .filter(Workout.id == workout_id, Workout.user_id == user.id)
        .first()
    )
    if not workout:
        response = RedirectResponse(url="/workouts", status_code=303)
        return response

    history_entry = WorkoutHistory(
        workout_id=workout.id,
        user_id=user.id,
        completed_at=datetime.utcnow(),
        notes=notes.strip(),
    )
    db.add(history_entry)
    db.commit()

    return RedirectResponse(url="/history", status_code=303)


@router.get("/history")
async def history(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        response = RedirectResponse(url="/login-page", status_code=303)
        response.delete_cookie("access_token")
        return response

    entries = (
        db.query(WorkoutHistory)
        .filter(WorkoutHistory.user_id == user.id)
        .order_by(WorkoutHistory.completed_at.desc())
        .all()
    )

    return templates.TemplateResponse(
        "history.html",
        {"request": request, "user": user, "entries": entries},
    )


@router.get("/profile")
async def profile(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        response = RedirectResponse(url="/login-page", status_code=303)
        response.delete_cookie("access_token")
        return response

    return templates.TemplateResponse(
        "profile.html",
        {"request": request, "user": user, "error": None, "message": None},
    )


@router.post("/profile")
async def update_profile(
    request: Request,
    fullname: str = Form(...),
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    if not user:
        response = RedirectResponse(url="/login-page", status_code=303)
        response.delete_cookie("access_token")
        return response

    if not fullname.strip() or len(fullname.strip()) < 2:
        return templates.TemplateResponse(
            "profile.html",
            {
                "request": request,
                "user": user,
                "error": "Please enter a valid full name.",
                "message": None,
            },
            status_code=400,
        )

    user.fullname = fullname.strip()
    db.commit()
    db.refresh(user)

    return templates.TemplateResponse(
        "profile.html",
        {
            "request": request,
            "user": user,
            "error": None,
            "message": "Profile updated successfully.",
        },
    )
