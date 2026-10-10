import os
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

OUTPUT_PDF = "EduMentor_AI_Viva_Preparation_Guide.pdf"

# ── Color Palette ─────────────────────────────────────────────────────────────
NAVY       = colors.HexColor("#0F172A")  # Deep Slate / Navy
PRIMARY    = colors.HexColor("#1E40AF")  # Deep Blue
SECONDARY  = colors.HexColor("#3B82F6")  # Accent Blue
CYAN       = colors.HexColor("#0284C7")  # Bright Cyan
BG_LIGHT   = colors.HexColor("#F8FAFC")  # Light Slate BG
BORDER_COL = colors.HexColor("#CBD5E1")  # Slate Border
GREEN      = colors.HexColor("#15803D")  # Success Green
LIGHT_GRN  = colors.HexColor("#DCFCE7")  # Light Green BG
AMBER      = colors.HexColor("#B45309")  # Amber / Warning
LIGHT_AMB  = colors.HexColor("#FEF3C7")  # Light Amber BG
RED        = colors.HexColor("#B91C1C")  # Alert Red
LIGHT_RED  = colors.HexColor("#FEE2E2")  # Light Red BG
PURPLE     = colors.HexColor("#6D28D9")  # Tech Purple
LIGHT_PURP = colors.HexColor("#EDE9FE")  # Light Purple BG
WHITE      = colors.white
DARK_TEXT  = colors.HexColor("#1E293B")
MUTED_TEXT = colors.HexColor("#64748B")

W = 18.0 * cm  # printable width (21 - 3)

# ── Numbered Canvas for Footer ────────────────────────────────────────────────
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, total_pages):
        w, h = A4
        self.saveState()
        # Top banner line on non-cover pages
        if self._pageNumber > 1:
            self.setStrokeColor(PRIMARY)
            self.setLineWidth(2)
            self.line(1.5 * cm, h - 1.2 * cm, w - 1.5 * cm, h - 1.2 * cm)
            
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(PRIMARY)
            self.drawString(1.5 * cm, h - 1.05 * cm, "EduMentor AI – Comprehensive Viva Preparation Master Guide")
            
            self.setFont("Helvetica", 8)
            self.setFillColor(MUTED_TEXT)
            self.drawRightString(w - 1.5 * cm, h - 1.05 * cm, "Tamil / Tanglish + English Reference")

        # Bottom footer line on all pages
        self.setStrokeColor(BORDER_COL)
        self.setLineWidth(0.75)
        self.line(1.5 * cm, 1.3 * cm, w - 1.5 * cm, 1.3 * cm)

        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(NAVY)
        self.drawString(1.5 * cm, 0.85 * cm, "EduMentor AI | Final Year Engineering Project Viva Guide")

        self.setFont("Helvetica", 8)
        self.setFillColor(MUTED_TEXT)
        self.drawRightString(w - 1.5 * cm, 0.85 * cm, f"Page {self._pageNumber} of {total_pages}")
        self.restoreState()


# ── Style Registry ────────────────────────────────────────────────────────────
def S(name, **kw):
    return ParagraphStyle(name, **kw)

title_style = S("Title", fontName="Helvetica-Bold", fontSize=22, textColor=WHITE, alignment=TA_CENTER, leading=26)
subtitle_style = S("SubTitle", fontName="Helvetica", fontSize=11, textColor=colors.HexColor("#93C5FD"), alignment=TA_CENTER, leading=15)
meta_style = S("Meta", fontName="Helvetica-Bold", fontSize=9, textColor=WHITE, alignment=TA_CENTER)

sec_title_style = S("SecTitle", fontName="Helvetica-Bold", fontSize=13, textColor=PRIMARY, spaceBefore=8, spaceAfter=4, leading=16)
sub_sec_style = S("SubSecTitle", fontName="Helvetica-Bold", fontSize=10.5, textColor=NAVY, spaceBefore=5, spaceAfter=2, leading=13)

body_style = S("Body", fontName="Helvetica", fontSize=9, textColor=DARK_TEXT, leading=13, spaceAfter=3)
body_bold = S("BodyBold", fontName="Helvetica-Bold", fontSize=9, textColor=DARK_TEXT, leading=13)
tanglish_style = S("Tanglish", fontName="Helvetica-Oblique", fontSize=8.5, textColor=colors.HexColor("#0369A1"), leading=12)

table_hdr = S("TH", fontName="Helvetica-Bold", fontSize=8.5, textColor=WHITE, leading=11, alignment=TA_CENTER)
table_cell = S("TC", fontName="Helvetica", fontSize=8, textColor=DARK_TEXT, leading=11)
table_cell_bold = S("TCB", fontName="Helvetica-Bold", fontSize=8, textColor=NAVY, leading=11)
table_cell_tanglish = S("TCT", fontName="Helvetica-Oblique", fontSize=7.8, textColor=colors.HexColor("#0284C7"), leading=10.5)

callout_style = S("Callout", fontName="Helvetica", fontSize=8.5, textColor=DARK_TEXT, leading=12.5)
callout_bold = S("CalloutB", fontName="Helvetica-Bold", fontSize=9, textColor=PRIMARY, leading=13)


def make_section_banner(title, icon="📌"):
    data = [[
        Paragraph(f"<b><font size='12'>{icon} {title.upper()}</font></b>", S("bann", fontName="Helvetica-Bold", fontSize=11, textColor=WHITE, leading=14))
    ]]
    t = Table(data, colWidths=[W])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), PRIMARY),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('CORNERPAD', (0,0), (-1,-1), 4),
    ]))
    return t


