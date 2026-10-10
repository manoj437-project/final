"""Helper script: writes scheduler.py to the same directory."""
import os, textwrap

content = textwrap.dedent('''\
"""
EduMentor AI - Background Scheduler
Runs every 30s, sends full session report to all mentors 1 minute before
the quiz deadline expires.
"""

import datetime
import logging
import smtplib
import urllib.request
import json as _json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from apscheduler.schedulers.background import BackgroundScheduler

from app.database import SessionLocal
from app.models import DailyTopic, Student, StudentScore, BoringReport, Mentor
from app.config import settings

logger = logging.getLogger(__name__)

# Dedup set — (year, topic, due_date, due_time)
_sent_reports: set = set()

LEAD_MINUTES = 1   # minutes before deadline


def _build_and_send_report(year: str, topic: str, today_str: str, deadline_label: str):
    """Build the full HTML session report and email it to every mentor."""
    db = SessionLocal()
    try:
        YEAR_FULL = {"1": "1st Year", "2": "2nd Year", "3": "3rd Year"}
        year_label = YEAR_FULL.get(year, f"Year {year}")

        all_students = (
            db.query(Student)
            .filter(Student.year == year)
            .order_by(Student.username.asc())
            .all()
        )
        total = len(all_students)
        if total == 0:
            logger.info(f"[Scheduler] No students for year {year} — skipping.")
            return

        not_understood_list, weak_list, good_list, all_students_data = [], [], [], []

        for s in all_students:
            score_rec = (
                db.query(StudentScore)
                .filter(
                    StudentScore.student_id == s.id,
                    StudentScore.topic == topic,
                    StudentScore.date == today_str,
                )
                .order_by(StudentScore.created_at.desc())
                .first()
            )
            if not score_rec:
                score_rec = (
                    db.query(StudentScore)
                    .filter(StudentScore.student_id == s.id)
                    .order_by(StudentScore.created_at.desc())
                    .first()
                )

            if score_rec:
                base = {"name": s.username, "regno": s.regno, "score": score_rec.score, "percentage": score_rec.percentage}
                if score_rec.not_understood:
                    not_understood_list.append({**base, "email": s.email})
                    all_students_data.append({**base, "status": "not_understood"})
                elif score_rec.percentage < 50:
                    weak_list.append({**base, "email": s.email})
                    all_students_data.append({**base, "status": "weak"})
                else:
                    good_list.append(base)
                    all_students_data.append({**base, "status": "good"})
            else:
                all_students_data.append({"name": s.username, "regno": s.regno, "score": None, "percentage": None, "status": "missed"})

        weak_count = len(not_understood_list) + len(weak_list)
        weak_pct   = round((weak_count / total) * 100) if total else 0

        boring_recs = (
            db.query(BoringReport)
            .join(Student, BoringReport.student_id == Student.id)
            .filter(Student.year == year, BoringReport.date == today_str)
            .all()
        )
        seen_boring: set = set()
        boring_students = []
        for br in boring_recs:
            s = db.query(Student).filter(Student.id == br.student_id).first()
            if s and s.regno not in seen_boring:
                seen_boring.add(s.regno)
                boring_students.append({"name": s.username, "regno": s.regno, "email": s.email})

        boring_count = len(boring_students)
        boring_pct   = round((boring_count / total) * 100) if total else 0
        missed_count = sum(1 for sd in all_students_data if sd["status"] == "missed")

        weak_color   = "#EF4444" if weak_pct > 50 else "#F59E0B" if weak_pct > 25 else "#10B981"
        boring_color = "#F59E0B" if boring_pct > 30 else "#6B7280"

        # Banners
        pre_banner = (
            "<div style=\\'background:#f0f9ff;border:2px solid #7dd3fc;border-radius:12px;padding:14px 20px;margin-bottom:24px;\\'>"
            f"<strong style=\\'color:#0369a1\\'>&#9200; Auto Report &mdash; {LEAD_MINUTES} Minute Before Deadline:</strong> "
            f"This report was automatically generated <strong>{LEAD_MINUTES} minute before</strong> "
            f"the quiz on <strong>&quot;{topic}&quot;</strong> expires. "
            "Students who have not submitted will show as <em>Missed</em>."
            "</div>"
        )

        alert = ""
        if weak_pct > 50:
            alert = (
                "<div style=\\'background:#fef2f2;border:2px solid #fca5a5;border-radius:12px;padding:16px 20px;margin-bottom:24px;\\'>"
                f"<strong style=\\'color:#EF4444\\'>&#9888; Action Required:</strong> More than 50% of students are struggling on "
                f"<strong>&quot;{topic}&quot;</strong>. Please consider a re-teaching session."
                "</div>"
            )
        elif boring_pct > 30:
            alert = (
                "<div style=\\'background:#fffbeb;border:2px solid #fcd34d;border-radius:12px;padding:16px 20px;margin-bottom:24px;\\'>"
                f"<strong style=\\'color:#D97706\\'>&#128564; Engagement Alert:</strong> {boring_pct}% of students found the class boring. "
                "Consider varying your teaching approach."
                "</div>"
            )

        # Marks table
        ST = {
            "good":           ("&#9989; Good",            "#dcfce7", "#16a34a"),
            "weak":           ("&#9888; Weak",            "#fff3f3", "#EF4444"),
            "not_understood": ("&#10060; Not Understood", "#fdf4ff", "#9333ea"),
            "missed":         ("&#128308; Missed",        "#fffbf0", "#D97706"),
        }
        all_rows = ""
        for sd in all_students_data:
            lbl, rbg, tc = ST.get(sd["status"], ("&#8212;", "#fff", "#111"))
            ps = f"{sd[\'percentage\']}%" if sd["percentage"] is not None else "&#8212;"
            ss = sd.get("score") or "&#8212;"
            all_rows += (
                f"<tr style=\\'background:{rbg}\\'>"
                f"<td style=\\'padding:9px 12px;border-bottom:1px solid #e5e7eb\\'>{sd[\'name\']}</td>"
                f"<td style=\\'padding:9px 12px;border-bottom:1px solid #e5e7eb;font-family:monospace;font-size:.82rem\\'>{sd[\'regno\']}</td>"
                f"<td style=\\'padding:9px 12px;border-bottom:1px solid #e5e7eb;font-weight:700\\'>{ss}</td>"
                f"<td style=\\'padding:9px 12px;border-bottom:1px solid #e5e7eb;text-align:center;font-weight:800;color:{tc}\\'>{ps}</td>"
                f"<td style=\\'padding:9px 12px;border-bottom:1px solid #e5e7eb;font-weight:700;color:{tc}\\'>{lbl}</td></tr>"
            )

        nu_rows = "".join(
            f"<tr style=\\'background:#fdf4ff\\'><td style=\\'padding:9px 12px;border-bottom:1px solid #e5e7eb\\'>{s[\'name\']}</td>"
            f"<td style=\\'padding:9px 12px;border-bottom:1px solid #e5e7eb;font-family:monospace\\'>{s[\'regno\']}</td>"
            f"<td style=\\'padding:9px 12px;border-bottom:1px solid #e5e7eb\\'>{s[\'email\']}</td>"
            f"<td style=\\'padding:9px 12px;border-bottom:1px solid #e5e7eb;color:#9333ea;font-weight:700\\'>&#10060; {s[\'score\']} ({s[\'percentage\']}%)</td></tr>"
            for s in not_understood_list
        ) if not_understood_list else "<tr><td colspan=\\'4\\' style=\\'padding:12px;text-align:center;color:#6b7280\\'>No students reported not understanding &#127881;</td></tr>"

        wk_rows = "".join(
            f"<tr style=\\'background:#fff3f3\\'><td style=\\'padding:9px 12px;border-bottom:1px solid #e5e7eb\\'>{w[\'name\']}</td>"
            f"<td style=\\'padding:9px 12px;border-bottom:1px solid #e5e7eb;font-family:monospace\\'>{w[\'regno\']}</td>"
            f"<td style=\\'padding:9px 12px;border-bottom:1px solid #e5e7eb\\'>{w[\'email\']}</td>"
            f"<td style=\\'padding:9px 12px;border-bottom:1px solid #e5e7eb;color:#EF4444;font-weight:700\\'>&#9888; {w[\'score\']} ({w[\'percentage\']}%)</td></tr>"
            for w in weak_list
        ) if weak_list else "<tr><td colspan=\\'4\\' style=\\'padding:12px;text-align:center;color:#6b7280\\'>No low-score students &#127881;</td></tr>"

        br_rows = "".join(
            f"<tr style=\\'background:#fffbeb\\'><td style=\\'padding:9px 12px;border-bottom:1px solid #e5e7eb\\'>{bs[\'name\']}</td>"
            f"<td style=\\'padding:9px 12px;border-bottom:1px solid #e5e7eb;font-family:monospace\\'>{bs[\'regno\']}</td>"
            f"<td style=\\'padding:9px 12px;border-bottom:1px solid #e5e7eb\\'>{bs[\'email\']}</td></tr>"
            for bs in boring_students
        ) if boring_students else "<tr><td colspan=\\'3\\' style=\\'padding:12px;text-align:center;color:#6b7280\\'>No boring reports today &#128522;</td></tr>"

        CSS = (
            "body{font-family:Arial,sans-serif;background:#f4f6fb;margin:0;padding:0}"
            ".c{max-width:720px;margin:30px auto;background:#fff;border-radius:18px;overflow:hidden;box-shadow:0 6px 32px rgba(0,0,0,.12)}"
            ".hd{background:linear-gradient(135deg,#0ea5e9,#7C3AED);color:#fff;padding:30px 36px}"
            ".hd h1{margin:0 0 6px;font-size:1.5rem}"
            ".hd p{margin:0;opacity:.9;font-size:.88rem;line-height:1.5}"
            ".bd{padding:28px 36px}"
            ".sg{display:flex;gap:12px;margin:20px 0 26px}"
            ".sb{flex:1;background:#f8f9fc;border-radius:12px;padding:16px 10px;text-align:center;border:1.5px solid #e5e7eb}"
            ".sn{font-size:1.9rem;font-weight:900;line-height:1}"
            ".sl{font-size:.7rem;color:#6b7280;margin-top:5px;line-height:1.3;text-transform:uppercase;letter-spacing:.04em}"
            ".bge{display:inline-block;font-size:.85rem;font-weight:800;padding:6px 14px;border-radius:8px;margin:24px 0 10px}"
            "table{width:100%;border-collapse:collapse;font-size:.86rem;margin-bottom:6px}"
            "th{background:#7C3AED;color:#fff;padding:9px 12px;text-align:left;font-size:.75rem;text-transform:uppercase;letter-spacing:.06em}"
            ".dv{height:1px;background:#e5e7eb;margin:24px 0}"
            ".ft{padding:18px 36px;text-align:center;font-size:.75rem;color:#9ca3af;border-top:1px solid #e5e7eb}"
        )

        html_body = (
            f"<!DOCTYPE html><html><head><meta charset=\\'utf-8\\'><style>{CSS}</style></head>"
            f"<body><div class=\\'c\\'>"
            f"<div class=\\'hd\\'><h1>&#9200; Auto Report &mdash; {LEAD_MINUTES} Min Before Deadline</h1>"
            f"<p>EduMentor AI &nbsp;|&nbsp; <strong>{year_label}</strong> &nbsp;|&nbsp; Topic: <strong>{topic}</strong> &nbsp;|&nbsp; Deadline: {deadline_label} &nbsp;|&nbsp; {today_str}</p></div>"
            f"<div class=\\'bd\\'><p style=\\'color:#374151;margin-top:0\\'>Dear Mentor,</p>"
            f"{pre_banner}{alert}"
            f"<div class=\\'sg\\'>"
            f"<div class=\\'sb\\'><div class=\\'sn\' style=\\'color:#7C3AED\\'>{total}</div><div class=\\'sl\\'>Total<br>Students</div></div>"
            f"<div class=\\'sb\\'><div class=\\'sn\' style=\\'color:{weak_color}\\'>{weak_pct}%</div><div class=\\'sl\\'>Overall Weak %<br><span style=\\'font-size:.65rem\\'>({weak_count}/{total})</span></div></div>"
            f"<div class=\\'sb\\'><div class=\\'sn\' style=\\'color:{boring_color}\\'>{boring_pct}%</div><div class=\\'sl\\'>Class Boring %<br><span style=\\'font-size:.65rem\\'>({boring_count}/{total})</span></div></div>"
            f"<div class=\\'sb\\'><div class=\\'sn\' style=\\'color:#F59E0B\\'>{missed_count}</div><div class=\\'sl\\'>Yet to<br>Submit</div></div></div>"
            f"<div class=\\'bge\' style=\\'background:#eff6ff;color:#1d4ed8\\'>&#128203; All Students &mdash; Marks ({total})</div>"
            f"<table><thead><tr><th>Student Name</th><th>Register No.</th><th>Score</th><th style=\\'text-align:center\\'>%</th><th>Status</th></tr></thead>"
            f"<tbody>{all_rows}</tbody></table>"
            f"<div class=\\'dv\\'></div>"
            f"<div class=\\'bge\' style=\\'background:#fdf4ff;color:#7e22ce\\'>&#10060; Did Not Understand ({len(not_understood_list)})</div>"
            f"<table><thead><tr><th>Student Name</th><th>Register No.</th><th>Email</th><th>Score / Status</th></tr></thead>"
            f"<tbody>{nu_rows}</tbody></table>"
            f"<div class=\\'dv\\'></div>"
            f"<div class=\\'bge\' style=\\'background:#fef2f2;color:#b91c1c\\'>&#9888; Weak Students &mdash; Score &lt; 50% ({len(weak_list)})</div>"
            f"<table><thead><tr><th>Student Name</th><th>Register No.</th><th>Email</th><th>Score</th></tr></thead>"
            f"<tbody>{wk_rows}</tbody></table>"
            f"<div class=\\'dv\\'></div>"
            f"<div class=\\'bge\' style=\\'background:#fffbeb;color:#92400e\\'>&#128564; Found Class Boring &mdash; {boring_pct}% ({boring_count}/{total})</div>"
            f"<table><thead><tr><th>Student Name</th><th>Register No.</th><th>Email</th></tr></thead>"
            f"<tbody>{br_rows}</tbody></table>"
            f"<div class=\\'dv\\'></div>"
            "<p style=\\'font-size:.82rem;color:#6b7280;margin-top:12px\\'>"
            "&#128161; Log in to your <strong>EduMentor AI dashboard</strong> to view individual quiz answers. "
            "Students marked <em>Missed</em> still have ~1 minute to submit.</p>"
            "</div>"
            f"<div class=\\'ft\\'>Auto-generated by EduMentor AI Scheduler &middot; {year_label} &middot; Topic: {topic} &middot; {today_str}</div>"
            "</div></body></html>"
        )

        mentors = db.query(Mentor).all()
        subject_line = (
            f"[EduMentor AI] Auto Report - {year_label} | "
            f"Weak: {weak_pct}% | Boring: {boring_pct}% | Missed: {missed_count} | "
            f"{topic} (Deadline in {LEAD_MINUTES} min)"
        )
        sent_count = 0
        for mentor in mentors:
            mentor_email = mentor.identity
            sent = False
            if settings.RESEND_API_KEY:
                try:
                    req_payload = _json.dumps({
                        "from": settings.RESEND_FROM_EMAIL,
                        "to": [mentor_email],
                        "subject": subject_line,
                        "html": html_body,
                    }).encode()
                    req = urllib.request.Request(
                        "https://api.resend.com/emails", data=req_payload,
                        headers={"Authorization": f"Bearer {settings.RESEND_API_KEY}", "Content-Type": "application/json"},
                    )
                    with urllib.request.urlopen(req, timeout=10) as resp:
                        if resp.status in (200, 201):
                            sent = True
                            sent_count += 1
                except Exception as e:
                    logger.warning(f"[Scheduler] Resend failed for {mentor_email}: {e}")
            if not sent and settings.SMTP_USER and settings.SMTP_PASS:
                try:
                    msg = MIMEMultipart("alternative")
                    msg["Subject"] = subject_line
                    msg["From"]    = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_USER}>"
                    msg["To"]      = mentor_email
                    msg.attach(MIMEText(html_body, "html"))
                    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                        server.starttls()
                        server.login(settings.SMTP_USER, settings.SMTP_PASS)
                        server.sendmail(settings.SMTP_USER, [mentor_email], msg.as_string())
                    sent_count += 1
                except Exception as e:
                    logger.error(f"[Scheduler] SMTP failed for {mentor_email}: {e}")

        logger.info(
            f"[Scheduler] Pre-deadline report sent for year={year} topic=\'{topic}\' "
            f"to {sent_count}/{len(mentors)} mentor(s). "
            f"weak={weak_pct}% boring={boring_pct}% missed={missed_count}"
        )
    except Exception as exc:
        logger.error(f"[Scheduler] Error in _build_and_send_report: {exc}", exc_info=True)
    finally:
        db.close()


def check_deadlines():
    """Poll all DailyTopic records. Fire report 1-1.5 min before deadline (once per key)."""
    now = datetime.datetime.now()
    today_str = now.date().isoformat()
    db = SessionLocal()
    try:
        topics = (
            db.query(DailyTopic)
            .filter(DailyTopic.due_time != None, DailyTopic.due_time != "")
            .all()
        )
        for rec in topics:
            due_time = rec.due_time
            due_date = rec.due_date or today_str
            try:
                h, m = map(int, due_time.split(":"))
                dy, dm, dd = map(int, due_date.split("-"))
                due_dt = now.replace(year=dy, month=dm, day=dd, hour=h, minute=m, second=0, microsecond=0)
            except Exception:
                continue
            delta_minutes = (due_dt - now).total_seconds() / 60.0
            if 1.0 <= delta_minutes <= 1.5:
                key = (rec.year, rec.topic, due_date, due_time)
                if key not in _sent_reports:
                    _sent_reports.add(key)
                    logger.info(
                        f"[Scheduler] Firing pre-deadline report: "
                        f"year={rec.year} topic=\'{rec.topic}\' deadline={due_date} {due_time}"
                    )
                    _build_and_send_report(rec.year, rec.topic, today_str, due_time)
    except Exception as exc:
        logger.error(f"[Scheduler] check_deadlines error: {exc}", exc_info=True)
    finally:
        db.close()


def start_scheduler() -> BackgroundScheduler:
    """Create and start the APScheduler. Call once from FastAPI startup event."""
    scheduler = BackgroundScheduler(
        job_defaults={"misfire_grace_time": 60, "coalesce": True},
        timezone="Asia/Kolkata",
    )
    scheduler.add_job(
        check_deadlines,
        trigger="interval",
        seconds=30,
        id="deadline_checker",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("[Scheduler] Background deadline checker started (every 30s, IST).")
    return scheduler
''')

dest = os.path.join(os.path.dirname(__file__), 'scheduler.py')
with open(dest, 'w', encoding='utf-8') as f:
    f.write(content)
print('Written to:', dest)
