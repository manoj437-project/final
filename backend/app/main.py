from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn

from app.database import engine, Base, SessionLocal
from app.models import Student, StudentScore, Mentor, WeeklyTimetable, DailyTopic, MentorAction, TopicHistory, SeederMeta, QuizAttempt
from app.utils import get_password_hash
from app.routers.auth import router as auth_router
from app.routers.timetable import router as timetable_router
from app.routers.students import router as students_router
from app.routers.chat import router as chat_router
from app.scheduler import start_scheduler

# Create Database tables
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──────────────────────────────────────────────────────────────
    seed_database()
    scheduler = start_scheduler()
    yield
    # ── Shutdown ─────────────────────────────────────────────────────────────
    scheduler.shutdown(wait=False)


app = FastAPI(
    title="EduMentor AI API Backend",
    description="A robust FastAPI + PostgreSQL backend for student AI tutoring and mentor analytics dashboards.",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict this to list of origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router)
app.include_router(timetable_router)
app.include_router(students_router)
app.include_router(chat_router)


# ─────────────────────────────────────────────────────────────────────────────
# DATABASE AUTO-SEEDER
# ─────────────────────────────────────────────────────────────────────────────

def seed_database():
    db: Session = SessionLocal()
    try:
        _seed_students(db)
        _seed_mentors(db)
        _seed_timetables(db)
        _seed_topic_history(db)
    except Exception as e:
        print(f"[Seeder] Error: {e}")
        db.rollback()
    finally:
        db.close()


