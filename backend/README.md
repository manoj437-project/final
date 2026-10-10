# EduMentor AI Backend (FastAPI & PostgreSQL)

This folder contains a neat, modular, and easy-to-use FastAPI backend for the **EduMentor AI** application. It connects to a PostgreSQL database and exposes REST APIs for authentication, AI chat history, quiz assessment logging, and mentor dashboard cohorts.

---

## Technical Stack
- **Web Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **ASGI Server**: [Uvicorn](https://www.uvicorn.org/)
- **Database ORM**: [SQLAlchemy](https://www.sqlalchemy.org/)
- **Security**: JWT (JSON Web Tokens) with `python-jose` and passwords hashed using `bcrypt` via `passlib`.
- **Database**: PostgreSQL (via `psycopg2-binary`).

---

## Directory Layout
```
backend/
├── app/
│   ├── config.py       # Configuration parser via pydantic-settings
│   ├── database.py     # SQLAlchemy Engine & session dependencies
│   ├── main.py         # App setup, CORS configuration, database tables generation & startup seeder
│   ├── models.py       # SQLAlchemy Database models
│   ├── schemas.py      # Pydantic Request/Response validation schemas
│   ├── utils.py        # Hashing and token utilities
│   └── routers/
│       ├── auth.py     # Endpoints for registering/logging in Students & Mentors
│       ├── chat.py     # Endpoint for student AI chatbot logs
│       ├── students.py # Endpoint for posting quiz scores & getting cohort dashboards
│       └── timetable.py# Endpoints for daily subject topic & weekly schedules
├── .env                # App environment settings (Local development config)
├── .env.example        # Environment variables template
└── requirements.txt    # Python package dependencies
```

---

## Setup & Running Locally

### 1. Prerequisites
- Python 3.10+ installed.
- PostgreSQL database server running (local or dockerized).

### 2. Configure Environment Variables
Copy `.env.example` to `.env` if not already present:
```bash
cp .env.example .env
```
Inside `.env`, configure your PostgreSQL credentials:
```env
DATABASE_URL=postgresql://<username>:<password>@localhost:5432/<database_name>
JWT_SECRET_KEY=<generate_random_hex_string>
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### 3. Install Dependencies
Create a python virtual environment, activate it, and install required libraries:

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 4. Run Development Server
Start the development server with:
```bash
# From within the backend directory
python -m uvicorn app.main:app --reload
```
The server will start on **`http://localhost:8000`**.

### 5. Interactive API Documentation
Once the server is running, visit:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## Database Auto-Seeding (Default Demo Accounts)
To make local evaluation easy, the database is **automatically seeded** with the default cohort students, test assessment scores, and mock mentor logins on startup:

### Student Logins (Password for all: `password123`)
1. **Alice Smith** (1st Year) — Email: `alice@edumentor.edu`
2. **Bob Johnson** (1st Year) — Email: `bob@edumentor.edu`
3. **Charlie Brown** (2nd Year) — Email: `charlie@edumentor.edu`
4. **Diana Prince** (3rd Year) — Email: `diana@edumentor.edu`
5. **Ethan Hunt** (3rd Year) — Email: `ethan@edumentor.edu`

### Mentor Logins (Password for all: `password123`)
1. **Dr. Sarah Jenkins** — Email/ID: `sarah@edumentor.edu`
2. **Prof. Alan Turing** — Email/ID: `alan@edumentor.edu`
