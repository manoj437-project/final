from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from typing import Optional, List
from jose import jwt

from app.database import get_db
from app.models import DailyTopic, WeeklyTimetable, Student, Mentor, TopicHistory
from app.routers.auth import get_current_mentor
from app.config import settings
from app.schemas import SubjectListResponse, TopicHistoryItem, TopicHistoryResponse

router = APIRouter(prefix="/api/timetable", tags=["Timetable"])

# Year-appropriate subjects
YEAR_SUBJECTS = {
    "1": [
        "Introduction to Programming",
        "Engineering Mathematics I",
        "Engineering Physics",
        "Engineering Chemistry",
        "Basic Electronics",
        "English Communication",
        "Engineering Graphics",
    ],
    "2": [
        "Data Structures & Algorithms",
        "Object Oriented Programming",
        "Digital Logic Design",
        "Engineering Mathematics II",
        "Computer Organization & Architecture",
        "Discrete Mathematics",
        "Database Management Systems",
    ],
    "3": [
        "Design & Analysis of Algorithms",
        "Operating Systems",
        "Computer Networks",
        "Software Engineering",
        "Artificial Intelligence",
        "Machine Learning",
        "Web Technologies",
    ],
}


def normalize_subject(raw: str, year: str) -> str:
    """Normalize a subject name to the canonical name in YEAR_SUBJECTS.
    E.g. 'Software engieering' -> 'Software Engineering'"""
    if not raw:
        return raw
    candidates = YEAR_SUBJECTS.get(year, [])
    trimmed = raw.strip()
    # Exact match (case-insensitive)
    for c in candidates:
        if c.lower() == trimmed.lower():
            return c
    # Fuzzy: strip non-alphanumeric, compare
    import re
    def clean(s): return re.sub(r'[^a-z0-9]', '', s.lower())
    raw_clean = clean(trimmed)
    for c in candidates:
        cc = clean(c)
        if cc == raw_clean or cc.startswith(raw_clean[:6]) or raw_clean.startswith(cc[:6]):
            return c
    return trimmed  # Return original if no match found


def get_year_from_auth_or_query(request: Request, year: Optional[str], db: Session) -> str:
    """Helper to determine the year from either a query parameter or the JWT auth header."""
    if year:
        return year

    # Try extracting year from the Authorization header if available
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=["HS256"])
            email_or_id = payload.get("sub")
            role = payload.get("role")
            if role == "student" and email_or_id:
                student = db.query(Student).filter(Student.email == email_or_id).first()
                if student:
                    return student.year
        except Exception:
            pass

    return "1"  # Default fallback


@router.get("/subjects", response_model=SubjectListResponse)
def get_subjects(year: Optional[str] = Query("1"), db: Session = Depends(get_db)):
    """Returns only the subjects that exist in the WeeklyTimetable for the given cohort year.
    This ensures the subject dropdown only shows subjects the mentor has actually set in the timetable."""
    target_year = year if year in YEAR_SUBJECTS else "1"

    # Fetch distinct non-empty subjects from the actual timetable rows
    rows = db.query(WeeklyTimetable.subject).filter(
        WeeklyTimetable.year == target_year,
        WeeklyTimetable.subject != None,
        WeeklyTimetable.subject != ""
    ).distinct().all()

    subjects = sorted({r.subject.strip() for r in rows if r.subject and r.subject.strip()})

    return SubjectListResponse(year=target_year, subjects=subjects)


