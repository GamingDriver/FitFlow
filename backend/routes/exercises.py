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
from database.models import User, Exercise, ExerciseRecord, Workout

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


@router.get("/api/exercises")
async def get_exercises_api(db: Session = Depends(get_db)):
    exercises = db.query(Exercise).order_by(Exercise.name).all()
    return {"exercises": [{"id": e.id, "name": e.name, "description": e.description, "target_muscle": e.target_muscle, "difficulty": e.difficulty} for e in exercises]}


@router.get("/exercises")
async def browse_exercises(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        return RedirectResponse(url="/login-page", status_code=303)

    exercises = db.query(Exercise).order_by(Exercise.name).all()

    return templates.TemplateResponse(
        "browse_exercises.html",
        {"request": request, "user": user, "exercises": exercises},
    )


@router.get("/build-workout")
async def build_workout(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        response = RedirectResponse(url="/login-page", status_code=303)
        response.delete_cookie("access_token")
        return response

    exercises = db.query(Exercise).order_by(Exercise.name).all()

    return templates.TemplateResponse(
        "build_workout.html",
        {
            "request": request,
            "user": user,
            "exercises": exercises,
            "error": None,
            "title": "",
            "description": "",
            "selected_exercises": [],
        },
    )


@router.post("/build-workout")
async def save_built_workout(
    request: Request,
    title: str = Form(...),
    description: str = Form(""),
    exercise_ids: str = Form(""),
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    if not user:
        response = RedirectResponse(url="/login-page", status_code=303)
        response.delete_cookie("access_token")
        return response

    if not title.strip():
        exercises = db.query(Exercise).order_by(Exercise.name).all()
        return templates.TemplateResponse(
            "build_workout.html",
            {
                "request": request,
                "user": user,
                "exercises": exercises,
                "error": "Workout title is required.",
                "title": title,
                "description": description,
                "selected_exercises": [],
            },
            status_code=400,
        )

    if not exercise_ids.strip():
        exercises = db.query(Exercise).order_by(Exercise.name).all()
        return templates.TemplateResponse(
            "build_workout.html",
            {
                "request": request,
                "user": user,
                "exercises": exercises,
                "error": "Please select at least one exercise.",
                "title": title,
                "description": description,
                "selected_exercises": [],
            },
            status_code=400,
        )

    try:
        selected_ids = [eid.strip() for eid in exercise_ids.split(",") if eid.strip()]
        selected_exercises = db.query(Exercise).filter(Exercise.id.in_(selected_ids)).all()

        new_workout = Workout(
            user_id=user.id,
            title=title.strip(),
            description=description.strip(),
        )
        new_workout.exercise_list = selected_exercises
        db.add(new_workout)
        db.commit()
        db.refresh(new_workout)

        return RedirectResponse(url="/workouts", status_code=303)
    except Exception as e:
        exercises = db.query(Exercise).order_by(Exercise.name).all()
        return templates.TemplateResponse(
            "build_workout.html",
            {
                "request": request,
                "user": user,
                "exercises": exercises,
                "error": f"Error creating workout: {str(e)}",
                "title": title,
                "description": description,
                "selected_exercises": [],
            },
            status_code=500,
        )


@router.post("/record-exercise")
async def record_exercise(
    request: Request,
    exercise_id: str = Form(...),
    weight_kg: float = Form(...),
    reps: int = Form(...),
    sets: int = Form(...),
    notes: str = Form(""),
    db: Session = Depends(get_db),
):
    user = get_current_user(request, db)
    if not user:
        response = RedirectResponse(url="/login-page", status_code=303)
        response.delete_cookie("access_token")
        return response

    exercise = db.query(Exercise).filter(Exercise.id == exercise_id).first()
    if not exercise:
        return RedirectResponse(url="/exercises", status_code=303)

    record = ExerciseRecord(
        user_id=user.id,
        exercise_id=exercise_id,
        weight_kg=weight_kg,
        reps=reps,
        sets=sets,
        notes=notes.strip(),
    )
    db.add(record)
    db.commit()

    return RedirectResponse(url="/exercises", status_code=303)
