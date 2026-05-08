import os
import sys
from pathlib import Path

# Add project root to sys.path so we can import database and backend packages
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from database.config import SessionLocal, init_database
from backend.routes import login, signup, dashboard, exercises

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
app.include_router(dashboard.router)
app.include_router(exercises.router)

print("✓ All routers included successfully")

init_database()
print("✓ Database initialized")

# Seed exercises if not already present
def seed_exercises():
    db = SessionLocal()
    try:
        from database.models import Exercise
        
        if db.query(Exercise).count() == 0:
            default_exercises = [
                Exercise(
                    name="Push-ups",
                    description="Upper body strength exercise",
                    target_muscle="Chest, Shoulders, Triceps",
                    difficulty="beginner",
                ),
                Exercise(
                    name="Squats",
                    description="Lower body strength exercise",
                    target_muscle="Quadriceps, Glutes, Hamstrings",
                    difficulty="beginner",
                ),
                Exercise(
                    name="Pull-ups",
                    description="Upper body pulling exercise",
                    target_muscle="Back, Biceps",
                    difficulty="intermediate",
                ),
                Exercise(
                    name="Deadlifts",
                    description="Full body strength exercise",
                    target_muscle="Back, Glutes, Hamstrings",
                    difficulty="intermediate",
                ),
                Exercise(
                    name="Bench Press",
                    description="Upper body strength exercise",
                    target_muscle="Chest, Shoulders, Triceps",
                    difficulty="intermediate",
                ),
                Exercise(
                    name="Plank",
                    description="Core stability exercise",
                    target_muscle="Core, Shoulders",
                    difficulty="beginner",
                ),
                Exercise(
                    name="Dumbbell Rows",
                    description="Upper body pulling exercise",
                    target_muscle="Back, Biceps",
                    difficulty="intermediate",
                ),
                Exercise(
                    name="Lunges",
                    description="Lower body strength exercise",
                    target_muscle="Quadriceps, Glutes, Hamstrings",
                    difficulty="beginner",
                ),
                Exercise(
                    name="Leg Press",
                    description="Lower body strength exercise",
                    target_muscle="Quadriceps, Glutes",
                    difficulty="intermediate",
                ),
                Exercise(
                    name="Burpees",
                    description="Full body cardio exercise",
                    target_muscle="Full Body",
                    difficulty="intermediate",
                ),
            ]
            db.add_all(default_exercises)
            db.commit()
            print("✓ Exercise catalog seeded successfully")
    except Exception as e:
        print(f"⚠ Error seeding exercises: {e}")
    finally:
        db.close()


seed_exercises()

@app.get("/")
async def root():
    return RedirectResponse(url="/login-page")

@app.get("/api/test")
async def test_api():
    return {"status": "ok", "message": "API is working"}

@app.post("/logout")
async def logout():
    response = RedirectResponse(url="/login-page", status_code=303)
    response.delete_cookie("access_token")
    return response


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
