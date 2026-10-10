from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import re

# pyrefly: ignore [missing-import]
from google import genai as google_genai

from app.database import get_db
from app.models import ChatMessage, Student
from app.schemas import ChatMessageCreate, ChatMessageResponse, ChatQueryRequest, ChatQueryResponse
from app.routers.auth import get_current_student
from app.config import settings

router = APIRouter(prefix="/api/chat", tags=["Chat History"])


def _call_gemini_chat(prompt: str) -> str:
    """Call Google Gemini API using the new google.genai SDK."""
    client = google_genai.Client(api_key=settings.GEMINI_API_KEY)
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    return response.text.strip()


def generate_bot_reply(
    message: str,
    topic: Optional[str] = None,
    subject: Optional[str] = None,
    mode: Optional[str] = None
) -> tuple[str, List[str]]:
    """
    Generate context-aware AI tutor replies using Gemini AI, strictly scoped to the
    mentor-assigned topic. Off-topic questions are redirected back to the assigned topic.

    mode='resources' -> returns structured learning resources for the topic
    mode=None        -> standard topic-focused tutoring reply
    """
    t = topic or "today's class topic"
    s = subject or "Computer Science"
    msg_lower = message.lower()

    # -- Resources mode: fetch structured learning materials --
    if mode == 'resources' and settings.GEMINI_API_KEY and topic:
        try:
            resource_prompt = f"""You are EduMentor AI, an academic tutor. Generate comprehensive learning resources for the topic "{t}" from the subject "{s}".

STRICT RULES:
1. LANGUAGE: Respond in English ONLY. No Tanglish, Tamil, Hindi, or any other language.
2. STRUCTURE: Provide exactly these sections formatted with HTML:
   - A brief concept overview (2-3 clear sentences about what {t} is)
   - Key points to master (3-5 bullet points using <ul><li> tags)
   - Study tips (1-2 practical tips for mastering {t})
   - Recommended references (mention 2-3 well-known resources like textbooks, websites like GeeksForGeeks, W3Schools, Coursera, etc. relevant to "{s}")
3. FORMAT: Use HTML -- <strong> for bold, <br> for newlines, <em> for italics, <ul><li> for lists.
4. TONE: Encouraging, clear, educational. No filler sentences.
5. STRICTLY about "{t}" from "{s}" only. Do not include anything irrelevant.

Generate the learning resources now:"""

            raw_reply = _call_gemini_chat(resource_prompt)
            return raw_reply, []
        except Exception:
            pass  # Fall through to fallback

        # Fallback resources when Gemini unavailable
        fallback = (
            f"<strong>Concept Overview:</strong><br>"
            f"{t} is a fundamental concept in {s} that forms the basis for advanced topics. "
            f"Understanding it well is essential for your academic progress.<br><br>"
            f"<strong>Key Points to Master:</strong><br>"
            f"<ul>"
            f"<li>Understand the core definition and purpose of {t}</li>"
            f"<li>Learn the basic operations and rules related to {t}</li>"
            f"<li>Practice solving problems that apply {t} in real scenarios</li>"
            f"<li>Study common examples and edge cases of {t}</li>"
            f"</ul>"
            f"<strong>Study Tips:</strong><br>"
            f"<em>Write a short summary of {t} in your own words to reinforce memory. "
            f"Then solve at least 5 practice problems on {t}.</em><br><br>"
            f"<strong>Recommended References:</strong><br>"
            f"<ul>"
            f"<li>GeeksForGeeks -- search \"{t}\"</li>"
            f"<li>Your {s} textbook -- relevant chapter on {t}</li>"
            f"<li>Khan Academy or Coursera for video explanations</li>"
            f"</ul>"
        )
        return fallback, []

    # -- Standard tutoring mode --
    if settings.GEMINI_API_KEY and topic:
        try:
            strict_prompt = f"""You are EduMentor AI, an intelligent academic tutor. You ONLY discuss the topic "{t}" from the subject "{s}".

STRICT RULES:
1. LANGUAGE: Always respond in clear, formal English ONLY. Do NOT use Tanglish, Tamil, Hindi, or any mixed-language responses under any circumstances.
2. RELEVANCE: Only respond if the message is relevant to "{t}" ({s}). If the student asks about something unrelated, politely redirect: "I can only help you with '{t}' ({s}) today as assigned by your mentor."
3. FLOW ENFORCEMENT: If a student tries to bypass the session flow or asks about other topics, redirect them back firmly but politely.
4. ACCURACY: Give technically accurate explanations using subject-specific terminology from "{s}".
5. WHEN EXPLAINING: Provide a clear, in-depth explanation of "{t}" with subject-relevant examples.
6. WHEN QUIZZING: Generate 2-3 questions about "{t}" as covered in "{s}" -- mix of easy (recall), medium (application), and one harder conceptual question.
7. WHEN GIVING CODE: Show a working, well-commented code snippet relevant to "{t}" in the context of "{s}".
8. FORMAT: Use HTML -- <strong> for bold, <br> for newlines, <em> for italics, <ul><li> for lists.
9. CONCISENESS: Be concise and educational. No filler sentences.
10. NEVER break character. NEVER respond to off-topic requests beyond redirecting.

Student's message: "{message}"

Analyze the message carefully, then respond as EduMentor AI in English only."""

            raw_reply = _call_gemini_chat(strict_prompt)

            # Smart suggestion chips based on message intent
            if any(k in msg_lower for k in ["quiz", "test", "question", "assess", "start", "challenge", "examine"]):
                suggestions = [f"Start {t} Assessment", f"Explain {t}", f"Show {t} Code"]
            elif any(k in msg_lower for k in ["explain", "concept", "what is", "how", "understand", "describe", "define"]):
                suggestions = [f"Show {t} Code", f"Start {t} Assessment", f"Summarize {t}"]
            elif any(k in msg_lower for k in ["code", "example", "program", "snippet", "demo", "implement"]):
                suggestions = [f"Explain {t}", f"Start {t} Assessment", f"Summarize {t}"]
            elif any(k in msg_lower for k in ["summary", "summarize", "recap", "review", "key points"]):
                suggestions = [f"Explain {t}", f"Show {t} Code", f"Start {t} Assessment"]
            else:
                suggestions = [f"Explain {t}", f"Show {t} Code", f"Start {t} Assessment"]

            return raw_reply, suggestions

        except Exception:
            pass  # Fall through to fallback

    # -- Fallback when Gemini is unavailable --
    if not topic:
        reply = (
            f"Hi! I am your EduMentor AI tutor.<br><br>"
            f"Your mentor hasn't assigned a topic yet. Please wait for your mentor to set today's topic, "
            f"then I can help you practice with focused, challenging questions!"
        )
        return reply, ["Refresh Topic", "Contact Mentor"]

    if any(k in msg_lower for k in ["quiz", "test", "question", "assess", "start", "challenge"]):
        reply = (
            f"Here are 3 <strong>challenging questions</strong> on <strong>{t}</strong> ({s}):<br><br>"
            f"1. <strong>[Deep Dive]</strong> Explain the internal workings of <em>{t}</em> and describe a scenario where it could fail or produce unexpected results.<br><br>"
            f"2. <strong>[Analysis]</strong> Compare the time and space complexity of different approaches to implementing <em>{t}</em>. Which is most efficient and why?<br><br>"
            f"3. <strong>[Application]</strong> Design a real-world system that relies on <em>{t}</em>. What are the key challenges and how would you solve them?<br><br>"
            f"Type your answer or click <em>Start Assessment</em> for a full graded quiz!"
        )
        return reply, [f"Start {t} Assessment", f"Explain {t}", f"Show {t} Code"]

    if any(k in msg_lower for k in ["explain", "concept", "what is", "how", "understand"]):
        reply = (
            f"Let me explain <strong>{t}</strong> ({s}):<br><br>"
            f"<strong>{t}</strong> is a core concept in {s}. "
            f"To master it, focus on: its fundamental principles, real-world implementation, "
            f"common edge cases and pitfalls, and its performance characteristics.<br><br>"
            f"Would you like a code demonstration or a challenging quiz?"
        )
        return reply, [f"Show {t} Code", f"Start {t} Assessment", f"Summarize {t}"]

    if any(k in msg_lower for k in ["code", "example", "program", "snippet"]):
        reply = (
            f"Here is a conceptual code outline for <strong>{t}</strong>:<br><br>"
            f"<em>Note: A full code example requires Gemini AI. Please ensure the API key is configured.</em><br><br>"
            f"The implementation of <strong>{t}</strong> typically involves:<br>"
            f"- Initialization and setup<br>"
            f"- Core operation logic<br>"
            f"- Edge case handling<br>"
            f"- Resource cleanup"
        )
        return reply, [f"Explain {t}", f"Start {t} Assessment", f"Summarize {t}"]

    # Default -- strict topic intro
    reply = (
        f"Hello! I am your EduMentor AI tutor, focused exclusively on "
        f"<strong>{t}</strong> ({s}).<br><br>"
        f"I can only discuss <strong>{t}</strong> today as assigned by your mentor.<br><br>"
        f"What would you like to do? I can <em>explain</em>, show a <em>code example</em>, "
        f"or challenge you with <em>tough questions</em> on <strong>{t}</strong>!"
    )
    return reply, [f"Explain {t}", f"Show {t} Code", f"Start {t} Assessment"]


