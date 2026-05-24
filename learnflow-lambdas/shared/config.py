import os


class Config:
    """Centralized config loaded from Lambda environment variables."""

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    # Hugging Face / Mistral LLM
    HF_API_TOKEN: str = os.getenv("HF_API_TOKEN", "")
    HF_MODEL_ENDPOINT: str = os.getenv(
        "HF_MODEL_ENDPOINT",
        "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3",
    )

    # SQS
    ROADMAP_QUEUE_URL: str = os.getenv("ROADMAP_QUEUE_URL", "")
    SUMMARIZER_QUEUE_URL: str = os.getenv("SUMMARIZER_QUEUE_URL", "")
    QUIZ_QUEUE_URL: str = os.getenv("QUIZ_QUEUE_URL", "")
    WEAK_TOPIC_QUEUE_URL: str = os.getenv("WEAK_TOPIC_QUEUE_URL", "")
    EMAIL_QUEUE_URL: str = os.getenv("EMAIL_QUEUE_URL", "")

    # Email (SES or SMTP)
    MAIL_FROM: str = os.getenv("MAIL_FROM", "")
    AWS_REGION: str = os.getenv("AWS_REGION", "ap-south-1")

    # Supabase (for storage access if needed)
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")


config = Config()
