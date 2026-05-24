"""
Note Summarizer Lambda
Trigger: SQS
Input: { "note_id": "uuid", "student_id": "uuid", "file_url": "path", "action": "summary|flashcards|mcqs|keypoints" }
Output: Generates AI summary/flashcards/MCQs and stores in DB.
"""

import asyncio
import json
import sys
sys.path.insert(0, "/opt/python")

from shared.sqs import parse_sqs_records
from shared.llm import call_mistral, parse_json_response
from shared.db import get_connection, get_cursor
from shared.config import config
import httpx


SUMMARY_PROMPT = """Summarize the following text concisely. Extract the most important concepts.

Text:
{text}

Return JSON:
{{
  "summary": "concise summary in 3-5 sentences",
  "key_points": ["point 1", "point 2", "point 3", "point 4", "point 5"]
}}

Return ONLY valid JSON."""

FLASHCARD_PROMPT = """Generate flashcards from this text for study revision.

Text:
{text}

Return JSON array of 8-10 flashcards:
[
  {{"front": "question or term", "back": "answer or definition"}}
]

Return ONLY valid JSON array."""

MCQ_PROMPT = """Generate multiple choice questions from this text.

Text:
{text}

Return JSON array of 5-8 MCQs:
[
  {{
    "question": "question text",
    "options": ["A) option", "B) option", "C) option", "D) option"],
    "correct": "A",
    "explanation": "brief explanation"
  }}
]

Return ONLY valid JSON array."""


def handler(event, context):
    records = parse_sqs_records(event)
    results = asyncio.run(_process_records(records))
    return {"statusCode": 200, "body": json.dumps({"processed": len(results)})}


async def _process_records(records: list[dict]) -> list:
    results = []
    for record in records:
        result = await _summarize_note(record)
        results.append(result)
    return results


async def _summarize_note(payload: dict) -> dict:
    note_id = payload["note_id"]
    student_id = payload["student_id"]
    file_url = payload["file_url"]
    action = payload.get("action", "summary")

    # Fetch file content from Supabase
    text = await _fetch_note_content(file_url)
    if not text:
        return {"note_id": note_id, "status": "failed", "reason": "empty_content"}

    # Truncate to fit LLM context
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

    _store_result(note_id, student_id, action, parsed)
    return {"note_id": note_id, "status": "success", "action": action}


async def _fetch_note_content(file_url: str) -> str:
    """Download note content from Supabase storage."""
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
        if file_resp.status_code == 200:
            return file_resp.text
    return ""


def _store_result(note_id: str, student_id: str, action: str, data):
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