def _seed_students(db: Session):
    if db.query(Student).count() > 0:
        return
    print("[Seeder] Seeding students and scores...")

    default_pass = get_password_hash("password123")
    import datetime
    today = datetime.date.today().isoformat()

    # ── 1st Year Cohort ─────────────────────────────────────────────────────
    y1 = [
        Student(username="Arun Kumar",    regno="24CS001", dept="Computer Science", year="1", email="arun@edumentor.edu",    password_hash=default_pass),
        Student(username="Bhavya Raj",    regno="24CS002", dept="Computer Science", year="1", email="bhavya@edumentor.edu",  password_hash=default_pass),
        Student(username="Chitra Devi",   regno="24CS003", dept="Computer Science", year="1", email="chitra@edumentor.edu",  password_hash=default_pass),
        Student(username="Dinesh M",      regno="24CS004", dept="Computer Science", year="1", email="dinesh@edumentor.edu",  password_hash=default_pass),
        Student(username="Ezhil Arasi",   regno="24CS005", dept="Computer Science", year="1", email="ezhil@edumentor.edu",   password_hash=default_pass),
        Student(username="Fathima N",     regno="24CS006", dept="Computer Science", year="1", email="fathima@edumentor.edu", password_hash=default_pass),
        Student(username="Gowtham S",     regno="24CS007", dept="Computer Science", year="1", email="gowtham@edumentor.edu", password_hash=default_pass),
    ]

    # ── 2nd Year Cohort ─────────────────────────────────────────────────────
    y2 = [
        Student(username="Harini P",      regno="23CS001", dept="Computer Science", year="2", email="harini@edumentor.edu",  password_hash=default_pass),
        Student(username="Ilavarasan K",  regno="23CS002", dept="Computer Science", year="2", email="ilavar@edumentor.edu",  password_hash=default_pass),
        Student(username="Janani T",      regno="23CS003", dept="Computer Science", year="2", email="janani@edumentor.edu",  password_hash=default_pass),
        Student(username="Karthikeyan R", regno="23CS004", dept="Computer Science", year="2", email="karthik@edumentor.edu", password_hash=default_pass),
        Student(username="Lavanya V",     regno="23CS005", dept="Computer Science", year="2", email="lavanya@edumentor.edu", password_hash=default_pass),
        Student(username="Madhan B",      regno="23CS006", dept="Computer Science", year="2", email="madhan@edumentor.edu",  password_hash=default_pass),
        Student(username="Nandhini C",    regno="23CS007", dept="Computer Science", year="2", email="nandhini@edumentor.edu",password_hash=default_pass),
    ]

    # ── 3rd Year Cohort ─────────────────────────────────────────────────────
    y3 = [
        Student(username="Oviya S",       regno="22CS001", dept="Computer Science", year="3", email="oviya@edumentor.edu",   password_hash=default_pass),
        Student(username="Praveen G",     regno="22CS002", dept="Computer Science", year="3", email="praveen@edumentor.edu", password_hash=default_pass),
        Student(username="Ranjitha M",    regno="22CS003", dept="Computer Science", year="3", email="ranjitha@edumentor.edu",password_hash=default_pass),
        Student(username="Surya Kumar",   regno="22CS004", dept="Computer Science", year="3", email="surya@edumentor.edu",   password_hash=default_pass),
        Student(username="Thenmozhi A",   regno="22CS005", dept="Computer Science", year="3", email="thenmo@edumentor.edu",  password_hash=default_pass),
        Student(username="Uma Devi",      regno="22CS006", dept="Computer Science", year="3", email="uma@edumentor.edu",     password_hash=default_pass),
        Student(username="Vasanth P",     regno="22CS007", dept="Computer Science", year="3", email="vasanth@edumentor.edu", password_hash=default_pass),
    ]

    db.add_all(y1 + y2 + y3)
    db.commit()

    # ── Scores ─────────────────────────────────────────────────────────────
    # Year 1 scores (varied: good, weak, missed)
    scores = [
        # Arun → good (80%)
        StudentScore(student_id=y1[0].id, topic="Variables & Data Types 📦", score="4/5", percentage=80, date=today),
        # Bhavya → weak (35%)
        StudentScore(student_id=y1[1].id, topic="Loops & Iteration 🔄",       score="2/5", percentage=35, date=today),
        # Chitra → good (90%)
        StudentScore(student_id=y1[2].id, topic="Functions & Scope 🧩",        score="5/5", percentage=90, date=today),
        # Dinesh → weak (40%)
        StudentScore(student_id=y1[3].id, topic="Arrays & Strings 📚",         score="2/5", percentage=40, date=today),
        # Ezhil → good (75%)
        StudentScore(student_id=y1[4].id, topic="Conditional Statements ❓",   score="3/4", percentage=75, date=today),
        # Fathima → no score (missed)
        # Gowtham → good (85%)
        StudentScore(student_id=y1[6].id, topic="Input/Output Basics 💻",       score="4/5", percentage=85, date=today),

        # Year 2 scores
        # Harini → good (88%)
        StudentScore(student_id=y2[0].id, topic="Linked Lists 🔗",             score="5/5", percentage=88, date=today),
        # Ilavarasan → weak (30%)
        StudentScore(student_id=y2[1].id, topic="Binary Trees 🌳",             score="2/5", percentage=30, date=today),
        # Janani → good (92%)
        StudentScore(student_id=y2[2].id, topic="Hashing Algorithms 🔐",       score="5/5", percentage=92, date=today),
        # Karthik → weak (45%)
        StudentScore(student_id=y2[3].id, topic="Graph BFS/DFS 🗺️",           score="2/4", percentage=45, date=today),
        # Lavanya → good (78%)
        StudentScore(student_id=y2[4].id, topic="Stack & Queue 📥",             score="4/5", percentage=78, date=today),
        # Madhan → no score (missed)
        # Nandhini → good (82%)
        StudentScore(student_id=y2[6].id, topic="Sorting Algorithms ⚡",        score="4/5", percentage=82, date=today),

        # Year 3 scores
        # Oviya → good (94%)
        StudentScore(student_id=y3[0].id, topic="Neural Networks 🧠",          score="5/5", percentage=94, date=today),
        # Praveen → weak (28%)
        StudentScore(student_id=y3[1].id, topic="Backtracking Algorithms 🔙",  score="1/5", percentage=28, date=today),
        # Ranjitha → good (86%)
        StudentScore(student_id=y3[2].id, topic="Dynamic Programming 🏗️",     score="4/5", percentage=86, date=today),
        # Surya → weak (42%)
        StudentScore(student_id=y3[3].id, topic="NP-Completeness 🤯",          score="2/5", percentage=42, date=today),
        # Thenmozhi → good (76%)
        StudentScore(student_id=y3[4].id, topic="Network Security 🛡️",        score="4/5", percentage=76, date=today),
        # Uma → no score (missed)
        # Vasanth → good (88%)
        StudentScore(student_id=y3[6].id, topic="Cloud Architecture ☁️",       score="4/5", percentage=88, date=today),
    ]

    db.add_all(scores)
    db.commit()
    print("[Seeder] Students and scores seeded successfully.")


