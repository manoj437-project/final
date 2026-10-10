import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://postgres:manoj@localhost:5432/edumentor"

    # JWT Authentication
    JWT_SECRET_KEY: str = "9a8b7c6d5e4f3g2h1i0j9k8l7m6n5o4p3q2r1s0t9u8v7w6x5y4z3210abcdef"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Google Gemini AI (for quiz generation & learning resources)
    GEMINI_API_KEY: str = ""

    # Resend Email Service (Primary)
    RESEND_API_KEY: str = ""
    RESEND_FROM_EMAIL: str = "EduMentor AI <noreply@edumentorai.in>"

    # Gmail SMTP (Fallback — used when Resend fails)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""                  # your Gmail address
    SMTP_PASS: str = ""                  # Gmail App Password (not login password)
    SMTP_FROM_NAME: str = "EduMentor AI"

    # Pydantic v2 settings configuration
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
