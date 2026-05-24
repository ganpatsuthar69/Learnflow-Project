"""
SQS Queue Client — used by FastAPI backend to trigger Lambda functions.
Publishes messages to SQS queues that Lambda functions consume.
"""

import json
import os
import boto3

AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")

sqs = boto3.client("sqs", region_name=AWS_REGION)

# Queue URLs (set via environment variables)
ROADMAP_QUEUE_URL = os.getenv("ROADMAP_QUEUE_URL", "")
SUMMARIZER_QUEUE_URL = os.getenv("SUMMARIZER_QUEUE_URL", "")
QUIZ_QUEUE_URL = os.getenv("QUIZ_QUEUE_URL", "")
WEAK_TOPIC_QUEUE_URL = os.getenv("WEAK_TOPIC_QUEUE_URL", "")
EMAIL_QUEUE_URL = os.getenv("EMAIL_QUEUE_URL", "")


def _send(queue_url: str, body: dict) -> str:
    response = sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(body),
    )
    return response["MessageId"]


def trigger_roadmap_generation(student_id: str, topic: str, level: str, context: str = "") -> str:
    """Trigger AI roadmap generation for a student."""
    return _send(ROADMAP_QUEUE_URL, {
        "student_id": student_id,
        "topic": topic,
        "level": level,
        "context": context,
    })


def trigger_note_summarization(note_id: str, student_id: str, file_url: str, action: str = "summary") -> str:
    """Trigger note summarization (summary, flashcards, mcqs, keypoints)."""
    return _send(SUMMARIZER_QUEUE_URL, {
        "note_id": note_id,
        "student_id": student_id,
        "file_url": file_url,
        "action": action,
    })


def trigger_quiz_generation(student_id: str, topic_id: str, topic_title: str, difficulty: str = "medium", count: int = 10) -> str:
    """Trigger quiz generation for a topic."""
    return _send(QUIZ_QUEUE_URL, {
        "student_id": student_id,
        "topic_id": topic_id,
        "topic_title": topic_title,
        "difficulty": difficulty,
        "count": count,
    })


def trigger_weak_topic_analysis(student_id: str) -> str:
    """Trigger weak topic analysis after quiz completion."""
    return _send(WEAK_TOPIC_QUEUE_URL, {
        "student_id": student_id,
    })


def send_email(to: str, template: str, params: dict = None) -> str:
    """Send email via Lambda (SES)."""
    return _send(EMAIL_QUEUE_URL, {
        "to": to,
        "template": template,
        "params": params or {},
    })
