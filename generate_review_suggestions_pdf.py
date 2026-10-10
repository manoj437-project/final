from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, HRFlowable
)

OUTPUT = "EduMentor_Testing_Review_Suggestions.pdf"

# ── Colors ────────────────────────────────────────────────────────────────────
NAVY    = colors.HexColor("#1A237E")
BLUE    = colors.HexColor("#1565C0")
DBLUE   = colors.HexColor("#0D47A1")
LGRAY   = colors.HexColor("#F0F2FA")
MGRAY   = colors.HexColor("#C5CAE9")
GREEN   = colors.HexColor("#2E7D32")
LGREEN  = colors.HexColor("#E8F5E9")
RED     = colors.HexColor("#B71C1C")
LRED    = colors.HexColor("#FFEBEE")
ORANGE  = colors.HexColor("#E65100")
LORANGE = colors.HexColor("#FFF3E0")
YELLOW  = colors.HexColor("#F9A825")
LYELLOW = colors.HexColor("#FFFDE7")
WHITE   = colors.white
BLACK   = colors.HexColor("#1A1A1A")
GRAY    = colors.HexColor("#555555")
BORDER  = colors.HexColor("#9FA8DA")
TEAL    = colors.HexColor("#00695C")

W = 17.0 * cm

# ── Page border ───────────────────────────────────────────────────────────────
def page_deco(c, doc):
    c.saveState()
    w, h = A4
    c.setStrokeColor(NAVY); c.setLineWidth(1.5)
    c.rect(1.1*cm, 1.1*cm, w-2.2*cm, h-2.2*cm)
    if doc.page > 1:
        c.setFillColor(NAVY)
        c.setFont("Helvetica", 7)
        c.drawCentredString(w/2, 0.72*cm,
            f"Page {doc.page}  |  EduMentor AI – Testing Review Suggestions & Analysis")
    c.restoreState()

# ── Styles ────────────────────────────────────────────────────────────────────
def S(name, **kw):
    return ParagraphStyle(name, **kw)

title_s   = S("t",  fontName="Helvetica-Bold", fontSize=26, textColor=WHITE,  alignment=TA_CENTER, leading=32)
sub_s     = S("s",  fontName="Helvetica",      fontSize=13, textColor=MGRAY,  alignment=TA_CENTER, leading=18)
info_s    = S("i",  fontName="Helvetica",      fontSize=10, textColor=WHITE,  alignment=TA_CENTER)
sec_s     = S("sc", fontName="Helvetica-Bold", fontSize=11, textColor=WHITE,  alignment=TA_LEFT,  leftIndent=8, leading=15)
head2_s   = S("h2", fontName="Helvetica-Bold", fontSize=11, textColor=NAVY,   alignment=TA_LEFT,  spaceBefore=6, spaceAfter=3)
head3_s   = S("h3", fontName="Helvetica-Bold", fontSize=10, textColor=DBLUE,  alignment=TA_LEFT,  spaceBefore=4, spaceAfter=2)
body_s    = S("b",  fontName="Helvetica",      fontSize=9.5,textColor=BLACK,  alignment=TA_LEFT,  spaceAfter=2, leading=14)
note_s    = S("n",  fontName="Helvetica-Oblique", fontSize=9, textColor=GRAY, alignment=TA_LEFT,  spaceAfter=3)
cell_s    = S("c",  fontName="Helvetica",      fontSize=8.5,textColor=BLACK,  alignment=TA_LEFT,  leading=12, wordWrap="CJK")
hdr_s     = S("hc", fontName="Helvetica-Bold", fontSize=8.5,textColor=WHITE,  alignment=TA_LEFT,  leading=12)
code_s    = S("cd", fontName="Courier",        fontSize=8,  textColor=TEAL,   alignment=TA_LEFT,  leading=12, leftIndent=8, spaceAfter=4)
alert_r_s = S("ar", fontName="Helvetica-Bold", fontSize=9,  textColor=RED,    alignment=TA_LEFT,  leading=13)
alert_g_s = S("ag", fontName="Helvetica-Bold", fontSize=9,  textColor=GREEN,  alignment=TA_LEFT,  leading=13)
alert_o_s = S("ao", fontName="Helvetica-Bold", fontSize=9,  textColor=ORANGE, alignment=TA_LEFT,  leading=13)