@router.get("/topics")
def get_topics_for_subject(
    year: Optional[str] = Query("1"),
    subject: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """Returns only the topics for a specific subject from WeeklyTimetable.
    If no subject is given, returns all non-empty topics for the year."""
    target_year = year if year in YEAR_SUBJECTS else "1"

    query = db.query(WeeklyTimetable.topic).filter(
        WeeklyTimetable.year == target_year,
        WeeklyTimetable.topic != None,
        WeeklyTimetable.topic != ""
    )

    if subject and subject.strip():
        # Match subject case-insensitively
        subj_clean = subject.strip()
        query = query.filter(WeeklyTimetable.subject.ilike(subj_clean))

    rows = query.distinct().all()
    topics = sorted({r.topic.strip() for r in rows if r.topic and r.topic.strip()})

    return {"year": target_year, "subject": subject or "", "topics": topics}


@router.get("/get-today")
def get_today(request: Request, year: Optional[str] = Query(None), db: Session = Depends(get_db)):
    """Retrieves the current daily topic for the specified cohort year."""
    import datetime
    target_year = get_year_from_auth_or_query(request, year, db)
    today_str = datetime.date.today().isoformat()

    # 1. Check if there is an active daily topic override set for this year
    # NOTE: DailyTopic has a UNIQUE constraint on year — one record per cohort year.
    # We query by year only (not date) since set_today always upserts the same record.
    topic_record = db.query(DailyTopic).filter(
        DailyTopic.year == target_year
    ).first()

    if topic_record:
        # Calculate is_expired based on due_date + due_time
        is_expired = False
        due_time = topic_record.due_time  # e.g. "15:30"
        due_date = topic_record.due_date  # e.g. "2026-08-15"
        if due_time:
            now = datetime.datetime.now()
            try:
                h, m = map(int, due_time.split(":"))
                # Use due_date if set, otherwise use today's date
                if due_date:
                    try:
                        dy, dm, dd = map(int, due_date.split("-"))
                        due_dt = now.replace(year=dy, month=dm, day=dd, hour=h, minute=m, second=0, microsecond=0)
                    except Exception:
                        due_dt = now.replace(hour=h, minute=m, second=0, microsecond=0)
                else:
                    due_dt = now.replace(hour=h, minute=m, second=0, microsecond=0)
                is_expired = now > due_dt
            except Exception:
                pass

        return {
            "success": True,
            "data": {
                "subject": topic_record.subject,
                "topic": topic_record.topic,
                "counts": topic_record.counts,
                "date": topic_record.date,
                "due_date": due_date,
                "due_time": due_time,
                "is_expired": is_expired,
                "question_mode": "manual" if topic_record.manual_questions else "ai",
                "activated_at": topic_record.updated_at.isoformat() if topic_record.updated_at else None,
            }
        }

    # 2. If no override for today, fall back to the Weekly Timetable
    day_name = datetime.datetime.now().strftime("%a")
    if day_name not in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]:
        day_name = "Mon"  # Fallback to Monday on Sunday/weekends

    # Find first non-empty slot for today (any period with a subject)
    cell = db.query(WeeklyTimetable).filter(
        WeeklyTimetable.year == target_year,
        WeeklyTimetable.day == day_name,
        WeeklyTimetable.subject != None,
        WeeklyTimetable.subject != ""
    ).order_by(WeeklyTimetable.period).first()

    if cell and cell.subject:
        return {
            "success": True,
            "data": {
                "subject": cell.subject,
                "topic": cell.topic or "",
                "counts": {"mcq": 3, "tf": 2, "fill": 0, "shortanswer": 0},  # Default counts
                "date": today_str,
                "due_time": None,
                "is_expired": False,
            }
        }

    return {"success": True, "data": None}


