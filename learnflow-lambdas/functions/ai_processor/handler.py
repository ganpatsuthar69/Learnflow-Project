"""
AI Processor Lambda — Handles all AI/LLM workloads.
Trigger: SQS (single queue, routes by "action" field)

Supported actions:
  - generate_roadmap
  - summarize_note
  - generate_quiz

Input format:
  { "action": "generate_roadmap", "payload": { ... } }
"""

import asyncio
import json
import sys
sys.path.insert(0, "/opt/python")

from shared.sqs import parse_sqs_records
from shared.llm import call_mistral, parse_json_response
from shared.db import get_connection, get_cursor


# ─── Prompts ───────────────────────────────────────────────────────────────────

ROADMAP_PROMPT = """You are an expert CS educator. Generate a structured learning roadmap.

Topic: {topic}
Level: {level}
Student Context: {context}

Return a JSON object:
{{
  "title": "Roadmap title",
  "description": "Brief description",
  "steps": [
    {{
      "title": "Step title",
      "description": "What to learn",
      "step_order": 1,
      "topics": [
        {{"title": "Topic name", "description": "Brief explanation", "topic_order": 1}}
      ]
    }}
  ]
}}

Generate 5-8 steps with 2-4 topics each. Return ONLY valid JSON."""

SUMMARY_PROMPT = """Summarize the following text concisely.

Text:
{text}

Return JSON:
{{"summary": "concise summary in 3-5 sentences", "key_points": ["point 1", "point 2", "point 3", "point 4", "point 5"]}}

Return ONLY valid JSON."""

FLASHCARD_PROMPT = """Generate flashcards from this text for study revision.

Text:
{text}

Return JSON array of 8-10 flashcards:
[{{"front": "question or term", "back": "answer or definition"}}]

Return ONLY valid JSON array."""

MCQ_PROMPT = """Generate multiple choice questions from this text.

Text:
{text}

Return JSON array of 5-8 MCQs:
[{{"question": "text", "options": ["A) opt", "B) opt", "C) opt", "D) opt"], "correct": "A", "explanation": "why"}}]

Return ONLY valid JSON array."""

QUIZ_PROMPT = """Generate {count} multiple choice questions about "{topic}" at {difficulty} difficulty for a CS student.

Return a JSON array:
[{{"question": "text", "options": ["A) opt", "B) opt", "C) opt", "D) opt"], "correct": "A", "explanation": "why", "difficulty": "{difficulty}"}}]

Return ONLY valid JSON array."""


# ─── Handler ───────────────────────────────────────────────────────────────────

def handler(event, context):
    """Lambda entry point — routes by action field."""
    records = parse_sqs_records(event)
    results = asyncio.run(_process_records(records))
    return {"statusCode": 200, "body": json.dumps({"processed": len(results)})}


async def _process_records(records: list[dict]) -> list:
    results = []
    for record in records:
        action = record.get("action", "")
        payload = record.get("payload", {})

        if action == "generate_roadmap":
            result = await _generate_roadmap(payload)
        elif action == "summarize_note":
            result = await _summarize_note(payload)
        elif action == "generate_quiz":
            result = await _generate_quiz(payload)
        else:
            result = {"status": "error", "reason": f"unknown action: {action}"}

        results.append(result)
    return results


# ─── Roadmap Generation ────────────────────────────────────────────────────────

async def _generate_roadmap(payload: dict) -> dict:
    student_id = payload["student_id"]
    topic = payload["topic"]
    level = payload.get("level", "beginner")
    context = payload.get("context", "CS undergraduate student")

    prompt = ROADMAP_PROMPT.format(topic=topic, level=level, context=context)
    response_text = await call_mistral(prompt, max_tokens=2048)
    data = parse_json_response(response_text)

    if not data:
        return {"student_id": student_id, "action": "generate_roadmap", "status": "failed"}

    _store_roadmap(student_id, data, level)
    return {"student_id": student_id, "action": "generate_roadmap", "status": "success"}