def sp(n=0.15): return Spacer(1, n*cm)

# ── Helpers ───────────────────────────────────────────────────────────────────
def banner(text, color=NAVY):
    t = Table([[Paragraph(text, sec_s)]], colWidths=[W])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), color),
        ("TOPPADDING",    (0,0),(-1,-1), 7),
        ("BOTTOMPADDING", (0,0),(-1,-1), 7),
        ("LEFTPADDING",   (0,0),(-1,-1), 12),
    ]))
    return t

def tbl(data, widths, hdr_color=BLUE):
    wrapped = []
    for r_idx, row in enumerate(data):
        new_row = []
        for cell in row:
            style = hdr_s if r_idx == 0 else cell_s
            if not isinstance(cell, Paragraph):
                cell = Paragraph(str(cell), style)
            new_row.append(cell)
        wrapped.append(new_row)
    t = Table(wrapped, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),  hdr_color),
        ("GRID",          (0,0),(-1,-1), 0.4, BORDER),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [WHITE, LGRAY]),
        ("LEFTPADDING",   (0,0),(-1,-1), 6),
        ("RIGHTPADDING",  (0,0),(-1,-1), 6),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("VALIGN",        (0,0),(-1,-1), "TOP"),
    ]))
    return t

def alert_box(text, style, bg):
    t = Table([[Paragraph(text, style)]], colWidths=[W])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), bg),
        ("LEFTPADDING",   (0,0),(-1,-1), 12),
        ("RIGHTPADDING",  (0,0),(-1,-1), 12),
        ("TOPPADDING",    (0,0),(-1,-1), 8),
        ("BOTTOMPADDING", (0,0),(-1,-1), 8),
        ("LINEABOVE",     (0,0),(-1,0),  2, RED if bg==LRED else (GREEN if bg==LGREEN else ORANGE)),
    ]))
    return t

def code_box(lines):
    text = "<br/>".join(lines)
    t = Table([[Paragraph(text, code_s)]], colWidths=[W])
    t.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), colors.HexColor("#F5F5F5")),
        ("LEFTPADDING",   (0,0),(-1,-1), 12),
        ("TOPPADDING",    (0,0),(-1,-1), 8),
        ("BOTTOMPADDING", (0,0),(-1,-1), 8),
        ("GRID",          (0,0),(-1,-1), 0.3, BORDER),
    ]))
    return t

def green_col(t, col, rows):
    t.setStyle(TableStyle([
        ("TEXTCOLOR", (col,1),(col,rows), GREEN),
        ("FONTNAME",  (col,1),(col,rows), "Helvetica-Bold"),
    ]))

def priority_col(t, col, rows_data):
    """Color priority column based on text."""
    for i, row in enumerate(rows_data[1:], start=1):
        val = str(row[col]) if col < len(row) else ""
        if "High" in val or "🔴" in val:
            t.setStyle(TableStyle([("TEXTCOLOR",(col,i),(col,i), RED),("FONTNAME",(col,i),(col,i),"Helvetica-Bold")]))
        elif "Medium" in val or "🟡" in val:
            t.setStyle(TableStyle([("TEXTCOLOR",(col,i),(col,i), ORANGE),("FONTNAME",(col,i),(col,i),"Helvetica-Bold")]))
        elif "Low" in val or "🟢" in val:
            t.setStyle(TableStyle([("TEXTCOLOR",(col,i),(col,i), GREEN),("FONTNAME",(col,i),(col,i),"Helvetica-Bold")]))

