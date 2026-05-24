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

    # SQS Queues
    AI_QUEUE_URL: str = os.getenv("AI_QUEUE_URL", "")
    TASK_QUEUE_URL: str = os.getenv("TASK_QUEUE_URL", "")

    # Email
    MAIL_FROM: str = os.getenv("MAIL_FROM", "")
    AWS_REGION: str = os.getenv("AWS_REGION", "ap-south-1")

    # Supabase
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")


config = Config()
