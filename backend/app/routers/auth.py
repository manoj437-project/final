from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from pydantic import BaseModel
import random
import time

from app.utils.email_service import send_welcome_email, send_otp_email

from app.database import get_db
from app.models import Student, Mentor
from app.schemas import (
    StudentRegister, StudentResponse, StudentLogin,
    MentorRegister, MentorResponse, MentorLogin, TokenResponse
)
from app.utils import verify_password, get_password_hash, create_access_token
from app.config import settings

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# HTTPBearer scheme handles parsing "Authorization: Bearer <JWT>"
security = HTTPBearer()

# In-memory OTP store: { email: { 'otp': str, 'expires': float, 'role': str } }
_otp_store: dict = {}


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    """Validates JWT and extracts the user context from database."""
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
        email_or_id: str = payload.get("sub")
        role: str = payload.get("role")
        if email_or_id is None or role is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    if role == "student":
        user = db.query(Student).filter(Student.email == email_or_id).first()
        if not user:
            raise credentials_exception
        return {"user": user, "role": "student"}
    elif role == "mentor":
        user = db.query(Mentor).filter(Mentor.identity == email_or_id).first()
        if not user:
            raise credentials_exception
        return {"user": user, "role": "mentor"}
    else:
        raise credentials_exception

def get_current_student(current_user: dict = Depends(get_current_user)) -> Student:
    """Dependency to check and return the authenticated Student."""
    if current_user["role"] != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden. Only students are authorized."
        )
    return current_user["user"]

def get_current_mentor(current_user: dict = Depends(get_current_user)) -> Mentor:
    """Dependency to check and return the authenticated Mentor."""
    if current_user["role"] != "mentor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden. Only mentors are authorized."
        )
    return current_user["user"]


# --- STUDENT ENDPOINTS ---

@router.post("/student/register", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def register_student(payload: StudentRegister, db: Session = Depends(get_db)):
    # Check if email is already taken
    existing_email = db.query(Student).filter(Student.email == payload.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration failed. Email is already registered."
        )

    # Check if regno is already taken
    existing_regno = db.query(Student).filter(Student.regno == payload.regno).first()
    if existing_regno:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration failed. Registration number is already registered."
        )

    # Create new student object
    hashed_pass = get_password_hash(payload.password)
    new_student = Student(
        username=payload.username,
        regno=payload.regno,
        dept=payload.dept,
        year=payload.year,
        email=payload.email,
        password_hash=hashed_pass
    )
    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    # Send welcome email in background (non-blocking)
    send_welcome_email(to_email=new_student.email, user_name=new_student.username)

    return new_student

@router.post("/student/login", response_model=TokenResponse)
def login_student(payload: StudentLogin, db: Session = Depends(get_db)):
    # Retrieve student
    student = db.query(Student).filter(Student.email == payload.email).first()
    if not student or not verify_password(payload.password, student.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password. Please check your credentials."
        )

    # Generate JWT
    token_data = {"sub": student.email, "role": "student"}
    access_token = create_access_token(data=token_data)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": "student",
        "name": student.username,
        "email_or_id": student.email,
        "year": student.year,
        "regno": student.regno
    }


# --- MENTOR ENDPOINTS ---

@router.post("/mentor/register", response_model=MentorResponse, status_code=status.HTTP_201_CREATED)
def register_mentor(payload: MentorRegister, db: Session = Depends(get_db)):
    # Check if identity is already taken
    existing_mentor = db.query(Mentor).filter(Mentor.identity == payload.identity).first()
    if existing_mentor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration failed. Mentor identity is already registered."
        )

    # Create new mentor object
    hashed_pass = get_password_hash(payload.password)
    new_mentor = Mentor(
        name=payload.name,
        dept=payload.dept,
        identity=payload.identity,
        password_hash=hashed_pass
    )
    db.add(new_mentor)
    db.commit()
    db.refresh(new_mentor)
    return new_mentor

@router.post("/mentor/login", response_model=TokenResponse)
def login_mentor(payload: MentorLogin, db: Session = Depends(get_db)):
    # Retrieve mentor
    mentor = db.query(Mentor).filter(Mentor.identity == payload.identity).first()
    if not mentor or not verify_password(payload.password, mentor.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid identity or password. Please check your credentials."
        )

    # Generate JWT
    token_data = {"sub": mentor.identity, "role": "mentor"}
    access_token = create_access_token(data=token_data)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": "mentor",
        "name": mentor.name,
        "email_or_id": mentor.identity
    }


# --- FORGOT / RESET PASSWORD ENDPOINTS ---

class ForgotPasswordRequest(BaseModel):
    email: str
    role: str  # 'student' or 'mentor'

class ResetPasswordRequest(BaseModel):
    email: str
    otp: str
    new_password: str
    role: str






@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Generates a 6-digit OTP and sends it to the user's registered email.
    Email is sent via background thread (Resend → SMTP fallback). Always returns success.
    """
    email = payload.email.strip().lower()

    # Verify the email exists in the database
    if payload.role == 'student':
        user = db.query(Student).filter(Student.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="No student account found with this email.")
        user_name = user.username
    elif payload.role == 'mentor':
        user = db.query(Mentor).filter(Mentor.identity == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="No mentor account found with this email.")
        user_name = user.name
    else:
        raise HTTPException(status_code=400, detail="Invalid role. Must be 'student' or 'mentor'.")

    # Generate 6-digit OTP with 10-minute expiry
    otp = str(random.randint(100000, 999999))
    expires = time.time() + 600  # 10 minutes
    _otp_store[email] = {'otp': otp, 'expires': expires, 'role': payload.role}

    # Fire OTP email in background (non-blocking — Resend → SMTP fallback)
    send_otp_email(to_email=email, user_name=user_name, otp_code=otp, role=payload.role)
    print(f"[EduMentor OTP] OTP queued for: {email} | Role: {payload.role}")

    return {
        "success": True,
        "message": f"OTP sent to {payload.email}. Please check your inbox (and spam folder)."
    }


@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Validates OTP and resets the user's password."""
    email = payload.email.strip().lower()

    stored = _otp_store.get(email)
    if not stored:
        raise HTTPException(status_code=400, detail="No OTP found. Please request a new OTP first.")

    if time.time() > stored['expires']:
        del _otp_store[email]
        raise HTTPException(status_code=400, detail="OTP has expired. Please request a new one.")

    if stored['otp'] != payload.otp.strip():
        raise HTTPException(status_code=400, detail="Invalid OTP. Please check and try again.")

    if len(payload.new_password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters.")

    # Update password in database
    new_hash = get_password_hash(payload.new_password)
    if payload.role == 'student':
        user = db.query(Student).filter(Student.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="Student not found.")
        user.password_hash = new_hash
    elif payload.role == 'mentor':
        user = db.query(Mentor).filter(Mentor.identity == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="Mentor not found.")
        user.password_hash = new_hash
    else:
        raise HTTPException(status_code=400, detail="Invalid role.")

    db.commit()

    # Remove used OTP
    del _otp_store[email]
    print(f"[EduMentor OTP] Password reset successful for: {email}")

    return {"success": True, "message": "Password reset successful! You can now login with your new password."}