# ═══════════════════════════════════════════════════════════════════════════════
def build():
    doc = SimpleDocTemplate(OUTPUT, pagesize=A4,
        leftMargin=2.0*cm, rightMargin=2.0*cm,
        topMargin=2.2*cm, bottomMargin=2.1*cm)
    story = []

    # ── COVER PAGE ─────────────────────────────────────────────────────────────
    cover = Table([[Paragraph("EduMentor AI", title_s)]], colWidths=[W])
    cover.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), NAVY),
        ("TOPPADDING",    (0,0),(-1,-1), 36),
        ("BOTTOMPADDING", (0,0),(-1,-1), 18),
    ]))
    story.append(cover)

    sub = Table([[Paragraph("Testing & Validation — Review Suggestions & Gap Analysis", sub_s)]], colWidths=[W])
    sub.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), BLUE),
        ("TOPPADDING",    (0,0),(-1,-1), 12),
        ("BOTTOMPADDING", (0,0),(-1,-1), 12),
    ]))
    story.append(sub)
    story.append(sp(0.7))

    details = [
        ["Project",    "EduMentor AI"],
        ["Stack",      "React + FastAPI + PostgreSQL + Google Gemini AI"],
        ["Team",       "24UCS07, 24UCS13"],
        ["Based on",   "EduMentor_Testing_Validation_Review.pdf (46 existing TCs)"],
        ["Date",       "08-09-2026"],
        ["Purpose",    "Identify missing tests & suggest improvements for Review 3"],
    ]
    dt = Table(
        [[Paragraph(f"<b>{r[0]}</b>", body_s), Paragraph(r[1], body_s)] for r in details],
        colWidths=[3.8*cm, 13.2*cm]
    )
    dt.setStyle(TableStyle([
        ("BACKGROUND",   (0,0),(0,-1), LGRAY),
        ("TEXTCOLOR",    (0,0),(0,-1), NAVY),
        ("GRID",         (0,0),(-1,-1), 0.4, BORDER),
        ("LEFTPADDING",  (0,0),(-1,-1), 8),
        ("TOPPADDING",   (0,0),(-1,-1), 6),
        ("BOTTOMPADDING",(0,0),(-1,-1), 6),
        ("ROWBACKGROUNDS",(0,0),(-1,-1), [LGRAY, WHITE]),
    ]))
    story.append(dt)
    story.append(sp(0.5))

    # Quick-stats box
    stats = Table([[
        Table([[Paragraph("<b>46</b>", S("st", fontName="Helvetica-Bold", fontSize=22, textColor=NAVY, alignment=TA_CENTER)),
                Paragraph("Existing TCs", S("sl", fontName="Helvetica", fontSize=9, textColor=GRAY, alignment=TA_CENTER))]], colWidths=[3.5*cm]),
        Table([[Paragraph("<b>27</b>", S("st2", fontName="Helvetica-Bold", fontSize=22, textColor=RED, alignment=TA_CENTER)),
                Paragraph("Missing Tests Found", S("sl2", fontName="Helvetica", fontSize=9, textColor=GRAY, alignment=TA_CENTER))]], colWidths=[3.5*cm]),
        Table([[Paragraph("<b>5</b>", S("st3", fontName="Helvetica-Bold", fontSize=22, textColor=ORANGE, alignment=TA_CENTER)),
                Paragraph("Improvement Areas", S("sl3", fontName="Helvetica", fontSize=9, textColor=GRAY, alignment=TA_CENTER))]], colWidths=[3.5*cm]),
        Table([[Paragraph("<b>81</b>", S("st4", fontName="Helvetica-Bold", fontSize=22, textColor=GREEN, alignment=TA_CENTER)),
                Paragraph("Recommended Total", S("sl4", fontName="Helvetica", fontSize=9, textColor=GRAY, alignment=TA_CENTER))]], colWidths=[4.5*cm]),
    ]], colWidths=[3.8*cm, 3.8*cm, 3.8*cm, 4.6*cm])
    stats.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), LGRAY),
        ("GRID",          (0,0),(-1,-1), 0.4, BORDER),
        ("TOPPADDING",    (0,0),(-1,-1), 10),
        ("BOTTOMPADDING", (0,0),(-1,-1), 10),
        ("ALIGN",         (0,0),(-1,-1), "CENTER"),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
    ]))
    story.append(stats)
    story.append(PageBreak())

    # ── SECTION A: WHAT THE EXISTING DOCUMENT DOES WELL ───────────────────────
    story.append(banner("A.  What the Existing Document Does Well", GREEN))
    story.append(sp(0.1))
    story.append(Paragraph(
        "The current Testing & Validation Review is well-structured and covers the core testing layers. "
        "The following strengths were identified:", body_s))
    story.append(sp(0.1))
    strengths = [
        ["Strength", "Detail"],
        ["4-level testing structure", "Unit → Integration → Validation → System testing — proper layering"],
        ["Equivalence partitioning", "Year, Score, Email, Password, Topic fields all covered"],
        ["Security tests included", "SQL injection, XSS, role escalation, bcrypt hash check"],
        ["Bug tracking section", "5 bugs logged with location and fix status"],
        ["Performance baselines", "Measured actual vs target (login ~180ms, chat ~1.2s, dashboard ~950ms)"],
        ["Validation against FRs", "All 13 functional requirements traced to test cases"],
    ]
    ts = tbl(strengths, [4.5*cm, 12.5*cm], NAVY)
    story.append(ts)
    story.append(PageBreak())

    # ── SECTION B: MISSING TESTS ───────────────────────────────────────────────
    story.append(banner("B.  Missing Tests Found (Cross-checked with Source Code)", RED))
    story.append(sp(0.1))
    story.append(Paragraph(
        "These features exist in the actual codebase but have zero test coverage in the current document.", note_s))
    story.append(sp(0.1))

    # B.1 OTP / Forgot Password
    story.append(Paragraph("B.1 — OTP / Forgot Password Flow  (auth.py  Lines 207–283)", head2_s))
    story.append(alert_box(
        "⚠  CRITICAL: A full OTP-based forgot/reset password system exists in auth.py — "
        "7 test cases are completely missing from the document.",
        alert_r_s, LRED))
    story.append(sp(0.1))
    otp = [
        ["TC#", "What to Test", "Input", "Expected Output"],
        ["UT-NEW-01", "Forgot password — valid student email", "POST /forgot-password + registered email", "OTP sent, success: true"],
        ["UT-NEW-02", "Forgot password — unregistered email", "Unknown email + role: student", "404 Not Found"],
        ["UT-NEW-03", "Reset password — valid OTP", "Correct OTP + new password (≥6 chars)", "Password updated, OTP deleted from store"],
        ["UT-NEW-04", "Reset password — expired OTP", "OTP used after 10-minute window", "400 OTP has expired"],
        ["UT-NEW-05", "Reset password — wrong OTP", "Incorrect 6-digit OTP", "400 Invalid OTP"],
        ["UT-NEW-06", "Reset — password too short", "new_password < 6 characters", "400 Password must be at least 6 characters"],
        ["UT-NEW-07", "Forgot password — invalid role", "role: admin (not student/mentor)", "400 Invalid role"],
    ]
    to = tbl(otp, [2.2*cm, 4.0*cm, 5.0*cm, 5.8*cm])
    story.append(to)
    story.append(sp(0.15))
    story.append(Paragraph("Example — UT-NEW-03 test verification:", head3_s))
    story.append(code_box([
        "POST  /api/auth/reset-password",
        'Body: { "email": "arun@edumentor.edu", "otp": "123456",',
        '        "new_password": "newpass123", "role": "student" }',
        "",
        'Expected Response: { "success": true,',
        '   "message": "Password reset successful! You can now login..." }',
        "Assert: student.password_hash in DB starts with '$2b$' (bcrypt)",
    ]))
    story.append(sp(0.2))

    # B.2 Quiz Generation
    story.append(Paragraph("B.2 — AI Quiz Generation Endpoint  (students.py)", head2_s))
    quiz = [
        ["TC#", "What to Test", "Input", "Expected Output"],
        ["UT-NEW-08", "Generate AI quiz for a topic", "POST /students/generate-quiz + topic + subject (authenticated)", "Returns MCQ, TF, fill-in, short questions"],
        ["UT-NEW-09", "Quiz generation — unauthenticated", "No auth token", "401 Unauthorized"],
        ["UT-NEW-10", "Quiz generation — empty topic", "Blank topic field", "422 Validation Error"],
    ]
    tq = tbl(quiz, [2.2*cm, 4.2*cm, 4.6*cm, 5.0*cm])
    story.append(tq)
    story.append(sp(0.2))

    # B.3 Quiz Status
    story.append(Paragraph("B.3 — Quiz Status / Duplicate Submission Prevention  (students.py)", head2_s))
    story.append(Paragraph(
        "Endpoint GET /api/students/quiz-status prevents students from submitting the same quiz twice. Not tested.", note_s))
    qstatus = [
        ["TC#", "What to Test", "Input", "Expected Output"],
        ["UT-NEW-11", "Quiz status — not yet attempted", "Valid student token + topic name", '{ "attempted": false }'],
        ["UT-NEW-12", "Quiz status — already submitted", "Same student + same topic (after submission)", '{ "attempted": true }'],
        ["IT-NEW-01", "Submit quiz twice (integration)", "Score POST → check status → POST again", "Second submit blocked or flagged by system"],
    ]
    tqs = tbl(qstatus, [2.2*cm, 4.0*cm, 4.6*cm, 6.2*cm])
    story.append(tqs)
    story.append(sp(0.2))

    # B.4 Topic History
    story.append(Paragraph("B.4 — Topic History & Due-Time Expiry  (timetable.py  Lines 113–132, 321–347)", head2_s))
    hist = [
        ["TC#", "What to Test", "Input", "Expected Output"],
        ["UT-NEW-13", "Get topic history for year 1", "GET /timetable/history?year=1", "Returns list of all past topics, newest first"],
        ["UT-NEW-14", "Set topic twice — both rows logged", "Two set-today calls for year 2", "History has 2 rows; DailyTopic has 1 (upserted)"],
        ["ST-NEW-01", "Topic marked expired after due time", "set-today with due_time = past time", '"is_expired": true in get-today response'],
        ["ST-NEW-02", "Topic not expired before due time", "set-today with due_time = 2 hours ahead", '"is_expired": false in get-today response'],
    ]
    th = tbl(hist, [2.2*cm, 4.2*cm, 4.6*cm, 6.0*cm])
    story.append(th)
    story.append(sp(0.2))

    # B.5 Mentor Registration
    story.append(Paragraph("B.5 — Mentor Registration  (auth.py  Lines 144–165)", head2_s))
    mreg = [
        ["TC#", "What to Test", "Input", "Expected Output"],
        ["UT-NEW-17", "Mentor register — valid data", "POST /auth/mentor/register with name, dept, identity, password", "201 Created — new mentor record"],
        ["UT-NEW-18", "Mentor register — duplicate identity", "Same identity (email/ID) used again", "400 Mentor identity already registered"],
    ]
    tmr = tbl(mreg, [2.2*cm, 4.2*cm, 5.4*cm, 5.2*cm])
    story.append(tmr)
    story.append(sp(0.2))

    # B.6 Weekly Timetable Save
    story.append(Paragraph("B.6 — Weekly Timetable Save by Mentor  (timetable.py  Lines 265–296)", head2_s))
    wsave = [
        ["TC#", "What to Test", "Input", "Expected Output"],
        ["IT-NEW-02", "Mentor saves full weekly timetable", "POST /timetable/weekly with year=2 + full schedule JSON", "Old records deleted, new records saved correctly"],
        ["IT-NEW-03", "Student views updated timetable", "Student logs in, opens timetable after mentor update", "Shows newly saved subjects and topics"],
    ]
    tws = tbl(wsave, [2.2*cm, 4.2*cm, 5.2*cm, 5.4*cm])
    story.append(tws)
    story.append(sp(0.2))

    # B.7 Gemini Fallback
    story.append(Paragraph("B.7 — Gemini AI Fallback Behavior  (chat.py  Lines 74–126)", head2_s))
    gfb = [
        ["TC#", "What to Test", "Condition", "Expected Output"],
        ["UT-NEW-20", "Chatbot responds when Gemini is down", "Invalid / missing GEMINI_API_KEY in .env", "Fallback reply returned, no server crash"],
        ["UT-NEW-21", "Off-topic messages are redirected", "Student asks about unrelated topic", "AI replies: 'I can only help with [assigned topic] today'"],
    ]
    tgf = tbl(gfb, [2.2*cm, 4.2*cm, 4.8*cm, 5.8*cm])
    story.append(tgf)
    story.append(sp(0.2))

    # B.8 Other
    story.append(Paragraph("B.8 — Other Missing Tests", head2_s))
    other = [
        ["TC#", "What to Test", "Where", "Expected Output"],
        ["UT-NEW-15", "Get learning resources for topic", "GET /students/resources + valid token", "Returns resource list for assigned topic"],
        ["UT-NEW-16", "Resources endpoint — unauthenticated", "No auth token", "401 Unauthorized"],
        ["UT-NEW-19", "Welcome email triggered on register", "POST /auth/student/register (new account)", "Email queued to Resend/SMTP for new student"],
        ["ST-NEW-03", "CORS wildcard check", "Review allow_origins in main.py", "Should be restricted to frontend domain in production"],
    ]
    tot = tbl(other, [2.2*cm, 4.2*cm, 4.6*cm, 6.0*cm])
    story.append(tot)
    story.append(PageBreak())

    # ── SECTION C: IMPROVEMENT SUGGESTIONS ────────────────────────────────────
    story.append(banner("C.  Suggestions to Improve Existing Tests", BLUE))
    story.append(sp(0.1))

    # C.1
    story.append(Paragraph("C.1 — Add FAIL Cases to the Document", head2_s))
    story.append(Paragraph(
        "Every existing test currently shows PASS. A complete review document should include "
        "2–3 intentional failures to demonstrate the test suite actually catches bugs.", body_s))
    fail_ex = [
        ["TC#", "Input", "Expected", "Actual (Before Fix)", "Result"],
        ["UT-15", "score = -5", "422 Error", "Score saved incorrectly", "FAIL → Fixed"],
        ["IT-05", "No token on mentor route", "403 Forbidden", "200 OK (no auth check)", "FAIL → Fixed"],
    ]
    tfe = tbl(fail_ex, [1.5*cm, 3.2*cm, 3.5*cm, 5.0*cm, 3.8*cm])
    story.append(tfe)
    story.append(sp(0.2))

    # C.2
    story.append(Paragraph("C.2 — Equivalence Partitioning Table Has Gaps", head2_s))
    ep_gaps = [
        ["Field", "Current EP Coverage", "Missing / Gap"],
        ["Year", "1, 2, 3 (string)", "Integer 1 sent instead of string — what happens?"],
        ["Topic Name", "Any text, 1 char, 255 chars", "Unicode / emoji (topics use emoji: 'Variables 📦')"],
        ["Password", "Less than 8 chars", "Password = only spaces (should fail but may not)"],
        ["Email", "Valid / invalid format", "Case sensitivity: ARUN@EMAIL.COM vs arun@email.com"],
    ]
    tep = tbl(ep_gaps, [2.5*cm, 5.5*cm, 9.0*cm])
    story.append(tep)
    story.append(sp(0.2))

    # C.3
    story.append(Paragraph("C.3 — Integration Tests Have No Failure Paths", head2_s))
    story.append(Paragraph(
        "All 6 integration tests (IT-01 to IT-06) cover only the happy path. "
        "Add at least one failure-scenario integration test.", body_s))
    it_new = [
        ["TC#", "Scenario", "Modules Connected", "Expected"],
        ["IT-07", "Student tries to access mentor dashboard", "auth → students → MentorDashboard", "403 Forbidden"],
        ["IT-08", "Mentor sets topic for invalid year (e.g., year=5)", "timetable → DailyTopic", "Graceful fallback or validation error"],
    ]
    tit = tbl(it_new, [1.5*cm, 5.0*cm, 5.5*cm, 5.0*cm])
    story.append(tit)
    story.append(sp(0.2))

    # C.4
    story.append(Paragraph("C.4 — Add Non-Functional Requirements (NFR) to Validation Section", head2_s))
    nfr = [
        ["NFR#", "Requirement", "How to Test"],
        ["NFR-01", "All passwords must be hashed — never stored in plaintext", "DB inspection: password_hash starts with $2b$ (bcrypt)"],
        ["NFR-02", "All API responses within 500 ms under normal load", "Timer on each endpoint using Postman / pytest"],
        ["NFR-03", "CORS headers correctly restrict origins in production", "cURL or browser devtools check for allowed origins"],
        ["NFR-04", "JWT tokens expire after configured duration", "Wait past token expiry, retry request — expect 401"],
    ]
    tnfr = tbl(nfr, [1.5*cm, 7.5*cm, 8.0*cm])
    story.append(tnfr)
    story.append(sp(0.2))

    # C.5 Security
    story.append(Paragraph("C.5 — Expand Security Testing Section", head2_s))
    story.append(alert_box(
        "⚠  IMPORTANT: The in-memory OTP store (_otp_store in auth.py) resets on every server restart. "
        "Any pending OTP is lost. This architectural risk must be documented.",
        alert_o_s, LORANGE))
    story.append(sp(0.1))
    sec_new = [
        ["TC#", "What to Test", "How Tested", "Expected"],
        ["ST-NEW-04", "Brute-force login attempts", "Send 50 wrong password requests to /auth/student/login", "No rate limiting — document as known risk"],
        ["ST-NEW-05", "OTP cleared on server restart", "Request OTP → restart server → use OTP", "400 No OTP found — OTP lost (document risk)"],
        ["ST-NEW-06", "CORS wildcard in production", "Check main.py allow_origins=[\"*\"]", "Should be restricted to frontend domain only"],
        ["ST-NEW-07", "Mentor token registers another mentor", "Use mentor JWT to POST /auth/mentor/register", "Should require admin auth or be restricted"],
    ]
    tsn = tbl(sec_new, [2.2*cm, 4.0*cm, 5.0*cm, 5.8*cm])
    story.append(tsn)
    story.append(sp(0.2))

    # C.6 Performance
    story.append(Paragraph("C.6 — Increase Concurrent Users in Performance Testing", head2_s))
    perf_new = [
        ["Metric", "Current Target", "Current Actual", "Recommended Target"],
        ["Concurrent users", "10+", "15 tested", "25+ (realistic class: 21 students seeded)"],
        ["AI chat under load", "Not tested", "Not tested", "5 simultaneous Gemini requests"],
        ["DB with 1000 score records", "Not tested", "Not tested", "Query time < 300 ms"],
        ["Timetable weekly fetch", "Not tested", "Not tested", "< 200 ms for full 3-year schedule"],
    ]
    tpn = tbl(perf_new, [4.5*cm, 3.5*cm, 3.5*cm, 5.5*cm], NAVY)
    story.append(tpn)
    story.append(PageBreak())

    # ── SECTION D: SUMMARY OF MISSING TESTS ───────────────────────────────────
    story.append(banner("D.  Summary of All Missing Tests", NAVY))
    story.append(sp(0.1))

    missing_summary = [
        ["Category", "Missing Tests", "Priority"],
        ["OTP / Forgot Password (auth.py)", "7 tests", "HIGH"],
        ["Quiz Generation & Status (students.py)", "3 tests", "HIGH"],
        ["Security Gaps (CORS, Brute-force, OTP memory)", "4 tests", "HIGH"],
        ["Topic History & Due-Time Expiry (timetable.py)", "4 tests", "MEDIUM"],
        ["Mentor Registration (auth.py)", "2 tests", "MEDIUM"],
        ["Weekly Timetable Save (timetable.py)", "2 tests", "MEDIUM"],
        ["Gemini AI Fallback (chat.py)", "2 tests", "MEDIUM"],
        ["Learning Resources Endpoint", "2 tests", "LOW"],
        ["Welcome Email on Registration", "1 test", "LOW"],
        ["TOTAL", "27 tests", ""],
    ]
    tsm = tbl(missing_summary, [8.5*cm, 3.5*cm, 5.0*cm], NAVY)
    # Color priority column
    tsm.setStyle(TableStyle([
        ("TEXTCOLOR", (2,1),(2,3), RED),   ("FONTNAME",(2,1),(2,3),"Helvetica-Bold"),
        ("TEXTCOLOR", (2,4),(2,7), ORANGE),("FONTNAME",(2,4),(2,7),"Helvetica-Bold"),
        ("TEXTCOLOR", (2,8),(2,9), GREEN), ("FONTNAME",(2,8),(2,9),"Helvetica-Bold"),
        ("BACKGROUND",(0,-1),(-1,-1), MGRAY),
        ("FONTNAME",  (0,-1),(-1,-1),"Helvetica-Bold"),
        ("TEXTCOLOR", (0,-1),(-1,-1), NAVY),
    ]))
    story.append(tsm)
    story.append(sp(0.3))

    # ── SECTION E: RECOMMENDED UPDATED SUMMARY ────────────────────────────────
    story.append(banner("E.  Recommended Updated Test Count for Review 3", GREEN))
    story.append(sp(0.1))

    upd = [
        ["Testing Level", "Current TCs", "New to Add", "Recommended Total", "Pass Target"],
        ["Unit Testing",        "16", "+21", "37", "37"],
        ["Integration Testing", "6",  "+3",  "9",  "9"],
        ["Validation Testing",  "13", "+4",  "17", "17"],
        ["System Testing",      "11", "+7",  "18", "18"],
        ["TOTAL",               "46", "+35", "81", "81"],
    ]
    tu = tbl(upd, [5.0*cm, 2.8*cm, 2.8*cm, 4.0*cm, 3.4*cm], NAVY)
    tu.setStyle(TableStyle([
        ("BACKGROUND", (0,-1),(-1,-1), MGRAY),
        ("FONTNAME",   (0,-1),(-1,-1), "Helvetica-Bold"),
        ("TEXTCOLOR",  (4,1), (4,-1),  GREEN),
        ("FONTNAME",   (4,1), (4,-1),  "Helvetica-Bold"),
        ("ALIGN",      (1,0), (-1,-1), "CENTER"),
    ]))
    story.append(tu)
    story.append(sp(0.3))

    # Quick-win tip
    story.append(alert_box(
        "✅  QUICK WIN for Review 3:\n"
        "Add the 7 OTP tests + 2 quiz-status tests + 3 security gap tests = 12 high-priority tests "
        "in one session. These cover real working endpoints that currently have zero documentation.",
        alert_g_s, LGREEN))
    story.append(sp(0.2))

    # Final note box
    final = Table([[
        Paragraph(
            "<b>Reviewer Note:</b>  The existing document is well-written and demonstrates good "
            "testing discipline. The 27 missing tests are not failures of the current work — "
            "they are features that were implemented but not yet documented in the test plan. "
            "Prioritise the OTP, quiz-status, and security gap tests before Review 3 as these "
            "cover production-ready endpoints and known architectural risks.", body_s)
    ]], colWidths=[W])
    final.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), LGRAY),
        ("LEFTPADDING",   (0,0),(-1,-1), 12),
        ("RIGHTPADDING",  (0,0),(-1,-1), 12),
        ("TOPPADDING",    (0,0),(-1,-1), 10),
        ("BOTTOMPADDING", (0,0),(-1,-1), 10),
        ("LINEABOVE",     (0,0),(-1,0),  2, NAVY),
    ]))
    story.append(final)

    doc.build(story, onFirstPage=page_deco, onLaterPages=page_deco)
    print("PDF generated: " + OUTPUT)

if __name__ == "__main__":
    build()
