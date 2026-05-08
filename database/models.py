from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Text, Integer, Float, Table
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from database.config import Base

# Association table for Workout-Exercise relationship
workout_exercise = Table(
    'workout_exercise',
    Base.metadata,
    Column('workout_id', String(36), ForeignKey('workouts.id'), primary_key=True),
    Column('exercise_id', String(36), ForeignKey('exercises.id'), primary_key=True),
)

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    fullname = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    workouts = relationship("Workout", back_populates="user", cascade="all, delete-orphan")
    history = relationship("WorkoutHistory", back_populates="user", cascade="all, delete-orphan")
    exercise_records = relationship("ExerciseRecord", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, fullname={self.fullname})>"


class Workout(Base):
    __tablename__ = "workouts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    exercises_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="workouts")
    exercises = relationship("Exercise", secondary=workout_exercise, backref="workouts")

    def __repr__(self):
        return f"<Workout(id={self.id}, title={self.title}, user_id={self.user_id})>"


class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)
    target_muscle = Column(String(100), nullable=True)
    difficulty = Column(String(50), default="intermediate")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    records = relationship("ExerciseRecord", back_populates="exercise", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Exercise(id={self.id}, name={self.name})>"


class ExerciseRecord(Base):
    __tablename__ = "exercise_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    exercise_id = Column(String(36), ForeignKey("exercises.id"), nullable=False)
    weight_kg = Column(Float, nullable=True)
    reps = Column(Integer, nullable=True)
    sets = Column(Integer, nullable=True)
    recorded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    notes = Column(Text, nullable=True)

    user = relationship("User", back_populates="exercise_records")
    exercise = relationship("Exercise", back_populates="records")

    def __repr__(self):
        return f"<ExerciseRecord(id={self.id}, user_id={self.user_id}, exercise_id={self.exercise_id})>"


class WorkoutHistory(Base):
    __tablename__ = "workout_history"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workout_id = Column(String(36), ForeignKey("workouts.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    completed_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    notes = Column(Text, nullable=True)

    workout = relationship("Workout")
    user = relationship("User", back_populates="history")

    def __repr__(self):
        return f"<WorkoutHistory(id={self.id}, workout_id={self.workout_id}, user_id={self.user_id})>"
