"""
SQS Queue Client — used by FastAPI backend to trigger Lambda functions.
Two queues:
  - AI_QUEUE: roadmap generation, note summarization, quiz generation
  - TASK_QUEUE: email sending, weak topic analysis, revision scheduling
"""

import json
import os
import boto3

AWS_REGION = os.getenv("AWS_REGION", "ap-south-1")

sqs = boto3.client("sqs", region_name=AWS_REGION)

AI_QUEUE_URL = os.getenv("AI_QUEUE_URL", "")
TASK_QUEUE_URL = os.getenv("TASK_QUEUE_URL", "")


def _send(queue_url: str, action: str, payload: dict) -> str:
    response = sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps({"action": action, "payload": payload}),
    )
    return response["MessageId"]


# ─── AI Queue ──────────────────────────────────────────────────────────────────

def trigger_roadmap_generation(student_id: str, topic: str, level: str, context: str = "") -> str:
    return _send(AI_QUEUE_URL, "generate_roadmap", {
        "student_id": student_id,
        "topic": topic,
        "level": level,
        "context": context,
    })


def trigger_note_summarization(note_id: str, student_id: str, file_url: str, action: str = "summary") -> str:
    return _send(AI_QUEUE_URL, "summarize_note", {
        "note_id": note_id,
        "student_id": student_id,
        "file_url": file_url,
        "type": action,
    })


def trigger_quiz_generation(student_id: str, topic_id: str, topic_title: str, difficulty: str = "medium", count: int = 10) -> str:
    return _send(AI_QUEUE_URL, "generate_quiz", {
        "student_id": student_id,
        "topic_id": topic_id,
        "topic_title": topic_title,
        "difficulty": difficulty,
        "count": count,
    })


# ─── Task Queue ────────────────────────────────────────────────────────────────

def send_email(to: str, template: str, params: dict = None) -> str:
    return _send(TASK_QUEUE_URL, "send_email", {
        "to": to,
        "template": template,
        "params": params or {},
    })


def trigger_weak_topic_analysis(student_id: str) -> str:
    return _send(TASK_QUEUE_URL, "analyze_weak_topics", {
        "student_id": student_id,
    })
