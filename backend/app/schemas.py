from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime

# --- AUTH SCHEMAS ---

class StudentRegister(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    regno: str = Field(..., min_length=2, max_length=20)
    dept: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    year: str = Field(..., description="Year of study: '1', '2', '3'")

    @field_validator("year")
    @classmethod
    def year_must_be_valid(cls, v: str) -> str:
        if v not in ("1", "2", "3"):
            raise ValueError("Year must be '1', '2', or '3'")
        return v

class StudentResponse(BaseModel):
    id: int
    username: str
    regno: str
    dept: str
    year: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True

class StudentLogin(BaseModel):
    email: EmailStr
    password: str


class MentorRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    dept: str = Field(..., min_length=2, max_length=50)
    identity: str = Field(..., min_length=2, max_length=50, description="Email or unique alphanumeric ID")
    password: str = Field(..., min_length=6)

class MentorResponse(BaseModel):
    id: int
    name: str
    dept: str
    identity: str
    created_at: datetime

    class Config:
        from_attributes = True

class MentorLogin(BaseModel):
    identity: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    name: str
    email_or_id: str
    year: Optional[str] = None
    regno: Optional[str] = None


# --- TIMETABLE SCHEMAS ---

class DailyTopicCreate(BaseModel):
    year: str
    subject: str
    topic: str

class DailyTopicResponse(BaseModel):
    id: int
    year: str
    subject: str
    topic: str
    updated_at: datetime

    class Config:
        from_attributes = True


class WeeklyTimetableCell(BaseModel):
    day: str
    period: str
    subject: str
    topic: str

class WeeklyTimetableSave(BaseModel):
    year: str
    cells: List[WeeklyTimetableCell]


# --- STUDENT SCORES & ASSESSMENT SCHEMAS ---

class StudentScoreCreate(BaseModel):
    topic: str = Field(..., min_length=1)
    score: str
    percentage: int = Field(..., ge=0, le=100)
    date: str
    not_understood: bool = False  # True if student said they didn't understand

class StudentScoreResponse(BaseModel):
    id: int
    student_id: int
    topic: str
    score: str
    percentage: int
    date: str

    class Config:
        from_attributes = True


class CohortStudent(BaseModel):
    name: str
    regno: str
    topic: str
    status: str  # 'good', 'weak', 'missed'
    statusText: str

class CohortDashboardResponse(BaseModel):
    total: int
    weak: int
    missed: int
    students: List[CohortStudent]


# --- CHAT SCHEMAS ---

class ChatMessageCreate(BaseModel):
    sender: str  # 'student' or 'ai'
    message: str

class ChatMessageResponse(BaseModel):
    id: int
    sender: str
    message: str
    timestamp: datetime

    class Config:
        from_attributes = True


# --- CHATBOT RESPONSE SCHEMAS ---

class ChatQueryRequest(BaseModel):
    message: str
    topic: Optional[str] = None
    subject: Optional[str] = None
    mode: Optional[str] = None  # 'resources' for learning material fetch; None for normal tutoring

class ChatQueryResponse(BaseModel):
    response: str
    suggestions: List[str]


# --- SUBJECT & TIMETABLE SCHEMAS ---

class SubjectListResponse(BaseModel):
    year: str
    subjects: List[str]


# --- WEAK REPORT SCHEMAS ---

class WeakStudentItem(BaseModel):
    name: str
    regno: str
    topic: str
    score: str
    percentage: int
    date: str

class WeakReportResponse(BaseModel):
    year: str
    total_weak: int
    students: List[WeakStudentItem]


# --- MENTOR ACTION SCHEMAS ---

class MentorActionCreate(BaseModel):
    year: str
    action_type: str
    description: Optional[str] = None

class MentorActionResponse(BaseModel):
    id: int
    year: str
    action_type: str
    description: Optional[str]
    student_count: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


# --- STUDENT DETAIL SCHEMA ---

class StudentScoreHistory(BaseModel):
    topic: str
    score: str
    percentage: int
    date: str

class StudentDetailResponse(BaseModel):
    name: str
    regno: str
    dept: str
    year: str
    email: str
    scores: List[StudentScoreHistory]
    latest_status: str  # 'good', 'weak', 'missed'


# --- STUDENT SCORE LIST & QUIZ STATUS SCHEMAS ---

class StudentScoreListResponse(BaseModel):
    scores: List[StudentScoreHistory]
    total: int

class QuizStatusResponse(BaseModel):
    attempted: bool
    topic: Optional[str] = None
    date: Optional[str] = None
    score: Optional[str] = None
    percentage: Optional[int] = None


# --- AI QUIZ GENERATION SCHEMAS ---

class QuizCountsRequest(BaseModel):
    mcq: int = 3
    tf: int = 2
    fill: int = 1

class QuizGenerateRequest(BaseModel):
    topic: str
    subject: str = "Computer Science"
    counts: QuizCountsRequest = QuizCountsRequest()
    year: Optional[str] = None
    history_id: Optional[int] = None

class QuizQuestion(BaseModel):
    type: str           # 'MCQ', 'TF', 'Fill'
    q: str              # question text
    a: str              # correct answer
    options: Optional[List[str]] = None  # MCQ/TF choices

class QuizGenerateResponse(BaseModel):
    topic: str
    questions: List[QuizQuestion]
    generated_by: str = "gemini"   # "gemini" or "mentor"
    student_attempts: Optional[List[Dict[str, Any]]] = None


# --- AI LEARNING RESOURCES SCHEMAS ---

class LearningResourceItem(BaseModel):
    title: str
    url: str

class LearningResourcesResponse(BaseModel):
    topic: str
    youtube: List[LearningResourceItem]
    websites: List[LearningResourceItem]
    generated_by: str = "gemini"


# --- TOPIC HISTORY SCHEMAS ---

class TopicHistoryItem(BaseModel):
    id: int
    subject: str
    topic: str
    date: Optional[str]
    due_date: Optional[str]
    due_time: Optional[str]
    counts: Optional[dict]
    set_by: Optional[str]
    manual_questions: Optional[List[dict]] = None
    created_at: datetime

    class Config:
        from_attributes = True

class TopicHistoryResponse(BaseModel):
    year: str
    total: int
    history: List[TopicHistoryItem]


# --- TOPIC PERFORMANCE SCHEMAS ---

class TopicPerformanceStudent(BaseModel):
    name: str
    regno: str
    status: str          # 'good', 'weak', 'missed'
    score: Optional[str]
    percentage: Optional[int]
    answers: Optional[List[Dict[str, Any]]] = None
    attempted_at: Optional[str] = None

class TopicPerformanceResponse(BaseModel):
    year: str
    topic: str
    subject: str
    date: Optional[str] = None
    total: int
    attempted: int
    weak_count: int
    missed_count: int
    students: List[TopicPerformanceStudent]
    questions: Optional[List[Dict[str, Any]]] = None
    generated_by: Optional[str] = "gemini"


# --- SEND REPORT SCHEMA ---

class SendReportResponse(BaseModel):
    success: bool
    message: str
    mentor_email: Optional[str]
    year: str
    total_students: int
    weak_count: int
    missed_count: int


# --- QUIZ ATTEMPT SCHEMAS ---

class QuizAttemptAnswer(BaseModel):
    """A single Q&A record inside a quiz attempt."""
    q: str                         # question text
    type: str                      # 'MCQ', 'TF', 'Fill'
    options: Optional[List[str]] = None  # MCQ/TF options
    student_answer: str            # what the student typed/selected
    correct_answer: str            # correct answer
    is_correct: bool

class QuizAttemptCreate(BaseModel):
    """Payload sent by student when quiz is finished."""
    topic: str
    subject: str = "Computer Science"
    date: str                      # YYYY-MM-DD
    score: str                     # e.g. '4/5'
    percentage: int = Field(..., ge=0, le=100)
    answers: List[QuizAttemptAnswer]

class QuizAttemptResponse(BaseModel):
    """Returned by mentor when viewing a student's quiz answers."""
    found: bool
    topic: str
    subject: Optional[str] = None
    date: Optional[str] = None
    score: Optional[str] = None
    percentage: Optional[int] = None
    answers: Optional[List[QuizAttemptAnswer]] = None
    message: str = ""