def _notify_students_quiz_activated(db, year: str, subject: str, topic: str, due_date, due_time, date_str: str):
    """Emails all students of a cohort year when mentor activates a quiz.
    Contains topic, subject, deadline info — purely informational."""
    import smtplib, datetime
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText
    from app.config import settings

    YEAR_FULL = {'1': '1st Year', '2': '2nd Year', '3': '3rd Year'}
    year_label = YEAR_FULL.get(year, f'Year {year}')

    # Format deadline string
    deadline_str = ""
    if due_date and due_time:
        try:
            dt = datetime.datetime.strptime(f"{due_date} {due_time}", "%Y-%m-%d %H:%M")
            deadline_str = dt.strftime("%d %B %Y, %I:%M %p")
        except Exception:
            deadline_str = f"{due_date} {due_time}"
    elif due_time:
        deadline_str = f"Today by {due_time}"
    else:
        deadline_str = "Today"

    # Collect all students for this year
    try:
        students = db.query(Student).filter(Student.year == year).all()
    except Exception:
        return

    if not students:
        return

    html_body = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
  body {{ font-family: Arial, sans-serif; background: #f4f6fb; margin: 0; padding: 0; }}
  .container {{ max-width: 580px; margin: 30px auto; background: #fff; border-radius: 18px; overflow: hidden; box-shadow: 0 6px 32px rgba(0,0,0,0.10); }}
  .header {{ background: linear-gradient(135deg, #7C3AED, #EC4899); color: #fff; padding: 30px 36px; }}
  .header h1 {{ margin: 0 0 6px; font-size: 1.4rem; }}
  .header p {{ margin: 0; opacity: 0.88; font-size: 0.88rem; }}
  .body {{ padding: 28px 36px; font-size: 0.95rem; color: #111; line-height: 1.7; }}
  .info-box {{ background: #f0eeff; border: 1.5px solid #c4b5fd; border-radius: 12px; padding: 18px 22px; margin: 18px 0; }}
  .label {{ font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.07em; color: #7c3aed; margin-bottom: 3px; }}
  .value {{ font-size: 1rem; font-weight: 700; color: #1a1a2e; }}
  .deadline {{ background: #fff7ed; border: 1.5px solid #fdba74; border-radius: 12px; padding: 14px 20px; margin: 14px 0; }}
  .deadline .value {{ color: #c2410c; }}
  .footer {{ padding: 16px 36px; text-align: center; font-size: 0.75rem; color: #9ca3af; border-top: 1px solid #e5e7eb; }}
</style></head>
<body><div class="container">
  <div class="header">
    <h1>📋 Quiz Assigned — Action Required</h1>
    <p>EduMentor AI &nbsp;|&nbsp; {year_label} &nbsp;|&nbsp; {date_str}</p>
  </div>
  <div class="body">
    <p>Dear Student,</p>
    <p>Your mentor has conducted a quiz session. Please log in to <strong>EduMentor AI</strong> and complete your quiz before the deadline.</p>
    <div class="info-box">
      <div class="label">Subject</div>
      <div class="value">{subject}</div>
      <br>
      <div class="label">Topic</div>
      <div class="value">{topic}</div>
    </div>
    <div class="deadline">
      <div class="label">⏰ Deadline</div>
      <div class="value">{deadline_str}</div>
    </div>
    <p style="color:#6b7280;font-size:0.88rem">Please complete the quiz on time. Your performance will be reported to your mentor.</p>
  </div>
  <div class="footer">Auto-generated by EduMentor AI &middot; {year_label}</div>
</div></body></html>"""

    subject_line = f"[EduMentor AI] 📋 Quiz Assigned: {topic} ({subject}) — Deadline: {deadline_str}"

    for student in students:
        student_email = student.email
        if not student_email:
            continue
        sent = False
        if settings.RESEND_API_KEY:
            try:
                import urllib.request, json as _json
                req_payload = _json.dumps({
                    "from": settings.RESEND_FROM_EMAIL,
                    "to": [student_email],
                    "subject": subject_line,
                    "html": html_body
                }).encode()
                req = urllib.request.Request(
                    "https://api.resend.com/emails", data=req_payload,
                    headers={"Authorization": f"Bearer {settings.RESEND_API_KEY}", "Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=10) as resp:
                    if resp.status in (200, 201):
                        sent = True
            except Exception:
                pass
        if not sent and settings.SMTP_USER and settings.SMTP_PASS:
            try:
                msg = MIMEMultipart("alternative")
                msg["Subject"] = subject_line
                msg["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_USER}>"
                msg["To"] = student_email
                msg.attach(MIMEText(html_body, "html"))
                with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                    server.starttls()
                    server.login(settings.SMTP_USER, settings.SMTP_PASS)
                    server.sendmail(settings.SMTP_USER, [student_email], msg.as_string())
            except Exception:
                pass


@router.post("/set-today")
def set_today(
    payload: dict,  # Freeform dict to easily accept nested 'counts' and fields from frontend
    request: Request,
    year: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_mentor: Mentor = Depends(get_current_mentor)
):
    """Sets today's active topic for a cohort (mentors only)."""
    import datetime
    # Try getting the year from query, or payload body
    target_year = year or payload.get("year") or "1"
    today_str = datetime.date.today().isoformat()
    date_str = payload.get("date", today_str)

    subject = normalize_subject(payload.get("subject", ""), target_year)
    topic = payload.get("topic", "")
    counts = payload.get("counts", {})
    due_time = payload.get("due_time", None)   # e.g. "15:30" or None
    due_date = payload.get("due_date", None)   # e.g. "2026-08-15" or None
    manual_questions = payload.get("manual_questions", None)  # list of {type,q,a,options} or None

    # year column is UNIQUE — query by year only so we always update the same record
    topic_record = db.query(DailyTopic).filter(
        DailyTopic.year == target_year
    ).first()

    if not topic_record:
        topic_record = DailyTopic(
            year=target_year,
            subject=subject,
            topic=topic,
            counts=counts,
            date=date_str,
            due_date=due_date,
            due_time=due_time,
            manual_questions=manual_questions
        )
        db.add(topic_record)
    else:
        topic_record.subject = subject
        topic_record.topic = topic
        topic_record.counts = counts
        topic_record.date = date_str
        topic_record.due_date = due_date
        topic_record.due_time = due_time
        topic_record.manual_questions = manual_questions

    db.commit()

    # ── Append immutable history row ──────────────────────────────────────────
    history_row = TopicHistory(
        year=target_year,
        subject=subject,
        topic=topic,
        counts=counts,
        date=date_str,
        due_date=due_date,
        due_time=due_time,
        set_by=current_mentor.name if current_mentor else None,
        manual_questions=manual_questions,
    )
    db.add(history_row)
    db.commit()

    # ── Notify all students of this year about the new quiz (background thread) ──
    import threading
    threading.Thread(
        target=_notify_students_quiz_activated,
        args=(db, target_year, subject, topic, due_date, due_time, date_str),
        daemon=True
    ).start()

    return {
        "success": True,
        "message": f"Today's topic has been set for cohort year {target_year}."
    }


@router.delete("/clear-today")
def clear_today(
    request: Request,
    year: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_mentor: Mentor = Depends(get_current_mentor)
):
    """
    Mentor-only: immediately deactivates the current active topic for a cohort year.
    Instead of deleting the record (which would fall back to WeeklyTimetable on refresh),
    we mark it as expired by setting due_date to yesterday and due_time to '00:00'.
    This keeps is_expired=True permanently across page refreshes until a new topic is set.
    """
    import datetime as _dt
    target_year = year or "1"
    topic_record = db.query(DailyTopic).filter(
        DailyTopic.year == target_year
    ).first()

    if not topic_record:
        return {"success": True, "message": "No active topic to deactivate."}

    # Mark as permanently expired — yesterday's date + 00:00 time
    yesterday = (_dt.date.today() - _dt.timedelta(days=1)).isoformat()
    topic_record.due_date = yesterday
    topic_record.due_time = "00:00"
    db.commit()

    return {
        "success": True,
        "message": f"Active topic deactivated for cohort year {target_year}."
    }


@router.get("/weekly")
def get_weekly(request: Request, year: Optional[str] = Query(None), db: Session = Depends(get_db)):
    """Gets the weekly schedule cell values for the cohort."""
    target_year = get_year_from_auth_or_query(request, year, db)
    cells = db.query(WeeklyTimetable).filter(WeeklyTimetable.year == target_year).all()

    # Reconstruct into dictionary mapping (day + period) to data
    schedule = {}
    for cell in cells:
        key = f"{cell.day}-{cell.period}"
        schedule[key] = {
            "subject": cell.subject or "",
            "topic": cell.topic or ""
        }

    return {
        "success": True,
        "year": target_year,
        "schedule": schedule
    }


@router.post("/weekly")
def save_weekly(
    payload: dict,  # Accepting freeform dictionary containing year and schedule grid
    db: Session = Depends(get_db),
    current_mentor: Mentor = Depends(get_current_mentor)
):
    """Saves/Updates the weekly schedule grid (mentors only)."""
    target_year = payload.get("year", "1")
    schedule = payload.get("schedule", {})  # Keyed by "Mon-P1", "Tue-P2", etc.

    # Remove existing weekly slots for this year
    db.query(WeeklyTimetable).filter(WeeklyTimetable.year == target_year).delete()

    # Save new slots
    for key, val in schedule.items():
        if "-" not in key:
            continue
        day, period = key.split("-", 1)
        new_cell = WeeklyTimetable(
            year=target_year,
            day=day,
            period=period,
            subject=normalize_subject(val.get("subject", ""), target_year),
            topic=val.get("topic", "")
        )
        db.add(new_cell)

    db.commit()
    return {
        "success": True,
        "message": f"Weekly timetable saved for cohort year {target_year}."
    }


@router.get("/all-topics")
def get_all_topics(year: Optional[str] = Query("1"), db: Session = Depends(get_db)):
    """Returns all daily topics set for a cohort year (legacy, uses DailyTopic)."""
    records = db.query(DailyTopic).filter(
        DailyTopic.year == year
    ).order_by(DailyTopic.date.desc()).all()

    return {
        "success": True,
        "year": year,
        "topics": [
            {
                "subject": r.subject,
                "topic": r.topic,
                "date": r.date,
                "counts": r.counts
            }
            for r in records
        ]
    }


@router.get("/history", response_model=TopicHistoryResponse)
def get_topic_history(
    year: Optional[str] = Query("1", description="Cohort year"),
    limit: int = Query(50, description="Max records to return"),
    db: Session = Depends(get_db)
):
    """Returns the full immutable history of all topic assignments for a cohort year,
    newest first. Each set-today call appends a new row regardless of topic."""
    records = db.query(TopicHistory).filter(
        TopicHistory.year == year
    ).order_by(TopicHistory.created_at.desc()).limit(limit).all()

    items = [
        TopicHistoryItem(
            id=r.id,
            subject=r.subject,
            topic=r.topic,
            date=r.date,
            due_date=r.due_date,
            due_time=r.due_time,
            counts=r.counts,
            set_by=r.set_by,
            created_at=r.created_at,
        )
        for r in records
    ]
    return TopicHistoryResponse(year=year, total=len(items), history=items)


@router.delete("/history")
def delete_topic_history(
    year: Optional[str] = Query("1", description="Cohort year to clear history for"),
    db: Session = Depends(get_db),
    current_mentor: Mentor = Depends(get_current_mentor)
):
    """Permanently deletes all topic assignment history for the given cohort year.
    Only authenticated mentors can perform this action."""
    deleted_count = db.query(TopicHistory).filter(
        TopicHistory.year == year
    ).delete(synchronize_session=False)
    db.commit()
    return {
        "success": True,
        "deleted": deleted_count,
        "message": f"All history for year {year} has been permanently deleted."
    }
