import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    regno = Column(String, unique=True, index=True, nullable=False)
    dept = Column(String, nullable=False)
    year = Column(String, nullable=False)  # '1', '2', '3'
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    scores = relationship("StudentScore", back_populates="student", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="student", cascade="all, delete-orphan")


class Mentor(Base):
    __tablename__ = "mentors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    dept = Column(String, nullable=False)
    identity = Column(String, unique=True, index=True, nullable=False)  # email or corporate ID
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class DailyTopic(Base):
    __tablename__ = "daily_topics"

    id = Column(Integer, primary_key=True, index=True)
    year = Column(String, unique=True, index=True, nullable=False)  # '1', '2', '3'
    subject = Column(String, nullable=False)
    topic = Column(String, nullable=False)
    counts = Column(JSON, nullable=True)
    date = Column(String, nullable=True)
    due_date = Column(String, nullable=True)   # e.g. "2026-08-15" (YYYY-MM-DD), None = today only
    due_time = Column(String, nullable=True)   # e.g. "15:30" (HH:MM 24h), None = no expiry
    manual_questions = Column(JSON, nullable=True)  # list of {type, q, a, options} set by mentor; None = AI-generated
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class WeeklyTimetable(Base):
    __tablename__ = "weekly_timetables"

    id = Column(Integer, primary_key=True, index=True)
    year = Column(String, index=True, nullable=False)  # '1', '2', '3'
    day = Column(String, nullable=False)  # 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'
    period = Column(String, nullable=False)  # 'P1', 'P2', 'P3', 'P4', 'P5'
    subject = Column(String, nullable=True)
    topic = Column(String, nullable=True)


class StudentScore(Base):
    __tablename__ = "student_scores"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    topic = Column(String, nullable=False)
    score = Column(String, nullable=False)  # e.g., "4/5"
    percentage = Column(Integer, nullable=False)  # e.g., 80
    date = Column(String, nullable=False)  # e.g., "7/20/2026"
    not_understood = Column(Boolean, default=False)  # True if student said "did not understand"
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    student = relationship("Student", back_populates="scores")


class BoringReport(Base):
    """Tracks students who found the class boring (triggers mentor email)."""
    __tablename__ = "boring_reports"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    topic = Column(String, nullable=False)
    date = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    student = relationship("Student")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    sender = Column(String, nullable=False)  # 'student' or 'ai'
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    student = relationship("Student", back_populates="chat_messages")


class MentorAction(Base):
    __tablename__ = "mentor_actions"

    id = Column(Integer, primary_key=True, index=True)
    mentor_id = Column(Integer, ForeignKey("mentors.id"), nullable=False)
    year = Column(String, nullable=False)  # '1', '2', '3'
    action_type = Column(String, nullable=False)  # 'alert_weak', 'email_inactive', 'generate_report'
    description = Column(Text, nullable=True)
    student_count = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    mentor = relationship("Mentor", backref="actions")


class TopicHistory(Base):
    """Immutable append-only log of every topic assignment.
    Unlike DailyTopic (which is upserted/overwritten), every call to
    set-today adds a new row here so full history is preserved."""
    __tablename__ = "topic_history"

    id = Column(Integer, primary_key=True, index=True)
    year = Column(String, index=True, nullable=False)   # '1', '2', '3'
    subject = Column(String, nullable=False)
    topic = Column(String, nullable=False)
    counts = Column(JSON, nullable=True)                 # {mcq, tf, fill, short}
    date = Column(String, nullable=True)                 # YYYY-MM-DD when assigned
    due_date = Column(String, nullable=True)
    due_time = Column(String, nullable=True)
    set_by = Column(String, nullable=True)               # mentor name
    manual_questions = Column(JSON, nullable=True)       # list of {type, q, a, options} set by mentor
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class SeederMeta(Base):
    """Tracks which seeders have already run, so they are never re-seeded
    even if the seeded rows are later deleted (e.g. mentor clears history)."""
    __tablename__ = "seeder_meta"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, nullable=False)   # e.g. 'topic_history_seeded'
    seeded_at = Column(DateTime, default=datetime.datetime.utcnow)


class QuizAttempt(Base):
    """
    Stores the full Q&A record for a single student quiz session.
    Each row = one completed quiz (topic + date + student).
    The 'answers' JSON column holds a list of:
      { q, type, student_answer, correct_answer, is_correct }
    """
    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    topic = Column(String, nullable=False)
    subject = Column(String, nullable=True)
    date = Column(String, nullable=False)          # YYYY-MM-DD
    score = Column(String, nullable=False)         # e.g. "4/5"
    percentage = Column(Integer, nullable=False)
    answers = Column(JSON, nullable=False)         # list of { q, type, student_answer, correct_answer, is_correct }
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relationships
    student = relationship("Student", backref="quiz_attempts")
