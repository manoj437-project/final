"""
EduMentor AI — Professional Email Service
==========================================
Priority:  1) Resend API  →  2) Gmail SMTP fallback
Threading: All sends run in background thread (non-blocking)
Logging:   Clear [Email] prefix for easy grep in logs
"""

import smtplib
import threading
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import resend

from app.config import settings


# ─────────────────────────────────────────────────────────────────────────────
# CORE DISPATCHER
# ─────────────────────────────────────────────────────────────────────────────

def send_email(to_email: str, subject: str, html_body: str) -> None:
    """
    Non-blocking email sender.
    Fires a background thread → Resend first, Gmail SMTP fallback.
    Returns immediately; never raises.
    """
    thread = threading.Thread(
        target=_send_with_fallback,
        args=(to_email, subject, html_body),
        daemon=True,
    )
    thread.start()


def _send_with_fallback(to_email: str, subject: str, html_body: str) -> None:
    """Internal: tries Resend, then falls back to Gmail SMTP."""
    if _try_resend(to_email, subject, html_body):
        return
    print(f"[Email] WARNING: Resend failed -> trying Gmail SMTP for: {to_email}")
    if _try_smtp(to_email, subject, html_body):
        return
    print(f"[Email] FAILED: Both Resend and SMTP failed for: {to_email}")


def _try_resend(to_email: str, subject: str, html_body: str) -> bool:
    """Attempt delivery via Resend API. Returns True on success."""
    if not settings.RESEND_API_KEY:
        print("[Email] WARNING: RESEND_API_KEY not set -- skipping Resend.")
        return False
    try:
        resend.api_key = settings.RESEND_API_KEY
        params: resend.Emails.SendParams = {
            "from": settings.RESEND_FROM_EMAIL,
            "to": [to_email],
            "subject": subject,
            "html": html_body,
        }
        result = resend.Emails.send(params)
        if result and result.get("id"):
            print(f"[Email] >> Sent via Resend  ->  {to_email}  |  id: {result['id']}")
            return True
        print(f"[Email] WARNING: Resend returned no id for: {to_email}")
        return False
    except Exception as exc:
        print(f"[Email] WARNING: Resend error for {to_email}: {exc}")
        return False


def _try_smtp(to_email: str, subject: str, html_body: str) -> bool:
    """Attempt delivery via Gmail SMTP. Returns True on success."""
    if not settings.SMTP_USER or not settings.SMTP_PASS:
        print("[Email] WARNING: SMTP_USER / SMTP_PASS not set -- skipping SMTP fallback.")
        return False
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_USER}>"
        msg["To"] = to_email
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=15) as server:
            server.ehlo()
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASS)
            server.sendmail(settings.SMTP_USER, to_email, msg.as_string())

        print(f"[Email] >> Sent via Gmail SMTP  ->  {to_email}")
        return True
    except Exception as exc:
        print(f"[Email] FAILED: SMTP error for {to_email}: {exc}")
        return False


# ─────────────────────────────────────────────────────────────────────────────
# HTML BASE TEMPLATE HELPER
# ─────────────────────────────────────────────────────────────────────────────

