"""
Roadmap Generator Lambda
Trigger: SQS
Input: { "student_id": "uuid", "topic": "Data Structures", "level": "beginner" }
Output: Generates personalized roadmap via Mistral LLM and stores in DB.
"""

import asyncio
import json
import sys
sys.path.insert(0, "/opt/python")  # Lambda layer path

from shared.sqs import parse_sqs_records
from shared.llm import call_mistral, parse_json_response
from shared.db import get_connection, get_cursor


ROADMAP_PROMPT = """You are an expert CS educator. Generate a structured learning roadmap.

Topic: {topic}
Level: {level}
Student Context: {context}

Return a JSON object with this exact structure:
{{
  "title": "Roadmap title",
  "description": "Brief description",
  "steps": [
    {{
      "title": "Step title",
      "description": "What to learn",
      "step_order": 1,
      "topics": [
        {{
          "title": "Topic name",
          "description": "Brief explanation",
          "topic_order": 1
        }}
      ]
    }}
  ]
}}

Generate 5-8 steps with 2-4 topics each. Be specific to {topic} at {level} level.
Return ONLY valid JSON, no extra text."""


def handler(event, context):
    """Lambda entry point — processes SQS messages."""
    records = parse_sqs_records(event)
    results = asyncio.run(_process_records(records))
    return {"statusCode": 200, "body": json.dumps({"processed": len(results)})}


async def _process_records(records: list[dict]) -> list:
    results = []
    for record in records:
        result = await _generate_roadmap(record)
        results.append(result)
    return results


async def _generate_roadmap(payload: dict) -> dict:
    student_id = payload["student_id"]
    topic = payload["topic"]
    level = payload.get("level", "beginner")
    student_context = payload.get("context", "CS undergraduate student")

    prompt = ROADMAP_PROMPT.format(
        topic=topic, level=level, context=student_context
    )

    response_text = await call_mistral(prompt, max_tokens=2048)
    roadmap_data = parse_json_response(response_text)

    if not roadmap_data:
        print(f"Failed to parse LLM response for student {student_id}")
        return {"student_id": student_id, "status": "failed"}

    # Store in database
    _store_roadmap(student_id, roadmap_data, topic, level)
    return {"student_id": student_id, "status": "success"}


def _store_roadmap(student_id: str, data: dict, topic: str, level: str):
    with get_connection() as conn:
        with get_cursor(conn) as cur:
            cur.execute(
                """INSERT INTO roadmaps (title, description, level, roadmap_type, created_by_ai)
                   VALUES (%s, %s, %s, 'ai', true) RETURNING id""",
                (data["title"], data.get("description", ""), level),
            )
            roadmap_id = cur.fetchone()["id"]

            # Link to student
            cur.execute(
                """INSERT INTO user_roadmaps (student_id, roadmap_id, status)
                   VALUES (%s, %s, 'active')""",
                (student_id, roadmap_id),
            )

            # Insert steps and topics
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