def make_callout(title_text, tanglish_text, english_desc, example_text="", border_col=PRIMARY, bg_col=BG_LIGHT):
    content = []
    content.append(Paragraph(f"<b>{title_text}</b>", callout_bold))
    if tanglish_text:
        content.append(Spacer(1, 2))
        content.append(Paragraph(f"<b>Tanglish Meaning:</b> <i>{tanglish_text}</i>", tanglish_style))
    if english_desc:
        content.append(Spacer(1, 2))
        content.append(Paragraph(f"<b>Technical Explanation:</b> {english_desc}", callout_style))
    if example_text:
        content.append(Spacer(1, 2))
        content.append(Paragraph(f"<b>Real-life Example:</b> <font color='#16A34A'><b>{example_text}</b></font>", callout_style))
    
    wrapper = [[content]]
    t = Table(wrapper, colWidths=[W])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), bg_col),
        ('BOX', (0,0), (-1,-1), 1, border_col),
        ('LINELEFT', (0,0), (0,-1), 3.5, border_col),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    return t


def build_pdf():
    doc = SimpleDocTemplate(
        OUTPUT_PDF,
        pagesize=A4,
        leftMargin=1.5 * cm,
        rightMargin=1.5 * cm,
        topMargin=1.6 * cm,
        bottomMargin=1.6 * cm,
    )
    story = []

    # ═════════════════════════════════════════════════════════════════════════
    # COVER / HEADER BANNER
    # ═════════════════════════════════════════════════════════════════════════
    header_data = [
        [Paragraph("🎓 EduMentor AI – Complete Project Viva Master Guide", title_style)],
        [Spacer(1, 3)],
        [Paragraph("Full Project Architecture, Every Tech Stack Breakdown, Workflow & Top 20 Viva Questions", subtitle_style)],
        [Spacer(1, 5)],
        [Paragraph("Language: English + Simple Tanglish Explanations with Real-World Analogies for Instant Viva Recall", meta_style)],
    ]
    header_table = Table(header_data, colWidths=[W])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), NAVY),
        ('TOPPADDING', (0,0), (-1,-1), 10),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 10))

    # ═════════════════════════════════════════════════════════════════════════
    # SECTION 1: 1-MINUTE VIVA PITCH (Examiner asks: "Explain your project")
    # ═════════════════════════════════════════════════════════════════════════
    story.append(make_section_banner("1. 1-Minute Elevator Pitch for Viva (Examiner-ku Enna Solla Vendiyathu?)", "🎤"))
    story.append(Spacer(1, 6))

    pitch_tanglish = (
        "Sir/Madam, namma project <b>EduMentor AI</b> oru Automated Daily Knowledge Evaluation and "
        "Mentorship Analytics System. Traditional colleges-la faculty nadathuna topic student-ku purinjitha illayanu "
        "semester exam-la than theriya varum. EduMentor AI-la mentor daily oru topic assign pannuvanga (e.g. TCP Protocol). "
        "System udane Google Gemini AI moolama dynamic questions (MCQ, True/False, Fill in blanks) generate pannum with a timer. "
        "Students test attend panna udane, marks instant-aa evaluate aagi, weak students (<50% or 'didn't understand') identify aavanga. "
        "Deadline mudiyumbothu, background scheduler automatically faculty-ku complete attendance, marks list and reteach suggestions-oda "
        "email anuppidum! Koodave students-ku 24/7 AI tutor chat support irukku!"
    )
    pitch_english = (
        "<b>In English (Examiner Pitch):</b> EduMentor AI is an end-to-end intelligent pedagogical ecosystem bridging "
        "the feedback gap between students and educators. It integrates dynamic AI-powered daily micro-assessments (Google Gemini), "
        "real-time automated grading, background task scheduling (APScheduler), automated faculty intervention alerting (Resend/SMTP), "
        "and an interactive 24/7 AI doubt-clearing tutor built using React 19, FastAPI, and SQLAlchemy."
    )
    story.append(make_callout("How to Start Your Viva Answer (The Killer Pitch)", pitch_tanglish, pitch_english, "Analogy: Namma college-la doctor maathiri daily health checkup eduthu faculty-ku report kudukra AI!", PRIMARY, BG_LIGHT))
    story.append(Spacer(1, 10))

    # ═════════════════════════════════════════════════════════════════════════
    # SECTION 2: MASTER TECH STACK MATRIX (Ethukku Use Pandrom Table)
    # ═════════════════════════════════════════════════════════════════════════
    story.append(make_section_banner("2. Complete Tech Stack Master Table (Ellamey Ethukku Use Pandrom?)", "🛠️"))
    story.append(Spacer(1, 6))

    tech_table_data = [
        [
            Paragraph("Technology", table_hdr),
            Paragraph("What is it? (Definition)", table_hdr),
            Paragraph("Namma Project-la Ethukku?", table_hdr),
            Paragraph("Simple Real-Life Example", table_hdr)
        ],
        [
            Paragraph("<b>React 19</b>", table_cell_bold),
            Paragraph("Component-based Frontend JavaScript Library for interactive Single Page Applications (SPA).", table_cell),
            Paragraph("Student Dashboard, Mentor Portal, Live Timer, Quiz Cards, and Real-time Chat UI build panna.", table_cell_tanglish),
            Paragraph("Lego Blocks maathiri: Button, Navbar, Timer ellam re-usable pieces.", table_cell)
        ],
        [
            Paragraph("<b>Vite 8</b>", table_cell_bold),
            Paragraph("Next-generation lightning-fast frontend dev server & module bundler using native ES modules.", table_cell),
            Paragraph("React code-ah ultra-fast reload (Hot Module Replacement) panni production bundle create panna.", table_cell_tanglish),
            Paragraph("Old Webpack cycle maathiri wait panna theva illa; Superfast Sports car maathiri 200ms-la run aagum.", table_cell)
        ],
        [
            Paragraph("<b>Tailwind CSS v4</b>", table_cell_bold),
            Paragraph("Utility-first CSS framework for rapid modern responsive UI styling without writing custom CSS files.", table_cell),
            Paragraph("Glassmorphic cards, gradients, modern dark/light styling, and responsive layout design panna.", table_cell_tanglish),
            Paragraph("Ready-made clothes maathiri: `bg-blue-600 rounded-xl p-4` nu direct-aa HTML tag-laye style pannalam.", table_cell)
        ],
        [
            Paragraph("<b>Framer Motion</b>", table_cell_bold),
            Paragraph("Production-ready declarative animation library for React components.", table_cell),
            Paragraph("Quiz card flip, modal popups, score progress bar smooth animation, and page transitions-ku.", table_cell_tanglish),
            Paragraph("PowerPoint slide animations maathiri UI elements smooth-aa paranthu vanthu settle aagum.", table_cell)
        ],
        [
            Paragraph("<b>React Router v7</b>", table_cell_bold),
            Paragraph("Client-side routing engine for multi-view Single Page Applications without browser reload.", table_cell),
            Paragraph("`/student/dashboard`, `/mentor/dashboard`, `/chat` nu seamless page navigation manage panna.", table_cell_tanglish),
            Paragraph("Page refresh aagama TV channel switch pandra maathiri instant screen switch.", table_cell)
        ],
        [
            Paragraph("<b>FastAPI</b>", table_cell_bold),
            Paragraph("Modern, high-performance asynchronous Python web framework based on OpenAPI & Starlette.", table_cell),
            Paragraph("Namma REST API Backend engine: Auth, Timetable, Daily Topic, Scoring, Gemini Quiz Generation handle panna.", table_cell_tanglish),
            Paragraph("Express counter maathiri: Request vantha async-aa fast-aa response kudukkum, Swagger docs automatic-aa generate pannum.", table_cell)
        ],
        [
            Paragraph("<b>Uvicorn</b>", table_cell_bold),
            Paragraph("Lightning-fast ASGI (Asynchronous Server Gateway Interface) web server implementation for Python.", table_cell),
            Paragraph("FastAPI application-ah run panni incoming HTTP/HTTPS browser requests-ah handle panna.", table_cell_tanglish),
            Paragraph("Engine of a Train: FastAPI is the train coaches, Uvicorn is the high-power electric engine driving it.", table_cell)
        ],
        [
            Paragraph("<b>Pydantic v2</b>", table_cell_bold),
            Paragraph("Data validation and parsing library using standard Python type hints (`schemas.py`).", table_cell),
            Paragraph("Frontend-la irunthu vara student answers, login credentials data types accurate-aa validate panna.", table_cell_tanglish),
            Paragraph("Airport Security Scanner: Wrong data type vantha ulla vidaama error throw pannidum.", table_cell)
        ],
        [
            Paragraph("<b>SQLAlchemy 2.0</b>", table_cell_bold),
            Paragraph("Object Relational Mapper (ORM) translating Python class objects into Database SQL queries.", table_cell),
            Paragraph("Direct SQL query ezhuthama `StudentScore`, `TopicHistory`, `QuizAttempt` Python models moolama DB operate panna.", table_cell_tanglish),
            Paragraph("Translator: Namma Python-la pesina, athu Database SQL language-ku translate pannikkum.", table_cell)
        ],
        [
            Paragraph("<b>PostgreSQL / SQLite</b>", table_cell_bold),
            Paragraph("ACID-compliant Relational Database Management System (RDBMS) storing relational tables.", table_cell),
            Paragraph("Students data, login passwords, quiz marks, chat history, topic assignments safely store panna.", table_cell_tanglish),
            Paragraph("College Central Record Room: Ella register files-um orderly racks-la save panni vachirukkum.", table_cell)
        ],
        [
            Paragraph("<b>Google Gemini AI</b>", table_cell_bold),
            Paragraph("Google's Multimodal Generative Large Language Model (`gemini-2.0-flash` & `1.5-flash`).", table_cell),
            Paragraph("Topic-ku relevant MCQ/TF questions automatically generate panna + 24/7 Student Doubt Solver Chatbot-ku.", table_cell_tanglish),
            Paragraph("Super intelligent virtual professor: Enna topic sonnalum instant-aa questions & clear answers explain pannuvaaru.", table_cell)
        ],
        [
            Paragraph("<b>JWT (python-jose)</b>", table_cell_bold),
            Paragraph("JSON Web Token standard for secure, stateless client-server token-based authentication.", table_cell),
            Paragraph("Student/Mentor login pannathum session maintain panna and role-based secure access verify panna.", table_cell_tanglish),
            Paragraph("College ID Card / Entry Pass: Oru murai pass vaangita, ovvoru murai ID card kaatti ulla pogalam.", table_cell)
        ],
        [
            Paragraph("<b>Bcrypt</b>", table_cell_bold),
            Paragraph("One-way cryptographic password hashing algorithm with salt protection against brute-force.", table_cell),
            Paragraph("Plain text passwords DB-la store aagama, irreversible hashed string-aa encrypt panni save panna.", table_cell_tanglish),
            Paragraph("Meat Grinder: Paper-ah podda pudichidalam, aana ground meat-la irunthu original paper thirumba edukka mudiyathu.", table_cell)
        ],
        [
            Paragraph("<b>APScheduler</b>", table_cell_bold),
            Paragraph("Advanced in-process background task scheduler for periodic Python execution.", table_cell),
            Paragraph("Every 30 seconds run aagi, quiz deadline mudiyum pothu auto-calculate panni faculty-ku report send panna.", table_cell_tanglish),
            Paragraph("Automatic Alarm Clock: Time aagiduchu nu alarm adichu email anuppum.", table_cell)
        ],
        [
            Paragraph("<b>Resend / SMTP</b>", table_cell_bold),
            Paragraph("Cloud Transactional Email API service & standard SMTP protocol for automated email dispatch.", table_cell),
            Paragraph("Mentor-ku session summary, weak students alert, and boring class report emails deliver panna.", table_cell_tanglish),
            Paragraph("Postman: Backend generate panra HTML report-ah faculty mail inbox-ku correct-aa drop pannum.", table_cell)
        ],
    ]

    t_tech = Table(tech_table_data, colWidths=[3.2*cm, 4.6*cm, 5.4*cm, 4.8*cm])
    t_tech.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COL),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [WHITE, BG_LIGHT]),
    ]))
    story.append(t_tech)
    story.append(Spacer(1, 10))

    # ═════════════════════════════════════════════════════════════════════════
    # SECTION 3: FRONTEND ARCHITECTURE & LIFE CYCLE
    # ═════════════════════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.append(make_section_banner("3. Frontend Architecture (React 19 + Vite + Tailwind CSS)", "💻"))
    story.append(Spacer(1, 6))

    front_intro = (
        "<b>Frontend Role:</b> User Interface (UI) and User Experience (UX). "
        "Two distinct dashboards exist: <b>Student Portal</b> and <b>Mentor Portal</b>."
    )
    story.append(Paragraph(front_intro, body_style))
    story.append(Spacer(1, 4))

    f1 = make_callout(
        "1. React Components & State Management",
        "React-la ovvoru screen-um small reusable components-aa pirikapadum. `useState` data store pannum, `useEffect` API call trigger pannum.",
        "React uses Virtual DOM. Instead of re-rendering the whole page, it diffs and updates only changed elements. We use `useState` for timer countdown and answers, `useEffect` for fetching daily topics on load.",
        "Quiz countdown timer ovvoru second-um decrement aagum pothu, full page reload aagathu; antha timer number mattum update aagum!",
        PRIMARY, BG_LIGHT
    )
    story.append(f1)
    story.append(Spacer(1, 5))

    f2 = make_callout(
        "2. Client-Side Routing (React Router DOM v7)",
        "Single Page Application (SPA) koncept. Browser-la page reload aagama URLs switch aagum.",
        "Manages declarative routing with `<Routes>` and `<Route>`. Protected routes inspect the JWT stored in `localStorage` or `sessionStorage` before granting access.",
        "User `/mentor/dashboard` click pannal, unauthorized person-ah iruntha login page-ku auto redirect pannidum.",
        CYAN, BG_LIGHT
    )
    story.append(f2)
    story.append(Spacer(1, 5))

    f3 = make_callout(
        "3. Live Quiz Taking & Anti-Cheat Countdown",
        "Frontend timer deadline time-oda match aagi zero aana udane, auto-submit trigger aagum.",
        "The timer calculates `remaining_seconds = deadline_timestamp - current_timestamp`. When it hits 0, `handleSubmitQuiz()` executes automatically.",
        "Student submit button click panna maranthalum or tab close panna ninaichalum, time mudinja udane existing answers submit aagidum.",
        AMBER, LIGHT_AMB
    )
    story.append(f3)
    story.append(Spacer(1, 10))

    # ═════════════════════════════════════════════════════════════════════════
    # SECTION 4: BACKEND ARCHITECTURE & API PIPELINE
    # ═════════════════════════════════════════════════════════════════════════
    story.append(make_section_banner("4. Backend Architecture (FastAPI + ASGI + SQLAlchemy)", "⚙️"))
    story.append(Spacer(1, 6))

    back_intro = (
        "<b>Backend Role:</b> Business logic, database interactions, authentication, scheduled background jobs, and AI API orchestration. "
        "Organized cleanly in modular routers: `auth.py`, `students.py`, `timetable.py`, and `chat.py`."
    )
    story.append(Paragraph(back_intro, body_style))
    story.append(Spacer(1, 4))

    b1 = make_callout(
        "1. FastAPI Request-Response Cycle & Dependency Injection",
        "FastAPI Asynchronous Python framework. `async/await` and `Depends(get_db)` use panni DB connection safely manage pandrom.",
        "FastAPI creates lightweight coroutines for incoming requests. `Depends(get_db)` opens a session, injects it into endpoint, and guarantees session close in `finally` block preventing memory leaks.",
        "100 students simultaneously quiz submit pannalum, ASGI event loop request-ah queue panni block aagama instantly handle pannum.",
        PRIMARY, BG_LIGHT
    )
    story.append(b1)
    story.append(Spacer(1, 5))

    b2 = make_callout(
        "2. Pydantic Schemas vs SQLAlchemy Models (Viva Golden Question!)",
        "<b>Examiner Question:</b> 'What is the difference between Schema and Model?' — Models create DB tables, Schemas validate API request/response JSON.",
        "<b>SQLAlchemy Model:</b> Defines database structure (`__tablename__`, columns, foreign keys).<br/>"
        "<b>Pydantic Schema:</b> Validates HTTP payloads before hitting database (e.g., email format, score integer type).",
        "Student score '4/5' string-aa irunthalum percentage 80 integer-aa irukkanumnu check panrathu Pydantic; DB table-la store panrathu SQLAlchemy.",
        PURPLE, LIGHT_PURP
    )
    story.append(b2)
    story.append(Spacer(1, 10))

    # ═════════════════════════════════════════════════════════════════════════
    # SECTION 5: SECURITY & AUTHENTICATION (JWT + BCRYPT)
    # ═════════════════════════════════════════════════════════════════════════
    story.append(make_section_banner("5. Security & Authentication Architecture", "🔐"))
    story.append(Spacer(1, 6))

    sec_table_data = [
        [
            Paragraph("Security Mechanism", table_hdr),
            Paragraph("How It Works in EduMentor AI", table_hdr),
            Paragraph("Why It Is Essential?", table_hdr)
        ],
        [
            Paragraph("<b>Bcrypt Password Hashing</b>", table_cell_bold),
            Paragraph("User register/seed aagum pothu password salt add panni hash aagum (`get_password_hash()`). Login-la `verify_password()` match check pannum.", table_cell),
            Paragraph("Database hacker access pannalum original password theriyathu. Plain passwords are NEVER saved in database.", table_cell_tanglish)
        ],
        [
            Paragraph("<b>JWT (JSON Web Token)</b>", table_cell_bold),
            Paragraph("Login success aana udane server creates a signed cryptographically tamper-proof token containing `sub` (regno/identity), `role` (student/mentor), and `exp`.", table_cell),
            Paragraph("Stateless: Server database-la session maintain panna theva illa. Token header-la send aagum (`Authorization: Bearer <token>`).", table_cell_tanglish)
        ],
        [
            Paragraph("<b>Role-Based Access Control (RBAC)</b>", table_cell_bold),
            Paragraph("`get_current_student` and `get_current_mentor` dependencies token decode panni identity & role verify pannum.", table_cell),
            Paragraph("Student mentor API-ah call panna mudiyathu (`403 Forbidden`). Mentor student quiz attend panna mudiyathu.", table_cell_tanglish)
        ],
        [
            Paragraph("<b>CORS Middleware</b>", table_cell_bold),
            Paragraph("FastAPI `CORSMiddleware` configured to allow safe cross-origin communication between Frontend (port 5173) and Backend (port 8000).", table_cell),
            Paragraph("Unauthorized external domains namma backend API-ah misuse pannama protect pannum.", table_cell_tanglish)
        ],
    ]
    t_sec = Table(sec_table_data, colWidths=[4.2*cm, 7.2*cm, 6.6*cm])
    t_sec.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), NAVY),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COL),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [WHITE, BG_LIGHT]),
    ]))
    story.append(t_sec)
    story.append(Spacer(1, 10))

    # ═════════════════════════════════════════════════════════════════════════
    # SECTION 6: ARTIFICIAL INTELLIGENCE & LLM ENGINE
    # ═════════════════════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.append(make_section_banner("6. Artificial Intelligence & LLM Pipeline (Google Gemini)", "🤖"))
    story.append(Spacer(1, 6))

    ai_intro = (
        "<b>Core AI Engine:</b> Google Gemini API integrated in `backend/app/utils/gemini_service.py`. "
        "Dual functionality: (1) Automated Pedagogical Assessment Question Generation, and (2) 24/7 Context-Aware Interactive Doubt Tutor."
    )
    story.append(Paragraph(ai_intro, body_style))
    story.append(Spacer(1, 4))

    ai1 = make_callout(
        "1. Dynamic Question Generator with Zero-Downtime Fallback",
        "Faculty topic (e.g. 'Deadlocks in OS') enter pannal, Gemini API dynamic MCQ, True/False, Fill in blanks JSON generate pannum.",
        "Prompt engineering instructs Gemini to return strict JSON format with schema `{type, q, a, options}`. "
        "<b>Multi-tier Failover:</b> If Gemini 2.0 Flash is busy, it auto-falls back to `1.5-flash` → `1.5-flash-8b` → Local Curated Topic Question Bank.",
        "Internet cut aanaalum or API rate limit (429) vanthaalum system crash aagathu; internal offline Question Bank-la irunthu exam start aagidum!",
        GREEN, LIGHT_GRN
    )
    story.append(ai1)
    story.append(Spacer(1, 5))

    ai2 = make_callout(
        "2. JSON Sanitization & Parsing Engine (`extract_clean_json`)",
        "LLM models silasamayam extra explanations or markdown code blocks (```json ... ```) kudukkum. Athai clean panni pure Python dict-aa convert panrom.",
        "Custom Regex cleaner strips conversational preambles, fences, and removes trailing commas before parsing via `json.loads()`.",
        "API response malformed-aa irunthalum server 500 Internal Server Error adikkama smooth-aa recovery pannum.",
        PRIMARY, BG_LIGHT
    )
    story.append(ai2)
    story.append(Spacer(1, 5))

    ai3 = make_callout(
        "3. 24/7 Context-Aware Student Doubt Solving Chatbot",
        "Student quiz mudicha piraku or study panrapo varra doubts-ah AI tutor kitta kelvi kettu instant simple explanations edukalam.",
        "Chat messages are saved in database (`ChatMessage` model). The system prompt conditions Gemini to respond as an empathetic academic tutor with examples.",
        "Student: 'TCP 3-way handshake enna?' AI: 'Imagine oru phone call: 1. Hello (SYN), 2. Hello kekkuthu (SYN-ACK), 3. Seri pesalam (ACK)!'",
        CYAN, BG_LIGHT
    )
    story.append(ai3)
    story.append(Spacer(1, 10))

    # ═════════════════════════════════════════════════════════════════════════
    # SECTION 7: BACKGROUND AUTOMATION & EMAIL ALERTS (APSCHEDULER)
    # ═════════════════════════════════════════════════════════════════════════
    story.append(make_section_banner("7. Background Automation & Alerting Engine (`scheduler.py`)", "⏱️"))
    story.append(Spacer(1, 6))

    sched_intro = (
        "<b>Why Background Scheduler?</b> Quiz-ku time limit mudiyum pothu human yaarum manual-aa calculate panna koodathu. "
        "EduMentor AI-la <b>APScheduler</b> background-la run aagi auto-grade panni email report dispatch pannum."
    )
    story.append(Paragraph(sched_intro, body_style))
    story.append(Spacer(1, 4))

    s1 = make_callout(
        "How the 30-Second Polling & 10-Second Deadline Catch Works",
        "APScheduler background thread-la every 30 seconds run aagum. Due date & due time compare panni, deadline kitta vantha trigger pannum.",
        "To avoid missing tight deadlines, the scheduler catches a 0-40s window before expiry. A deduplication set (`_sent_reports`) ensures the report is sent exactly ONCE per session.",
        "Mentor quiz set pannitu switch off pannitalum, exact-aa deadline mudiyum pothu antha particular mentor mail-ku report poi sernthidum!",
        AMBER, LIGHT_AMB
    )
    story.append(s1)
    story.append(Spacer(1, 5))

    s2 = make_callout(
        "Automated Pedagogical Interventions (What is inside the Email?)",
        "Email report faculty-ku comprehensive actionable insights tharum:<br/>"
        "• <b>Full Marksheet Table:</b> All students marks + Missed (not attended) list.<br/>"
        "• <b>Weak Students List (<50%):</b> Direct names and marks highlighted in RED.<br/>"
        "• <b>Not Understood Students:</b> Students who marked 'Puriyala' flag.<br/>"
        "• <b>Reteach Suggestion:</b> If weak students > 50%, urgent re-teaching recommendation alert trigger aagum!",
        "Emails are sent via Resend REST API or fallback SMTP to ensure 99.9% inbox delivery.",
        "Faculty paper correct panna theva illa; class mudinja 15th minute-la full class diagnosis faculty email inbox-la ready!",
        RED, LIGHT_RED
    )
    story.append(s2)
    story.append(Spacer(1, 10))

    # ═════════════════════════════════════════════════════════════════════════
    # SECTION 8: DATABASE ARCHITECTURE & 9 KEY TABLES
    # ═════════════════════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.append(make_section_banner("8. Database Architecture – 9 Key Tables (`models.py`)", "🗄️"))
    story.append(Spacer(1, 6))

    db_table_data = [
        [
            Paragraph("Table Name", table_hdr),
            Paragraph("Primary Purpose", table_hdr),
            Paragraph("Key Columns / Schema", table_hdr),
            Paragraph("Namma Project-la Ethukku?", table_hdr)
        ],
        [
            Paragraph("<b>students</b>", table_cell_bold),
            Paragraph("Student master profile records.", table_cell),
            Paragraph("`id, username, regno, dept, year, email, password_hash`", table_cell),
            Paragraph("Student authentication, cohort grouping (1st/2nd/3rd year).", table_cell_tanglish)
        ],
        [
            Paragraph("<b>mentors</b>", table_cell_bold),
            Paragraph("Faculty/Mentor master records.", table_cell),
            Paragraph("`id, name, dept, identity, password_hash`", table_cell),
            Paragraph("Faculty login and quiz session assignment tracking.", table_cell_tanglish)
        ],
        [
            Paragraph("<b>daily_topics</b>", table_cell_bold),
            Paragraph("Active daily topic assigned per cohort.", table_cell),
            Paragraph("`id, year, subject, topic, counts, date, due_date, due_time, manual_questions`", table_cell),
            Paragraph("Current live topic & active timer deadline per cohort year.", table_cell_tanglish)
        ],
        [
            Paragraph("<b>topic_history</b>", table_cell_bold),
            Paragraph("Immutable append-only history of every assignment.", table_cell),
            Paragraph("`id, year, subject, topic, set_by, due_date, due_time, created_at`", table_cell),
            Paragraph("Auditing: Who assigned which topic and when (never overwritten).", table_cell_tanglish)
        ],
        [
            Paragraph("<b>student_scores</b>", table_cell_bold),
            Paragraph("Stores assessment results for students.", table_cell),
            Paragraph("`id, student_id, topic, score, percentage, date, not_understood`", table_cell),
            Paragraph("Mark records for analytics, leaderboard, weak student detection.", table_cell_tanglish)
        ],
        [
            Paragraph("<b>quiz_attempts</b>", table_cell_bold),
            Paragraph("Full question-by-question audit log per attempt.", table_cell),
            Paragraph("`id, student_id, topic, answers(JSON), score, percentage`", table_cell),
            Paragraph("Detailed breakdown of student answers vs correct answers.", table_cell_tanglish)
        ],
        [
            Paragraph("<b>boring_reports</b>", table_cell_bold),
            Paragraph("Anonymous class engagement & boredom reports.", table_cell),
            Paragraph("`id, student_id, topic, date, created_at`", table_cell),
            Paragraph("Tracks students who found class dry/boring for pedagogical review.", table_cell_tanglish)
        ],
        [
            Paragraph("<b>chat_messages</b>", table_cell_bold),
            Paragraph("Persistent AI tutor conversation logs.", table_cell),
            Paragraph("`id, student_id, sender('student'|'ai'), message, timestamp`", table_cell),
            Paragraph("Stores chat history so student can review past doubts anytime.", table_cell_tanglish)
        ],
        [
            Paragraph("<b>weekly_timetables</b>", table_cell_bold),
            Paragraph("Class timetable matrix across the week.", table_cell),
            Paragraph("`id, year, day, period, subject, topic`", table_cell),
            Paragraph("Helps mentor schedule topics according to daily class routine.", table_cell_tanglish)
        ],
    ]

    t_db = Table(db_table_data, colWidths=[3.2*cm, 4.4*cm, 5.2*cm, 5.2*cm])
    t_db.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COL),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 3.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3.5),
        ('LEFTPADDING', (0,0), (-1,-1), 4),
        ('RIGHTPADDING', (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [WHITE, BG_LIGHT]),
    ]))
    story.append(t_db)
    story.append(Spacer(1, 10))

    # ═════════════════════════════════════════════════════════════════════════
    # SECTION 9: STEP-BY-STEP END-TO-END WORKFLOW
    # ═════════════════════════════════════════════════════════════════════════
    story.append(make_section_banner("9. End-to-End System Workflow (How It Works from A to Z)", "🔄"))
    story.append(Spacer(1, 6))

    steps_text = [
        ("Step 1: Faculty Sets Daily Topic", "Mentor logs in, selects Year (e.g. 2nd Year), enters Subject ('Operating Systems'), Topic ('Page Replacement Algorithms'), specifies Question counts (3 MCQ, 2 TF) and sets a Deadline (e.g. 4:00 PM)."),
        ("Step 2: AI Question Generation", "Backend calls Google Gemini 2.0 Flash with prompt rules. If API works, dynamic questions are returned in JSON; if quota exceeds, curated fallback bank provides instant questions. Topic is activated in DB."),
        ("Step 3: Student Enters & Takes Assessment", "Students in that year log in. Active quiz banner alerts them with countdown timer. Students answer questions, optionally tick 'I did not understand today\\'s session' or report boredom."),
        ("Step 4: Immediate Auto-Grading", "On submit (or auto-submit when timer expires), backend verifies answers, calculates percentage, saves into `student_scores` and `quiz_attempts`. Student gets immediate scorecard with explanations."),
        ("Step 5: Background Engine & Email Report", "At 4:00 PM, APScheduler wakes up. It fetches all student scores for that topic. Students who didn't submit are flagged as 'Missed'. Marks table and weak student list are compiled into a responsive HTML email and sent to the mentor!"),
        ("Step 6: AI Doubt Resolution Support", "Struggling students navigate to AI Tutor tab to ask doubts anytime. Gemini AI clarifies complex concepts in conversational, simplified terms.")
    ]

    for title, desc in steps_text:
        story.append(Paragraph(f"<b>{title}:</b> {desc}", body_style))
        story.append(Spacer(1, 2))
    story.append(Spacer(1, 10))

    # ═════════════════════════════════════════════════════════════════════════
    # SECTION 10: TOP 20 VIVA QUESTIONS & ANSWERS (EXAMINER FAVORITES)
    # ═════════════════════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.append(make_section_banner("10. Top 20 Viva Questions & Smart Tanglish Answers", "🎯"))
    story.append(Spacer(1, 6))

    viva_qa = [
        (
            "Q1: Why did you choose FastAPI instead of Django or Flask?",
            "FastAPI is modern, asynchronous (ASGI), and significantly faster than Flask/Django. It uses Python type hints for automated Pydantic validation and automatically generates interactive Swagger/OpenAPI documentation. Django is heavy with unnecessary built-in template engines, whereas FastAPI is lightweight and ideal for decoupled React frontend SPAs.",
            "FastAPI async-aa irunthathaala superfast. Auto documentation (`/docs`) generate aagidum. React kooda REST API connect panna FastAPI is the best modern choice!"
        ),
        (
            "Q2: What is the role of Vite and why not Create-React-App (CRA)?",
            "Create-React-App is officially deprecated. CRA uses Webpack which bundles the entire code before serving, making builds very slow. Vite uses Native ES Modules (ESM) and esbuild written in Go, offering sub-second dev server start times and instant Hot Module Replacement (HMR).",
            "CRA pazhasu, slow-aa irukkum. Vite modern tool, lightning fast-aa compile pannum!"
        ),
        (
            "Q3: How does JWT Authentication work in your project?",
            "When a student or mentor enters valid credentials, the backend signs a JSON Web Token with a secret key (`SECRET_KEY`), algorithm (`HS256`), and expiration time. The frontend stores this token and sends it in the `Authorization: Bearer <token>` header for subsequent requests. The backend verifies the token statelessly without needing server-side session lookup.",
            "Server token generate panni tharum. Frontend ovvoru request koodavum antha token-ah send panni identity verify pannikkum."
        ),
        (
            "Q4: What happens if Google Gemini API is down or rate-limited?",
            "Our system implements a multi-tier fallback mechanism. It first tries `gemini-2.0-flash`, then `gemini-1.5-flash`, and if all cloud LLM calls fail, it automatically falls back to an internal curated question bank (`TOPIC_QUESTION_BANK`) and contextual template generator. The application never crashes.",
            "Internet cut aanaalum quota theerthaalum offline question bank-la irunthu test run aagidum, system fail aagathu!"
        ),
        (
            "Q5: How does the timer countdown prevent cheating or delayed submissions?",
            "The deadline is enforced on both frontend and backend. The frontend runs a JavaScript countdown timer that automatically executes `handleSubmitQuiz()` when it hits zero. Furthermore, the backend stores `due_date` and `due_time`; submissions after deadline cutoff are rejected.",
            "Time mudinja udane screen auto submit aagidum, student thappa submit pannaama escape aaga mudiyathu."
        ),
        (
            "Q6: What is an ORM and why did you use SQLAlchemy?",
            "Object-Relational Mapping (ORM) maps database tables to Python classes. Instead of writing raw SQL strings (`SELECT * FROM students WHERE id = 1`), we interact with Python objects (`db.query(Student).get(1)`). It provides SQL injection prevention, schema migrations, and database independence.",
            "Direct SQL query ezhuthaama Python objects moolama database safe-aa handle panna ORM use pandrom."
        ),
        (
            "Q7: How do you identify weak students?",
            "A student is classified as 'Weak' if either: (1) Their assessment score is below 50% (< 50% marks), or (2) The student explicitly checks the 'I did not understand today's session' toggle (`not_understood = True`) during quiz submission.",
            "Score 50%-ku keela irunthaalo or 'enakku puriyala' nu click pannalo system avangala weak list-la pottudum."
        ),
        (
            "Q8: What is APScheduler and why is it needed?",
            "Advanced Python Scheduler (APScheduler) runs in-process background tasks. It polls every 30 seconds to monitor active deadlines. In the last 10-40 seconds of a quiz window, it compiles session attendance, identifies weak students, and automatically triggers email delivery without human intervention.",
            "Background-la running alarm clock maathiri; deadline mudiyum pothu automatic-aa calculate panni faculty-ku email anuppum."
        ),
        (
            "Q9: How are passwords stored securely?",
            "Passwords are NEVER stored as plain text. We use the `bcrypt` cryptographic hashing library with random salting. Even if someone obtains full database access, bcrypt is computationally expensive and mathematically infeasible to reverse engineer.",
            "Bcrypt one-way hashing use pandrom. Password hash aagi irukkum, yarukkum original password theriyathu."
        ),
        (
            "Q10: What is the difference between DailyTopic and TopicHistory tables?",
            "`DailyTopic` holds only the single currently active topic for each year cohort (it is updated/upserted). `TopicHistory` is an append-only immutable audit trail that saves every topic assigned historically along with the mentor's name and timestamps.",
            "DailyTopic innaiki active-aa irukra topic-ah mattum store pannum. TopicHistory pazhaya ella topics records-um audit trail-aa save pannum."
        ),
        (
            "Q11: How do you handle Cross-Origin Resource Sharing (CORS)?",
            "Since the React frontend runs on port 5173 and FastAPI runs on port 8000, browsers block cross-origin HTTP requests by default. We configure FastAPI's `CORSMiddleware` with allowed origins, methods, and headers to enable safe cross-origin communication.",
            "Frontend and Backend different ports-la run aagurathaala browser security block pannaama irukka CORS configure pandrom."
        ),
        (
            "Q12: How does the AI Chatbot retain context?",
            "Chat history is persisted in the `chat_messages` table with student ID, sender role (`student` or `ai`), and timestamp. When a query is made, relevant context from previous interactions can be injected into the prompt, and past doubts remain accessible across logins.",
            "Chat messages DB-la store aavathaala student logout panni thirumba vanthaalum pazhaya doubts review pannalam."
        ),
        (
            "Q13: Why Tailwind CSS v4 over traditional CSS files?",
            "Tailwind CSS uses utility classes directly in JSX markup. It eliminates CSS file bloat, provides a standardized spacing/typography design system, enables lightning-fast prototyping, and includes built-in dark mode and responsive breakpoints (`md:`, `lg:`).",
            "Custom CSS ezhuthi waste panna theva illa. Class names vachae responsive and modern glassmorphic look create pannalam."
        ),
        (
            "Q14: What is the purpose of Pydantic's `BaseModel`?",
            "Pydantic's `BaseModel` is used in `schemas.py` to define data contracts. It automatically validates incoming JSON types, rejects extra/invalid fields, and serializes Python data objects into clean JSON API responses.",
            "API request and response data types-ah strict-aa check panni validate panra security layer."
        ),
        (
            "Q15: How does the email alerting system work without blocking user requests?",
            "Email dispatch is handled either through background scheduler jobs or asynchronous execution using Resend API / SMTP. The primary user flow doesn't hang waiting for third-party email delivery.",
            "Email anuppurathaala student app hang aagathu; background worker process anuppidum."
        ),
        (
            "Q16: What is a Single Page Application (SPA)?",
            "An SPA loads a single HTML shell (`index.html`) on initial load. Subsequent page transitions occur dynamically via JavaScript DOM manipulation without full browser page reloads, providing a desktop-app-like experience.",
            "Page refresh aagama content mattum fast-aa maarum app structure."
        ),
        (
            "Q17: What happens when a student marks a class as 'Boring'?",
            "The system records the response in the `boring_reports` table linked to the student ID, topic, and date. This qualitative metric is tracked to help mentors assess engagement and adapt pedagogical techniques.",
            "Class dull-aa iruntha anonymous-aa student report pannalam. Faculty teaching style refine panna useful data."
        ),
        (
            "Q18: What is the database auto-seeder (`seed_database`)?",
            "On server startup, `main.py` runs `seed_database()` which checks if initial mock student accounts, mentor credentials, and timetables exist. If empty, it pre-populates the database so the system is immediately testable and functional.",
            "Server start aagum pothu sample students and mentors data illana automatic-aa create panni ready pannidum."
        ),
        (
            "Q19: What is ASGI and how does Uvicorn fit in?",
            "ASGI (Asynchronous Server Gateway Interface) is the asynchronous successor to WSGI. It allows Python web applications to handle asynchronous protocols like WebSockets, HTTP/2, and long-polling. Uvicorn is the high-performance ASGI web server hosting FastAPI.",
            "WSGI synchronous pazhaya model. ASGI async modern model. Uvicorn is the server that runs FastAPI on ASGI."
        ),
        (
            "Q20: What are the future enhancements of EduMentor AI?",
            "Future roadmap includes: (1) Voice-based oral viva testing via Whisper AI, (2) Adaptive difficulty (questions automatically become harder or easier based on real-time performance), (3) Mobile application integration via React Native, and (4) Predictive analytics predicting university semester exam grades.",
            "Voice based viva, dynamic difficulty adjustment, mobile app and semester score prediction add pannalam!"
        )
    ]

    for q, ans_en, ans_tg in viva_qa:
        q_box = []
        q_box.append(Paragraph(f"<b><font color='#1E40AF'>{q}</font></b>", callout_bold))
        q_box.append(Spacer(1, 2))
        q_box.append(Paragraph(f"<b>Examiner-ku Answer (English):</b> {ans_en}", body_style))
        q_box.append(Spacer(1, 2))
        q_box.append(Paragraph(f"<b>Unakku Puriyanum-na (Tanglish Summary):</b> <i>{ans_tg}</i>", tanglish_style))
        
        t_box = Table([[q_box]], colWidths=[W])
        t_box.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), BG_LIGHT),
            ('BOX', (0,0), (-1,-1), 0.75, BORDER_COL),
            ('LINELEFT', (0,0), (0,-1), 3, PRIMARY),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 5),
            ('LEFTPADDING', (0,0), (-1,-1), 8),
            ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ]))
        story.append(t_box)
        story.append(Spacer(1, 6))

    # ═════════════════════════════════════════════════════════════════════════
    # SECTION 11: VIVA GOLDEN TIPS & CONFIDENCE CHECKLIST
    # ═════════════════════════════════════════════════════════════════════════
    story.append(Spacer(1, 4))
    story.append(make_section_banner("11. Viva Hall Golden Rules (Confidence Checklist)", "🏆"))
    story.append(Spacer(1, 6))

    rules = [
        "<b>1. Don't Say 'I Don't Know':</b> Examiner kelvi keta udane blank aagathinga. Say: 'Sir, in our current architecture we handled this using X, but we can also extend it using Y.'",
        "<b>2. Explain the Problem First:</b> 'Before our project, faculty had to wait 3 months for semester results. With EduMentor AI, they get daily feedback in 15 minutes.'",
        "<b>3. Highlight the Fallback AI:</b> Examiner will definitely ask 'Gemini limit mudinja enna pannuvinga?' Answer: 'We implemented a multi-tier fallback with an offline curated question bank so zero downtime!'",
        "<b>4. Show Ownership:</b> Confidently name the files: 'Frontend is in React 19 (`StudentDashboardPage.jsx`), Backend is in FastAPI (`students.py`), Database is managed by SQLAlchemy (`models.py`) and Background tasks by APScheduler (`scheduler.py`).'",
    ]
    for r in rules:
        story.append(Paragraph(r, body_style))
        story.append(Spacer(1, 2))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"[SUCCESS] PDF Generated at: {os.path.abspath(OUTPUT_PDF)}")

if __name__ == "__main__":
    build_pdf()