def _wrap_template(content_html: str) -> str:
    """Wraps content in the EduMentor AI base email shell (dark theme, mobile-friendly)."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>EduMentor AI</title>
</head>
<body style="margin:0;padding:0;background-color:#0a0f1e;font-family:'Segoe UI',Helvetica,Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#0a0f1e;padding:40px 20px;">
    <tr>
      <td align="center">
        <table width="560" cellpadding="0" cellspacing="0" style="max-width:560px;width:100%;">

          <!-- ── Logo Header ── -->
          <tr>
            <td align="center" style="padding-bottom:32px;">
              <div style="display:inline-block;background:linear-gradient(135deg,#6366f1,#8b5cf6);border-radius:16px;padding:14px 28px;">
                <span style="font-size:22px;font-weight:700;color:#ffffff;letter-spacing:1px;">🎓 EduMentor AI</span>
              </div>
            </td>
          </tr>

          <!-- ── Card ── -->
          <tr>
            <td style="background:linear-gradient(145deg,#141929,#1e2640);border-radius:24px;padding:48px 40px;border:1px solid rgba(99,102,241,0.25);box-shadow:0 20px 60px rgba(0,0,0,0.5);">
              {content_html}
            </td>
          </tr>

          <!-- ── Footer ── -->
          <tr>
            <td align="center" style="padding-top:28px;">
              <p style="margin:0;font-size:12px;color:#334155;">
                Powered by <strong style="color:#6366f1;">EduMentor AI</strong> · AI-Powered Education Platform
              </p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""


# ─────────────────────────────────────────────────────────────────────────────
# EMAIL TEMPLATES
# ─────────────────────────────────────────────────────────────────────────────

def send_welcome_email(to_email: str, user_name: str) -> None:
    """Sends a welcome email to a newly registered student."""
    content = f"""
      <p style="margin:0 0 8px;font-size:14px;color:#94a3b8;text-transform:uppercase;letter-spacing:1px;">Welcome aboard 🎉</p>
      <h1 style="margin:0 0 24px;font-size:26px;font-weight:700;color:#f1f5f9;">You're in, {user_name}!</h1>
      <p style="margin:0 0 32px;font-size:15px;line-height:1.7;color:#94a3b8;">
        Hi <strong style="color:#e2e8f0;">{user_name}</strong>,<br/>
        Welcome to <strong style="color:#a78bfa;">EduMentor AI</strong> — your AI-powered academic companion.
        Your student account is now active and ready to use.
      </p>

      <!-- Feature highlights -->
      <div style="background:rgba(99,102,241,0.08);border:1px solid rgba(99,102,241,0.2);border-radius:16px;padding:24px 28px;margin-bottom:32px;">
        <p style="margin:0 0 16px;font-size:14px;font-weight:600;color:#e2e8f0;">What you can do with EduMentor AI:</p>
        <table width="100%" cellpadding="0" cellspacing="0">
          <tr>
            <td style="padding:6px 0;font-size:14px;color:#94a3b8;">🤖 &nbsp;Chat with your AI Tutor for instant help</td>
          </tr>
          <tr>
            <td style="padding:6px 0;font-size:14px;color:#94a3b8;">📊 &nbsp;Track your quiz scores and progress</td>
          </tr>
          <tr>
            <td style="padding:6px 0;font-size:14px;color:#94a3b8;">📅 &nbsp;View your weekly timetable</td>
          </tr>
          <tr>
            <td style="padding:6px 0;font-size:14px;color:#94a3b8;">🎯 &nbsp;Get personalized study recommendations</td>
          </tr>
        </table>
      </div>

      <!-- CTA Button -->
      <div style="text-align:center;margin-bottom:32px;">
        <a href="#" style="display:inline-block;background:linear-gradient(135deg,#6366f1,#8b5cf6);color:#ffffff;font-size:15px;font-weight:600;padding:14px 36px;border-radius:12px;text-decoration:none;letter-spacing:0.5px;">
          Start Learning Now →
        </a>
      </div>

      <hr style="border:none;border-top:1px solid rgba(99,102,241,0.2);margin:0 0 24px;" />
      <p style="margin:0;font-size:12px;color:#475569;text-align:center;line-height:1.7;">
        This email was sent to <strong style="color:#64748b;">{to_email}</strong> because you registered on EduMentor AI.<br/>
        &copy; 2026 EduMentor AI. All rights reserved.
      </p>
    """
    send_email(
        to_email=to_email,
        subject="🎓 Welcome to EduMentor AI — Your account is ready!",
        html_body=_wrap_template(content),
    )


def send_otp_email(to_email: str, user_name: str, otp_code: str, role: str = "student") -> None:
    """Sends a password-reset OTP email. OTP is valid for 10 minutes."""
    role_label = "Student" if role == "student" else "Mentor"
    content = f"""
      <p style="margin:0 0 8px;font-size:14px;color:#94a3b8;text-transform:uppercase;letter-spacing:1px;">{role_label} Account</p>
      <h1 style="margin:0 0 24px;font-size:26px;font-weight:700;color:#f1f5f9;">Password Reset Request</h1>
      <p style="margin:0 0 32px;font-size:15px;line-height:1.7;color:#94a3b8;">
        Hi <strong style="color:#e2e8f0;">{user_name}</strong>,<br/>
        We received a request to reset your EduMentor AI password.
        Use the OTP below to proceed. This code is valid for
        <strong style="color:#a78bfa;">10 minutes</strong>.
      </p>

      <!-- OTP Box -->
      <div style="background:linear-gradient(135deg,rgba(99,102,241,0.15),rgba(139,92,246,0.15));border:2px solid rgba(99,102,241,0.4);border-radius:16px;padding:32px;text-align:center;margin-bottom:32px;">
        <p style="margin:0 0 12px;font-size:12px;color:#94a3b8;text-transform:uppercase;letter-spacing:2px;">Your One-Time Password</p>
        <div style="font-size:48px;font-weight:800;letter-spacing:14px;color:#a78bfa;font-family:'Courier New',monospace;">{otp_code}</div>
        <p style="margin:14px 0 0;font-size:12px;color:#64748b;">⏳ Expires in 10 minutes</p>
      </div>

      <!-- Security Warning -->
      <div style="background:rgba(239,68,68,0.08);border-left:4px solid #ef4444;border-radius:8px;padding:16px 20px;margin-bottom:32px;">
        <p style="margin:0;font-size:13px;color:#fca5a5;line-height:1.6;">
          🔒 <strong>Never share this OTP</strong> with anyone, including EduMentor support staff.
          If you didn't request a password reset, please ignore this email — your account is safe.
        </p>
      </div>

      <!-- Steps -->
      <p style="margin:0 0 12px;font-size:14px;font-weight:600;color:#e2e8f0;">How to use this OTP:</p>
      <ol style="margin:0 0 32px;padding-left:20px;color:#94a3b8;font-size:14px;line-height:2;">
        <li>Go back to the EduMentor AI reset password page</li>
        <li>Enter your email and the OTP above</li>
        <li>Set your new password</li>
      </ol>

      <hr style="border:none;border-top:1px solid rgba(99,102,241,0.2);margin:0 0 24px;" />
      <p style="margin:0;font-size:12px;color:#475569;text-align:center;line-height:1.7;">
        This email was sent to <strong style="color:#64748b;">{to_email}</strong>
        because a password reset was requested for your EduMentor AI account.<br/>
        &copy; 2026 EduMentor AI. All rights reserved.
      </p>
    """
    send_email(
        to_email=to_email,
        subject=f"🔐 Your EduMentor AI OTP: {otp_code}",
        html_body=_wrap_template(content),
    )


def send_approval_email(to_email: str, user_name: str) -> None:
    """Sends an approval notification email (e.g. mentor approves student action)."""
    content = f"""
      <p style="margin:0 0 8px;font-size:14px;color:#94a3b8;text-transform:uppercase;letter-spacing:1px;">Account Update ✅</p>
      <h1 style="margin:0 0 24px;font-size:26px;font-weight:700;color:#f1f5f9;">You've Been Approved!</h1>
      <p style="margin:0 0 32px;font-size:15px;line-height:1.7;color:#94a3b8;">
        Hi <strong style="color:#e2e8f0;">{user_name}</strong>,<br/>
        Great news! Your request has been <strong style="color:#34d399;">approved</strong> by your mentor on EduMentor AI.
        You now have full access to continue your learning journey.
      </p>

      <!-- Success badge -->
      <div style="background:rgba(52,211,153,0.08);border:1px solid rgba(52,211,153,0.3);border-radius:16px;padding:24px;text-align:center;margin-bottom:32px;">
        <div style="font-size:48px;margin-bottom:12px;">✅</div>
        <p style="margin:0;font-size:16px;font-weight:600;color:#34d399;">Request Approved</p>
        <p style="margin:8px 0 0;font-size:13px;color:#6ee7b7;">Your mentor has reviewed and approved your request.</p>
      </div>

      <!-- CTA -->
      <div style="text-align:center;margin-bottom:32px;">
        <a href="#" style="display:inline-block;background:linear-gradient(135deg,#6366f1,#8b5cf6);color:#ffffff;font-size:15px;font-weight:600;padding:14px 36px;border-radius:12px;text-decoration:none;">
          Continue Learning →
        </a>
      </div>

      <hr style="border:none;border-top:1px solid rgba(99,102,241,0.2);margin:0 0 24px;" />
      <p style="margin:0;font-size:12px;color:#475569;text-align:center;line-height:1.7;">
        This email was sent to <strong style="color:#64748b;">{to_email}</strong>.<br/>
        &copy; 2026 EduMentor AI. All rights reserved.
      </p>
    """
    send_email(
        to_email=to_email,
        subject="✅ Your EduMentor AI request has been approved",
        html_body=_wrap_template(content),
    )


def send_rejection_email(to_email: str, user_name: str, reason: str = "") -> None:
    """Sends a rejection notification email with optional reason."""
    reason_block = ""
    if reason:
        reason_block = f"""
      <div style="background:rgba(239,68,68,0.08);border-left:4px solid #ef4444;border-radius:8px;padding:16px 20px;margin-bottom:32px;">
        <p style="margin:0 0 6px;font-size:12px;color:#94a3b8;text-transform:uppercase;letter-spacing:1px;">Reason provided:</p>
        <p style="margin:0;font-size:14px;color:#fca5a5;line-height:1.6;">{reason}</p>
      </div>
        """

    content = f"""
      <p style="margin:0 0 8px;font-size:14px;color:#94a3b8;text-transform:uppercase;letter-spacing:1px;">Account Update</p>
      <h1 style="margin:0 0 24px;font-size:26px;font-weight:700;color:#f1f5f9;">Request Not Approved</h1>
      <p style="margin:0 0 32px;font-size:15px;line-height:1.7;color:#94a3b8;">
        Hi <strong style="color:#e2e8f0;">{user_name}</strong>,<br/>
        We're sorry to inform you that your request on EduMentor AI has <strong style="color:#f87171;">not been approved</strong>
        at this time. Please reach out to your mentor for more information.
      </p>

      <!-- Rejected badge -->
      <div style="background:rgba(239,68,68,0.08);border:1px solid rgba(239,68,68,0.25);border-radius:16px;padding:24px;text-align:center;margin-bottom:32px;">
        <div style="font-size:48px;margin-bottom:12px;">❌</div>
        <p style="margin:0;font-size:16px;font-weight:600;color:#f87171;">Request Rejected</p>
        <p style="margin:8px 0 0;font-size:13px;color:#fca5a5;">Please contact your mentor for clarification.</p>
      </div>

      {reason_block}

      <!-- Support CTA -->
      <p style="margin:0 0 32px;font-size:14px;color:#94a3b8;text-align:center;">
        If you believe this is a mistake, please contact your mentor or class coordinator directly.
      </p>

      <hr style="border:none;border-top:1px solid rgba(99,102,241,0.2);margin:0 0 24px;" />
      <p style="margin:0;font-size:12px;color:#475569;text-align:center;line-height:1.7;">
        This email was sent to <strong style="color:#64748b;">{to_email}</strong>.<br/>
        &copy; 2026 EduMentor AI. All rights reserved.
      </p>
    """
    send_email(
        to_email=to_email,
        subject="❌ Update on your EduMentor AI request",
        html_body=_wrap_template(content),
    )