def _seed_mentors(db: Session):
    if db.query(Mentor).count() > 0:
        return
    print("[Seeder] Seeding mentors...")
    mentor_pass = get_password_hash("password123")
    # NOTE: These are only created on a completely fresh database.
    # priya@edumentor.edu was removed — it was a fake address that always bounced.
    mentors = [
        Mentor(name="Prof. Senthil Kumar", dept="Computer Science", identity="senthil@edumentor.edu", password_hash=mentor_pass),
        Mentor(name="Dr. Meena Lakshmi",  dept="Computer Science", identity="meena@edumentor.edu",   password_hash=mentor_pass),
    ]
    db.add_all(mentors)
    db.commit()
    print("[Seeder] Mentors seeded successfully.")


def _seed_timetables(db: Session):
    if db.query(WeeklyTimetable).count() > 0:
        return
    print("[Seeder] Seeding weekly timetables...")

    DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]

    # ── Year 1 Timetable ────────────────────────────────────────────────────
    y1_schedule = {
        "Mon": [
            ("Intro to Programming",       "Variables & Data Types"),
            ("Engineering Mathematics I",  "Sets & Relations"),
            ("Engineering Physics",        "Mechanics Basics"),
            ("English Communication",      "Technical Writing"),
            ("Engineering Graphics",       "Orthographic Projection"),
        ],
        "Tue": [
            ("Intro to Programming",       "Control Flow & Loops"),
            ("Engineering Chemistry",      "Atomic Structure"),
            ("Engineering Mathematics I",  "Functions & Limits"),
            ("Basic Electronics",          "Semiconductor Basics"),
            ("English Communication",      "Presentation Skills"),
        ],
        "Wed": [
            ("Engineering Graphics",       "Isometric Drawing"),
            ("Intro to Programming",       "Functions & Recursion"),
            ("Engineering Physics",        "Optics & Waves"),
            ("Engineering Mathematics I",  "Differentiation"),
            ("Basic Electronics",          "Diodes & Transistors"),
        ],
        "Thu": [
            ("Intro to Programming",       "Arrays & Strings"),
            ("Engineering Chemistry",      "Chemical Bonding"),
            ("Engineering Mathematics I",  "Integration Basics"),
            ("English Communication",      "Group Discussion"),
            ("Engineering Physics",        "Electrostatics"),
        ],
        "Fri": [
            ("Intro to Programming",       "Pointers & Memory"),
            ("Engineering Mathematics I",  "Matrices & Determinants"),
            ("Basic Electronics",          "Logic Gates"),
            ("Engineering Graphics",       "CAD Introduction"),
            ("Engineering Chemistry",      "Organic Chemistry"),
        ],
        "Sat": [
            ("Intro to Programming",       "Lab: Mini Project"),
            ("Engineering Physics",        "Lab: Optics Experiment"),
            ("Basic Electronics",          "Lab: Circuit Design"),
            ("",                           ""),
            ("",                           ""),
        ],
    }

    # ── Year 2 Timetable ────────────────────────────────────────────────────
    y2_schedule = {
        "Mon": [
            ("Data Structures & Algorithms", "Arrays & Linked Lists"),
            ("Object Oriented Programming",  "Classes & Objects"),
            ("Digital Logic Design",         "Combinational Circuits"),
            ("Discrete Mathematics",         "Propositional Logic"),
            ("Database Management Systems",  "ER Diagrams"),
        ],
        "Tue": [
            ("Data Structures & Algorithms", "Stacks & Queues"),
            ("Computer Organization",        "ALU Design"),
            ("Object Oriented Programming",  "Inheritance"),
            ("Discrete Mathematics",         "Graph Theory"),
            ("Digital Logic Design",         "Sequential Circuits"),
        ],
        "Wed": [
            ("Database Management Systems",  "SQL Basics"),
            ("Data Structures & Algorithms", "Trees & Binary Search"),
            ("Object Oriented Programming",  "Polymorphism"),
            ("Computer Organization",        "Memory Hierarchy"),
            ("Discrete Mathematics",         "Combinatorics"),
        ],
        "Thu": [
            ("Data Structures & Algorithms", "Hashing & Heaps"),
            ("Database Management Systems",  "Normalization"),
            ("Digital Logic Design",         "Finite State Machines"),
            ("Object Oriented Programming",  "Abstract Classes"),
            ("Computer Organization",        "Instruction Set Architecture"),
        ],
        "Fri": [
            ("Data Structures & Algorithms", "Graphs BFS & DFS"),
            ("Database Management Systems",  "Transactions & ACID"),
            ("Object Oriented Programming",  "Design Patterns"),
            ("Discrete Mathematics",         "Recurrence Relations"),
            ("Computer Organization",        "Pipelining"),
        ],
        "Sat": [
            ("Data Structures & Algorithms", "Lab: Sorting Algorithms"),
            ("Database Management Systems",  "Lab: SQL Queries"),
            ("Object Oriented Programming",  "Lab: Mini OOP Project"),
            ("",                             ""),
            ("",                             ""),
        ],
    }

    # ── Year 3 Timetable ────────────────────────────────────────────────────
    y3_schedule = {
        "Mon": [
            ("Design & Analysis of Algorithms", "Divide & Conquer"),
            ("Operating Systems",               "Process Scheduling"),
            ("Computer Networks",               "OSI Model"),
            ("Artificial Intelligence",         "Search Algorithms"),
            ("Machine Learning",                "Linear Regression"),
        ],
        "Tue": [
            ("Design & Analysis of Algorithms", "Dynamic Programming"),
            ("Computer Networks",               "TCP/IP Protocol"),
            ("Operating Systems",               "Memory Management"),
            ("Machine Learning",                "Classification Algorithms"),
            ("Software Engineering",            "SDLC Models"),
        ],
        "Wed": [
            ("Artificial Intelligence",         "Knowledge Representation"),
            ("Design & Analysis of Algorithms", "Greedy Algorithms"),
            ("Computer Networks",               "Routing Protocols"),
            ("Software Engineering",            "UML & Design Diagrams"),
            ("Machine Learning",                "Neural Networks Basics"),
        ],
        "Thu": [
            ("Design & Analysis of Algorithms", "NP Completeness"),
            ("Operating Systems",               "File Systems"),
            ("Computer Networks",               "Network Security"),
            ("Machine Learning",                "Clustering Algorithms"),
            ("Artificial Intelligence",         "Expert Systems"),
        ],
        "Fri": [
            ("Web Technologies",                "REST API Design"),
            ("Design & Analysis of Algorithms", "Approximation Algorithms"),
            ("Machine Learning",                "Deep Learning Intro"),
            ("Software Engineering",            "Testing & QA"),
            ("Computer Networks",               "Wireless Networks"),
        ],
        "Sat": [
            ("Machine Learning",                "Lab: Model Training"),
            ("Computer Networks",               "Lab: Packet Analysis"),
            ("Software Engineering",            "Lab: Project Review"),
            ("",                                ""),
            ("",                                ""),
        ],
    }

    periods = ["P1", "P2", "P3", "P4", "P5"]
    all_cells = []

    for year, schedule in [("1", y1_schedule), ("2", y2_schedule), ("3", y3_schedule)]:
        for day in DAYS:
            day_slots = schedule.get(day, [])
            for i, period in enumerate(periods):
                if i < len(day_slots):
                    subj, topic = day_slots[i]
                else:
                    subj, topic = "", ""
                all_cells.append(WeeklyTimetable(
                    year=year,
                    day=day,
                    period=period,
                    subject=subj,
                    topic=topic
                ))

    db.add_all(all_cells)
    db.commit()
    print("[Seeder] Weekly timetables seeded successfully.")

