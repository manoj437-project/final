"""
EduMentor AI - Background Scheduler
Runs every 30s, sends full session report to the ASSIGNING MENTOR ONLY
in the last 10 seconds (0-40s window) before the quiz deadline expires.
Includes:
  - All students marks table (Missed = no submission today, never uses old scores)
  - Weak students list (score < 50%)
  - Not-understanding students list
  - Quiz not-attending (missed) students list
  - Mentor reteach suggestion if needed
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
from app.models import DailyTopic, Student, StudentScore, BoringReport, Mentor, TopicHistory
from app.config import settings

logger = logging.getLogger(__name__)

# Dedup set - (year, topic, due_date, due_time)
_sent_reports: set = set()

# Fire when deadline is within the last 10 seconds.
# Window is 0-40s (0.0-0.667 min) so the 10s mark is reliably caught
# within a 30-second polling cycle -- otherwise a narrow 10s window
# could be skipped entirely between two consecutive 30s polls.
LEAD_MIN_LOW  = 0.0          # 0 seconds  (fire right up to deadline)
LEAD_MIN_HIGH = 40 / 60      # ~40 seconds (guarantees capture within 30s poll)
LEAD_SECONDS  = 10           # label used in the email subject & body
LEAD_MINUTES  = LEAD_SECONDS / 60   # kept for any legacy references


def _build_and_send_report(year: str, topic: str, today_str: str, deadline_label: str):
    """Build the full HTML session report and email ONLY to the mentor who assigned this quiz."""
    db = SessionLocal()
    try:
        YEAR_FULL = {"1": "1st Year", "2": "2nd Year", "3": "3rd Year"}
        year_label = YEAR_FULL.get(year, f"Year {year}")

        # -- Find ONLY the mentor who assigned this quiz ----------------------
        latest_history = (
            db.query(TopicHistory)
            .filter(TopicHistory.year == year, TopicHistory.topic == topic)
            .order_by(TopicHistory.created_at.desc())
            .first()
        )
        activating_mentor_name = latest_history.set_by if latest_history else None
        target_mentor = None
        if activating_mentor_name:
            target_mentor = db.query(Mentor).filter(Mentor.name == activating_mentor_name).first()

        if not target_mentor:
            logger.warning(
                f"[Scheduler] Cannot find assigning mentor '{activating_mentor_name}' "
                f"for year={year} topic='{topic}' -- skipping email."
            )
            return

        all_students = (
            db.query(Student)
            .filter(Student.year == year)
            .order_by(Student.username.asc())
            .all()
        )
        total = len(all_students)
        if total == 0:
            logger.info(f"[Scheduler] No students for year {year} - skipping.")
            return

        not_understood_list, weak_list, good_list, all_students_data = [], [], [], []

        # Get activation time to exclude old scores from previous runs of the same topic
        daily_rec = db.query(DailyTopic).filter(DailyTopic.year == year).first()
        activation_time = daily_rec.updated_at if (daily_rec and daily_rec.updated_at) else None

        for s in all_students:
            # ONLY look at today's score for this specific topic, submitted AFTER current activation.
            # This ensures re-activated quizzes don't pick up scores from previous sessions.
            score_q = (
                db.query(StudentScore)
                .filter(
                    StudentScore.student_id == s.id,
                    StudentScore.topic == topic,
                    StudentScore.date == today_str,
                )
            )
            if activation_time:
                score_q = score_q.filter(StudentScore.created_at >= activation_time)
            score_rec = score_q.order_by(StudentScore.created_at.desc()).first()

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
                # No submission for this quiz session -> Missed
                all_students_data.append({
                    "name": s.username, "regno": s.regno,
                    "score": None, "percentage": None, "status": "missed"
                })

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

        # Build not-attending list
        not_attending_list = [
            {"name": sd["name"], "regno": sd["regno"]}
            for sd in all_students_data if sd["status"] == "missed"
        ]

        weak_color   = "#EF4444" if weak_pct > 50 else "#F59E0B" if weak_pct > 25 else "#10B981"
        boring_color = "#F59E0B" if boring_pct > 30 else "#6B7280"

        # Banners
        pre_banner = (
            "<div style='background:#f0f9ff;border:2px solid #7dd3fc;border-radius:12px;padding:14px 20px;margin-bottom:24px;'>"
            f"<strong style='color:#0369a1'>&#9200; Auto Report &mdash; Final {LEAD_SECONDS} Seconds Before Deadline:</strong> "
            f"This report was automatically generated in the <strong>last {LEAD_SECONDS} seconds</strong> "
            f"before the quiz on <strong>&quot;{topic}&quot;</strong> expires. "
            "Students who have not submitted will show as <em>Quiz Not Attending</em>."
            "</div>"
        )

        # Determine reteach recommendation
        reteach_needed = (weak_pct > 50) or (len(not_understood_list) >= max(1, total // 3))

        alert = ""
        if reteach_needed:
            reteach_reasons = []
            if weak_pct > 50:
                reteach_reasons.append(f"{weak_pct}% of students scored below 50%")
            if len(not_understood_list) >= max(1, total // 3):
                reteach_reasons.append(f"{len(not_understood_list)} student(s) reported not understanding the topic")
            reasons_str = " and ".join(reteach_reasons)
            alert = (
                "<div style='background:#fef2f2;border:2px solid #fca5a5;border-radius:12px;padding:16px 20px;margin-bottom:24px;'>"
                f"<strong style='color:#EF4444'>&#9888; ACTION REQUIRED &mdash; Re-Teaching Recommended:</strong><br>"
                f"Reason: {reasons_str}.<br><br>"
                f"<strong>Suggested Actions for &quot;{topic}&quot;:</strong>"
                "<ul style='margin:8px 0;padding-left:18px'>"
                "<li>Schedule a re-teaching session on this topic before the next assessment</li>"
                "<li>Provide additional study materials and practice problems</li>"
                "<li>Hold a dedicated doubt-clearing session for struggling students</li>"
                "<li>Consider breaking the topic into smaller sub-topics for better comprehension</li>"
                "</ul>"
                "</div>"
            )
        elif boring_pct > 30:
            alert = (
                "<div style='background:#fffbeb;border:2px solid #fcd34d;border-radius:12px;padding:16px 20px;margin-bottom:24px;'>"
                f"<strong style='color:#D97706'>&#128564; Engagement Alert:</strong> {boring_pct}% of students found the class boring. "
                "Consider varying your teaching approach."
                "</div>"
            )

        # Marks table rows
        ST = {
            "good":           ("&#9989; Good",            "#dcfce7", "#16a34a"),
            "weak":           ("&#9888; Weak",            "#fff3f3", "#EF4444"),
            "not_understood": ("&#10060; Not Understood", "#fdf4ff", "#9333ea"),
            "missed":         ("&#128308; Missed",        "#fff7ed", "#c2410c"),
        }
        all_rows = ""
        for sd in all_students_data:
            lbl, rbg, tc = ST.get(sd["status"], ("&mdash;", "#fff", "#111"))
            ps = f"{sd['percentage']}%" if sd["percentage"] is not None else "&mdash;"
            ss = sd.get("score") or "&mdash;"
            all_rows += (
                f"<tr style='background:{rbg}'>"
                f"<td style='padding:9px 12px;border-bottom:1px solid #e5e7eb'>{sd['name']}</td>"
                f"<td style='padding:9px 12px;border-bottom:1px solid #e5e7eb;font-family:monospace;font-size:.82rem'>{sd['regno']}</td>"
                f"<td style='padding:9px 12px;border-bottom:1px solid #e5e7eb;font-weight:700'>{ss}</td>"
                f"<td style='padding:9px 12px;border-bottom:1px solid #e5e7eb;text-align:center;font-weight:800;color:{tc}'>{ps}</td>"
                f"<td style='padding:9px 12px;border-bottom:1px solid #e5e7eb;font-weight:700;color:{tc}'>{lbl}</td></tr>"
            )

        # Not-understood rows
        nu_rows = "".join(
            f"<tr style='background:#fdf4ff'>"
            f"<td style='padding:9px 12px;border-bottom:1px solid #e5e7eb'>{s['name']}</td>"
            f"<td style='padding:9px 12px;border-bottom:1px solid #e5e7eb;font-family:monospace'>{s['regno']}</td>"
            f"<td style='padding:9px 12px;border-bottom:1px solid #e5e7eb'>{s['email']}</td>"
            f"<td style='padding:9px 12px;border-bottom:1px solid #e5e7eb;color:#9333ea;font-weight:700'>&#10060; {s['score']} ({s['percentage']}%)</td></tr>"
            for s in not_understood_list
        ) if not_understood_list else "<tr><td colspan='4' style='padding:12px;text-align:center;color:#6b7280'>No students reported not understanding &#127881;</td></tr>"

        # Weak rows
        wk_rows = "".join(
            f"<tr style='background:#fff3f3'>"
            f"<td style='padding:9px 12px;border-bottom:1px solid #e5e7eb'>{w['name']}</td>"
            f"<td style='padding:9px 12px;border-bottom:1px solid #e5e7eb;font-family:monospace'>{w['regno']}</td>"
            f"<td style='padding:9px 12px;border-bottom:1px solid #e5e7eb'>{w['email']}</td>"
            f"<td style='padding:9px 12px;border-bottom:1px solid #e5e7eb;color:#EF4444;font-weight:700'>&#9888; {w['score']} ({w['percentage']}%)</td></tr>"
            for w in weak_list
        ) if weak_list else "<tr><td colspan='4' style='padding:12px;text-align:center;color:#6b7280'>No low-score students &#127881;</td></tr>"

        # Quiz not-attending rows
        na_rows = "".join(
            f"<tr style='background:#fff7ed'>"
            f"<td style='padding:9px 12px;border-bottom:1px solid #e5e7eb'>{na['name']}</td>"
            f"<td style='padding:9px 12px;border-bottom:1px solid #e5e7eb;font-family:monospace'>{na['regno']}</td>"
            f"<td style='padding:9px 12px;border-bottom:1px solid #e5e7eb;color:#c2410c;font-weight:700'>Did not attend the quiz</td></tr>"
            for na in not_attending_list
        ) if not_attending_list else "<tr><td colspan='3' style='padding:12px;text-align:center;color:#6b7280'>All students attended the quiz &#127881;</td></tr>"

        # Boring rows
        br_rows = "".join(
            f"<tr style='background:#fffbeb'>"
            f"<td style='padding:9px 12px;border-bottom:1px solid #e5e7eb'>{bs['name']}</td>"
            f"<td style='padding:9px 12px;border-bottom:1px solid #e5e7eb;font-family:monospace'>{bs['regno']}</td>"
            f"<td style='padding:9px 12px;border-bottom:1px solid #e5e7eb'>{bs['email']}</td></tr>"
            for bs in boring_students
        ) if boring_students else "<tr><td colspan='3' style='padding:12px;text-align:center;color:#6b7280'>No boring reports today &#128522;</td></tr>"

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
            f"<!DOCTYPE html><html><head><meta charset='utf-8'><style>{CSS}</style></head>"
            f"<body><div class='c'>"
            f"<div class='hd'><h1>&#9200; Auto Report &mdash; Final {LEAD_SECONDS}s Before Deadline</h1>"
            f"<p>EduMentor AI &nbsp;|&nbsp; <strong>{year_label}</strong> &nbsp;|&nbsp; Topic: <strong>{topic}</strong> &nbsp;|&nbsp; Deadline: {deadline_label} &nbsp;|&nbsp; {today_str}</p></div>"
            f"<div class='bd'><p style='color:#374151;margin-top:0'>Dear {target_mentor.name},</p>"
            f"{pre_banner}{alert}"
            f"<div class='sg'>"
            f"<div class='sb'><div class='sn' style='color:#7C3AED'>{total}</div><div class='sl'>Total<br>Students</div></div>"
            f"<div class='sb'><div class='sn' style='color:{weak_color}'>{weak_pct}%</div><div class='sl'>Overall Weak %<br><span style='font-size:.65rem'>({weak_count}/{total})</span></div></div>"
            f"<div class='sb'><div class='sn' style='color:#9333ea'>{len(not_understood_list)}</div><div class='sl'>Not<br>Understood</div></div>"
            f"<div class='sb'><div class='sn' style='color:#c2410c'>{missed_count}</div><div class='sl'>Quiz Not<br>Attending</div></div></div>"
            f"<div class='bge' style='background:#eff6ff;color:#1d4ed8'>&#128203; All Students &mdash; Marks ({total})</div>"
            f"<table><thead><tr><th>Student Name</th><th>Register No.</th><th>Score</th><th style='text-align:center'>%</th><th>Status</th></tr></thead>"
            f"<tbody>{all_rows}</tbody></table>"
            f"<div class='dv'></div>"
            f"<div class='bge' style='background:#fdf4ff;color:#7e22ce'>&#10060; Did Not Understand the Topic ({len(not_understood_list)})</div>"
            f"<table><thead><tr><th>Student Name</th><th>Register No.</th><th>Email</th><th>Score / Status</th></tr></thead>"
            f"<tbody>{nu_rows}</tbody></table>"
            f"<div class='dv'></div>"
            f"<div class='bge' style='background:#fef2f2;color:#b91c1c'>&#9888; Weak Students &mdash; Score &lt; 50% ({len(weak_list)})</div>"
            f"<table><thead><tr><th>Student Name</th><th>Register No.</th><th>Email</th><th>Score</th></tr></thead>"
            f"<tbody>{wk_rows}</tbody></table>"
            f"<div class='dv'></div>"
            f"<div class='bge' style='background:#fff7ed;color:#c2410c'>&#128308; Quiz Not Attending ({missed_count})</div>"
            f"<table><thead><tr><th>Student Name</th><th>Register No.</th><th>Note</th></tr></thead>"
            f"<tbody>{na_rows}</tbody></table>"
            f"<div class='dv'></div>"
            f"<div class='bge' style='background:#fffbeb;color:#92400e'>&#128564; Found Class Boring &mdash; {boring_pct}% ({boring_count}/{total})</div>"
            f"<table><thead><tr><th>Student Name</th><th>Register No.</th><th>Email</th></tr></thead>"
            f"<tbody>{br_rows}</tbody></table>"
            f"<div class='dv'></div>"
            "<p style='font-size:.82rem;color:#6b7280;margin-top:12px'>"
            "&#128161; Log in to your <strong>EduMentor AI dashboard</strong> to view individual quiz answers. "
            "Students in <em>Quiz Not Attending</em> did not submit before the deadline.</p>"
            "</div>"
            f"<div class='ft'>Auto-generated by EduMentor AI Scheduler &middot; {year_label} &middot; Topic: {topic} &middot; {today_str}</div>"
            "</div></body></html>"
        )

        mentor_email = target_mentor.identity
        subject_line = (
            f"[EduMentor AI] FINAL {LEAD_SECONDS}s Report - {year_label} | "
            f"Weak: {weak_pct}% | Not Understood: {len(not_understood_list)} | Not Attending: {missed_count} | "
            f"{topic} (Deadline NOW)"
        )
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
                sent = True
            except Exception as e:
                logger.error(f"[Scheduler] SMTP failed for {mentor_email}: {e}")

        logger.info(
            f"[Scheduler] Pre-deadline report {'sent' if sent else 'FAILED'} for year={year} topic='{topic}' "
            f"to mentor '{target_mentor.name}' <{mentor_email}>. "
            f"weak={weak_pct}% not_understood={len(not_understood_list)} not_attending={missed_count}"
        )
    except Exception as exc:
        logger.error(f"[Scheduler] Error in _build_and_send_report: {exc}", exc_info=True)
    finally:
        db.close()


def check_deadlines():
    """Poll all DailyTopic records. Fire report between LEAD_MIN_LOW and LEAD_MIN_HIGH min before deadline (once per key)."""
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
            if LEAD_MIN_LOW <= delta_minutes <= LEAD_MIN_HIGH:
                key = (rec.year, rec.topic, due_date, due_time)
                if key not in _sent_reports:
                    _sent_reports.add(key)
                    logger.info(
                        f"[Scheduler] Firing pre-deadline report: "
                        f"year={rec.year} topic='{rec.topic}' deadline={due_date} {due_time}"
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