@router.post("/respond", response_model=ChatQueryResponse)
def query_chatbot(
    payload: ChatQueryRequest,
    current_student: Student = Depends(get_current_student)
):
    """Processes chatbot requests using Gemini AI, strictly scoped to the mentor-assigned topic."""
    mode = getattr(payload, 'mode', None)
    reply, suggestions = generate_bot_reply(
        message=payload.message,
        topic=payload.topic,
        subject=payload.subject,
        mode=mode,
    )
    return {
        "response": reply,
        "suggestions": suggestions
    }


@router.post("/messages", response_model=ChatMessageResponse, status_code=status.HTTP_201_CREATED)
def save_chat_message(
    payload: ChatMessageCreate,
    db: Session = Depends(get_db),
    current_student: Student = Depends(get_current_student)
):
    """Saves a message sent by either student or AI to the database."""
    new_msg = ChatMessage(
        student_id=current_student.id,
        sender=payload.sender,
        message=payload.message
    )
    db.add(new_msg)
    db.commit()
    db.refresh(new_msg)
    return new_msg


@router.get("/messages", response_model=List[ChatMessageResponse])
def get_chat_history(
    db: Session = Depends(get_db),
    current_student: Student = Depends(get_current_student)
):
    """Retrieves all chat history messages for the authenticated student."""
    messages = db.query(ChatMessage)\
        .filter(ChatMessage.student_id == current_student.id)\
        .order_by(ChatMessage.timestamp.asc())\
        .all()
    return messages