def _seed_topic_history(db: Session):
    """Seeds past topic assignment history for all 3 years so the history panel shows data.
    Uses SeederMeta flag so this runs ONLY ONCE — even if the mentor later clears history.
    """
    SEED_KEY = "topic_history_seeded"
    # Check permanent flag — not row count (count can be 0 after mentor deletes history)
    already_seeded = db.query(SeederMeta).filter(SeederMeta.key == SEED_KEY).first()
    if already_seeded:
        return
    print("[Seeder] Seeding topic history...")
    import datetime

    # Build dates for the past 7 days
    today = datetime.date.today()
    dates = [(today - datetime.timedelta(days=i)).isoformat() for i in range(6, 0, -1)]

    history_entries = [
        # ── Year 1 history ──────────────────────────────────────────────
        TopicHistory(year="1", subject="Introduction to Programming",      topic="Variables & Data Types",   counts={"mcq":3,"tf":2,"fill":0,"short":0}, date=dates[0], set_by="Dr. Priya Rajan"),
        TopicHistory(year="1", subject="Engineering Mathematics I",         topic="Sets & Relations",          counts={"mcq":3,"tf":2,"fill":0,"short":0}, date=dates[1], set_by="Dr. Priya Rajan"),
        TopicHistory(year="1", subject="Introduction to Programming",      topic="Control Flow & Loops",      counts={"mcq":3,"tf":2,"fill":1,"short":0}, date=dates[2], set_by="Prof. Senthil Kumar"),
        TopicHistory(year="1", subject="Engineering Physics",              topic="Optics & Waves",             counts={"mcq":2,"tf":2,"fill":0,"short":0}, date=dates[3], set_by="Dr. Priya Rajan"),
        TopicHistory(year="1", subject="Introduction to Programming",      topic="Functions & Recursion",     counts={"mcq":3,"tf":2,"fill":1,"short":0}, date=dates[4], set_by="Dr. Priya Rajan"),
        TopicHistory(year="1", subject="Basic Electronics",                topic="Logic Gates",               counts={"mcq":3,"tf":2,"fill":0,"short":0}, date=dates[5], set_by="Prof. Senthil Kumar"),

        # ── Year 2 history ──────────────────────────────────────────────
        TopicHistory(year="2", subject="Data Structures & Algorithms",     topic="Arrays & Linked Lists",     counts={"mcq":3,"tf":2,"fill":0,"short":0}, date=dates[0], set_by="Prof. Senthil Kumar"),
        TopicHistory(year="2", subject="Object Oriented Programming",       topic="Classes & Objects",         counts={"mcq":3,"tf":2,"fill":1,"short":0}, date=dates[1], set_by="Dr. Priya Rajan"),
        TopicHistory(year="2", subject="Data Structures & Algorithms",     topic="Stacks & Queues",           counts={"mcq":3,"tf":2,"fill":0,"short":0}, date=dates[2], set_by="Prof. Senthil Kumar"),
        TopicHistory(year="2", subject="Database Management Systems",       topic="SQL Basics",                counts={"mcq":4,"tf":2,"fill":1,"short":0}, date=dates[3], set_by="Dr. Meena Lakshmi"),
        TopicHistory(year="2", subject="Data Structures & Algorithms",     topic="Trees & Binary Search",     counts={"mcq":3,"tf":2,"fill":1,"short":0}, date=dates[4], set_by="Prof. Senthil Kumar"),
        TopicHistory(year="2", subject="Object Oriented Programming",       topic="Inheritance",               counts={"mcq":3,"tf":2,"fill":0,"short":0}, date=dates[5], set_by="Dr. Priya Rajan"),

        # ── Year 3 history ──────────────────────────────────────────────
        TopicHistory(year="3", subject="Design & Analysis of Algorithms",  topic="Divide & Conquer",          counts={"mcq":3,"tf":2,"fill":0,"short":0}, date=dates[0], set_by="Dr. Meena Lakshmi"),
        TopicHistory(year="3", subject="Machine Learning",                  topic="Linear Regression",         counts={"mcq":3,"tf":2,"fill":1,"short":0}, date=dates[1], set_by="Dr. Meena Lakshmi"),
        TopicHistory(year="3", subject="Operating Systems",                 topic="Process Scheduling",        counts={"mcq":3,"tf":2,"fill":0,"short":0}, date=dates[2], set_by="Prof. Senthil Kumar"),
        TopicHistory(year="3", subject="Software Engineering",              topic="SDLC Models",               counts={"mcq":3,"tf":2,"fill":1,"short":0}, date=dates[3], set_by="Dr. Priya Rajan"),
        TopicHistory(year="3", subject="Design & Analysis of Algorithms",  topic="Dynamic Programming",       counts={"mcq":4,"tf":2,"fill":1,"short":0}, date=dates[4], set_by="Dr. Meena Lakshmi"),
        TopicHistory(year="3", subject="Artificial Intelligence",           topic="Search Algorithms",         counts={"mcq":3,"tf":2,"fill":0,"short":0}, date=dates[5], set_by="Dr. Meena Lakshmi"),
    ]

    db.add_all(history_entries)
    # ── Record permanent "seeded" flag so this never re-runs ──────────────────
    db.add(SeederMeta(key=SEED_KEY))
    db.commit()
    print(f"[Seeder] Topic history seeded: {len(history_entries)} entries across 3 years.")


# NOTE: startup/shutdown now handled by the lifespan context manager above.


@app.get("/")
def read_root():
    return {
        "status": "online",
        "message": "Welcome to EduMentor AI FastAPI Backend!",
        "documentation": "/docs"
    }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
