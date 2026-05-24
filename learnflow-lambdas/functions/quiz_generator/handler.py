"""
Quiz Generator Lambda
Trigger: SQS
Input: { "student_id": "uuid", "topic_id": "uuid", "topic_title": "str", "difficulty": "easy|medium|hard", "count": 10 }
Output: Generates quiz questions via LLM and stores in DB.
"""

import asyncio
import json
import sys
sys.path.insert(0, "/opt/python")

from shared.sqs import parse_sqs_records
from shared.llm import call_mistral, parse_json_response
from shared.db import get_connection, get_cursor


QUIZ_PROMPT = """Generate {count} multiple choice questions about "{topic}" at {difficulty} difficulty for a CS student.

Return a JSON array:
[
  {{
    "question": "question text",
    "options": ["A) option", "B) option", "C) option", "D) option"],
    "correct": "A",
    "explanation": "why this is correct",
    "difficulty": "{difficulty}"
  }}
]

Make questions specific, educational, and progressively challenging.
Return ONLY valid JSON array."""


def handler(event, context):
    records = parse_sqs_records(event)
    results = asyncio.run(_process_records(records))
    return {"statusCode": 200, "body": json.dumps({"processed": len(results)})}


async def _process_records(records: list[dict]) -> list:
    results = []
    for record in records:
        result = await _generate_quiz(record)
        results.append(result)
    return results


async def _generate_quiz(payload: dict) -> dict:
    student_id = payload["student_id"]
    topic_id = payload["topic_id"]
    topic_title = payload["topic_title"]
    difficulty = payload.get("difficulty", "medium")
    count = payload.get("count", 10)

    prompt = QUIZ_PROMPT.format(
        topic=topic_title, difficulty=difficulty, count=count
    )

    response_text = await call_mistral(prompt, max_tokens=2048)
    questions = parse_json_response(response_text)

    if not questions or not isinstance(questions, list):
        return {"student_id": student_id, "status": "failed"}

    _store_quiz(student_id, topic_id, questions, difficulty)
    return {"student_id": student_id, "status": "success", "count": len(questions)}


def _store_quiz(student_id: str, topic_id: str, questions: list, difficulty: str):
    with get_connection() as conn:
        with get_cursor(conn) as cur:
            # Create quiz session
            cur.execute(
                """INSERT INTO quiz_sessions (student_id, topic_id, difficulty, total_questions)
                   VALUES (%s, %s, %s, %s) RETURNING id""",
                (student_id, topic_id, difficulty, len(questions)),
            )
            session_id = cur.fetchone()["id"]

            # Insert questions
            for i, q in enumerate(questions):
                cur.execute(
                    """INSERT INTO quiz_questions
                       (session_id, question_text, options, correct_answer, explanation, question_order)
                       VALUES (%s, %s, %s, %s, %s, %s)""",
                    (
                        session_id,
                        q["question"],
                        json.dumps(q["options"]),
                        q["correct"],
                        q.get("explanation", ""),
                        i + 1,
                    ),
                )

            conn.commit()