def _store_roadmap(student_id: str, data: dict, level: str):
    with get_connection() as conn:
        with get_cursor(conn) as cur:
            cur.execute(
                """INSERT INTO roadmaps (title, description, level, roadmap_type, created_by_ai)
                   VALUES (%s, %s, %s, 'ai', true) RETURNING id""",
                (data["title"], data.get("description", ""), level),
            )
            roadmap_id = cur.fetchone()["id"]

            cur.execute(
                """INSERT INTO user_roadmaps (student_id, roadmap_id, status)
                   VALUES (%s, %s, 'active')""",
                (student_id, roadmap_id),
            )

            for step in data.get("steps", []):
                cur.execute(
                    """INSERT INTO steps (roadmap_id, title, description, step_order)
                       VALUES (%s, %s, %s, %s) RETURNING id""",
                    (roadmap_id, step["title"], step.get("description", ""), step["step_order"]),
                )
                step_id = cur.fetchone()["id"]

                for t in step.get("topics", []):
                    cur.execute(
                        """INSERT INTO topics (step_id, title, description, topic_order)
                           VALUES (%s, %s, %s, %s)""",
                        (step_id, t["title"], t.get("description", ""), t["topic_order"]),
                    )
            conn.commit()


# ─── Note Summarization ────────────────────────────────────────────────────────

async def _summarize_note(payload: dict) -> dict:
    note_id = payload["note_id"]
    student_id = payload["student_id"]
    file_url = payload["file_url"]
    action = payload.get("type", "summary")

    text = await _fetch_note_content(file_url)
    if not text:
        return {"note_id": note_id, "status": "failed", "reason": "empty_content"}

    text = text[:4000]

    prompt_map = {
        "summary": SUMMARY_PROMPT,
        "flashcards": FLASHCARD_PROMPT,
        "mcqs": MCQ_PROMPT,
        "keypoints": SUMMARY_PROMPT,
    }
    prompt = prompt_map.get(action, SUMMARY_PROMPT).format(text=text)
    response_text = await call_mistral(prompt, max_tokens=1500)
    parsed = parse_json_response(response_text)

    if not parsed:
        return {"note_id": note_id, "status": "failed", "reason": "parse_error"}

    _store_summary(note_id, student_id, action, parsed)
    return {"note_id": note_id, "action": "summarize_note", "status": "success"}


async def _fetch_note_content(file_url: str) -> str:
    import httpx
    from shared.config import config

    async with httpx.AsyncClient(timeout=30.0) as client:
        sign_url = f"{config.SUPABASE_URL}/storage/v1/object/sign/Notes/{file_url}"
        resp = await client.post(
            sign_url,
            headers={"Authorization": f"Bearer {config.SUPABASE_KEY}"},
            json={"expiresIn": 300},
        )
        if resp.status_code != 200:
            return ""
        signed = resp.json()
        download_url = f"{config.SUPABASE_URL}/storage/v1{signed['signedURL']}"
        file_resp = await client.get(download_url)
        return file_resp.text if file_resp.status_code == 200 else ""


def _store_summary(note_id: str, student_id: str, action: str, data):
    with get_connection() as conn:
        with get_cursor(conn) as cur:
            cur.execute(
                """INSERT INTO note_summaries (note_id, student_id, action_type, result_data)
                   VALUES (%s, %s, %s, %s)
                   ON CONFLICT (note_id, action_type)
                   DO UPDATE SET result_data = EXCLUDED.result_data""",
                (note_id, student_id, action, json.dumps(data)),
            )
            conn.commit()


# ─── Quiz Generation ───────────────────────────────────────────────────────────

async def _generate_quiz(payload: dict) -> dict:
    student_id = payload["student_id"]
    topic_id = payload["topic_id"]
    topic_title = payload["topic_title"]
    difficulty = payload.get("difficulty", "medium")
    count = payload.get("count", 10)

    prompt = QUIZ_PROMPT.format(topic=topic_title, difficulty=difficulty, count=count)
    response_text = await call_mistral(prompt, max_tokens=2048)
    questions = parse_json_response(response_text)

    if not questions or not isinstance(questions, list):
        return {"student_id": student_id, "action": "generate_quiz", "status": "failed"}

    _store_quiz(student_id, topic_id, questions, difficulty)
    return {"student_id": student_id, "action": "generate_quiz", "status": "success"}


def _store_quiz(student_id: str, topic_id: str, questions: list, difficulty: str):
    with get_connection() as conn:
        with get_cursor(conn) as cur:
            cur.execute(
                """INSERT INTO quiz_sessions (student_id, topic_id, difficulty, total_questions)
                   VALUES (%s, %s, %s, %s) RETURNING id""",
                (student_id, topic_id, difficulty, len(questions)),
            )
            session_id = cur.fetchone()["id"]

            for i, q in enumerate(questions):
                cur.execute(
                    """INSERT INTO quiz_questions
                       (session_id, question_text, options, correct_answer, explanation, question_order)
                       VALUES (%s, %s, %s, %s, %s, %s)""",
                    (session_id, q["question"], json.dumps(q["options"]), q["correct"], q.get("explanation", ""), i + 1),
                )
            conn.commit()
