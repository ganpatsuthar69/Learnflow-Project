"""
Task Processor Lambda — Handles all non-AI workloads.
Trigger: SQS (single queue, routes by "action" field) + EventBridge (cron)

Supported actions:
  - send_email
  - analyze_weak_topics
  - schedule_revisions (also triggered by daily cron)

Input format:
  { "action": "send_email", "payload": { ... } }

For EventBridge cron:
  Automatically runs schedule_revisions
"""

import json
import sys
import boto3
from datetime import date, timedelta, datetime
sys.path.insert(0, "/opt/python")

from shared.sqs import parse_sqs_records
from shared.db import get_connection, get_cursor
from shared.config import config

ses = boto3.client("ses", region_name=config.AWS_REGION)


# ─── Email Templates ───────────────────────────────────────────────────────────

TEMPLATES = {
    "otp": {
        "subject": "Your OTP - LearnFlow",
        "body": "Hi,\n\nYour OTP for LearnFlow is: {otp}\n\nThis OTP is valid for 5 minutes.\n\nIf you did not request this, please ignore this email.\n\n- LearnFlow Team",
    },
    "welcome": {
        "subject": "Welcome to LearnFlow!",
        "body": "Hi {name},\n\nWelcome to LearnFlow! Your account has been verified.\n\nStart your personalized learning journey now.\n\n- LearnFlow Team",
    },
    "revision_reminder": {
        "subject": "Time to Revise - LearnFlow",
        "body": "Hi {name},\n\nYou have {count} topics due for revision today:\n\n{topics}\n\nConsistent revision builds long-term memory.\n\n- LearnFlow Team",
    },
}

# Weak topic thresholds
WEAK_ACCURACY_THRESHOLD = 0.6
MISSED_REVISION_THRESHOLD = 2

# Spaced repetition intervals
SRS_INTERVALS = [2, 7, 15, 30]


# ─── Handler ───────────────────────────────────────────────────────────────────

def handler(event, context):
    """Lambda entry point — routes by action or handles EventBridge cron."""

    # EventBridge cron trigger (no Records field)
    if "source" in event and event["source"] == "aws.events":
        result = _schedule_revisions()
        return {"statusCode": 200, "body": json.dumps({"scheduled": result})}

    # SQS trigger
    records = parse_sqs_records(event)
    results = []

    for record in records:
        action = record.get("action", "")
        payload = record.get("payload", {})

        if action == "send_email":
            result = _send_email(payload)
        elif action == "analyze_weak_topics":
            result = _analyze_weak_topics(payload)
        elif action == "schedule_revisions":
            result = _schedule_revisions()
        else:
            result = {"status": "error", "reason": f"unknown action: {action}"}

        results.append(result)

    return {"statusCode": 200, "body": json.dumps({"processed": len(results)})}


# ─── Email Sender ──────────────────────────────────────────────────────────────

def _send_email(payload: dict) -> dict:
    to_email = payload["to"]
    template = payload.get("template")
    params = payload.get("params", {})

    if template and template in TEMPLATES:
        subject = TEMPLATES[template]["subject"]
        body = TEMPLATES[template]["body"].format(**params)
    else:
        subject = payload.get("subject", "LearnFlow Notification")
        body = payload.get("body", "")

    try:
        ses.send_email(
            Source=f"LearnFlow <{config.MAIL_FROM}>",
            Destination={"ToAddresses": [to_email]},
            Message={
                "Subject": {"Data": subject, "Charset": "UTF-8"},
                "Body": {"Text": {"Data": body, "Charset": "UTF-8"}},
            },
        )
        return {"to": to_email, "status": "sent"}
    except Exception as e:
        print(f"Email send failed to {to_email}: {e}")
        return {"to": to_email, "status": "failed"}


# ─── Weak Topic Analyzer ──────────────────────────────────────────────────────

def _analyze_weak_topics(payload: dict) -> dict:
    student_id = payload["student_id"]
    weak_topics = []

    with get_connection() as conn:
        with get_cursor(conn) as cur:
            # Check quiz accuracy per topic
            cur.execute(
                """SELECT qs.topic_id, t.title,
                          COUNT(qq.id) as total,
                          SUM(CASE WHEN qq.student_answer = qq.correct_answer THEN 1 ELSE 0 END) as correct
                   FROM quiz_sessions qs
                   JOIN quiz_questions qq ON qq.session_id = qs.id
                   JOIN topics t ON t.id = qs.topic_id
                   WHERE qs.student_id = %s AND qq.student_answer IS NOT NULL
                   GROUP BY qs.topic_id, t.title""",
                (student_id,),
            )

            for row in cur.fetchall():
                accuracy = row["correct"] / row["total"] if row["total"] > 0 else 0
                if accuracy < WEAK_ACCURACY_THRESHOLD:
                    weak_topics.append({
                        "topic_id": str(row["topic_id"]),
                        "title": row["title"],
                        "reason": "low_quiz_accuracy",
                        "accuracy": round(accuracy, 2),
                    })

            # Check missed revisions
            cur.execute(
                """SELECT utp.topic_id, t.title, COUNT(*) as missed_count
                   FROM revision_tasks rt
                   JOIN user_topic_progress utp ON utp.id = rt.topic_progress_id
                   JOIN topics t ON t.id = utp.topic_id
                   WHERE rt.student_id = %s AND rt.status = 'missed'
                   GROUP BY utp.topic_id, t.title
                   HAVING COUNT(*) >= %s""",
                (student_id, MISSED_REVISION_THRESHOLD),
            )

            for row in cur.fetchall():
                existing = [w for w in weak_topics if w["topic_id"] == str(row["topic_id"])]
                if existing:
                    existing[0]["reason"] = "low_accuracy_and_missed_revisions"
                else:
                    weak_topics.append({
                        "topic_id": str(row["topic_id"]),
                        "title": row["title"],
                        "reason": "missed_revisions",
                    })

            # Upsert weak topics
            for wt in weak_topics:
                cur.execute(
                    """INSERT INTO weak_topics (student_id, topic_id, reason, detected_at)
                       VALUES (%s, %s, %s, %s)
                       ON CONFLICT (student_id, topic_id)
                       DO UPDATE SET reason = EXCLUDED.reason, detected_at = EXCLUDED.detected_at""",
                    (student_id, wt["topic_id"], wt["reason"], datetime.utcnow()),
                )

            conn.commit()

    return {"student_id": student_id, "weak_topics": len(weak_topics)}


# ─── Revision Scheduler ───────────────────────────────────────────────────────

def _schedule_revisions() -> int:
    today = date.today()
    count = 0

    with get_connection() as conn:
        with get_cursor(conn) as cur:
            for interval in SRS_INTERVALS:
                target_date = today - timedelta(days=interval)

                cur.execute(
                    """SELECT utp.id, ur.student_id, t.title as topic_title
                       FROM user_topic_progress utp
                       JOIN user_roadmaps ur ON ur.id = utp.user_roadmap_id
                       JOIN topics t ON t.id = utp.topic_id
                       WHERE utp.is_completed = true
                         AND utp.completed_at::date = %s
                         AND NOT EXISTS (
                           SELECT 1 FROM revision_tasks rt
                           WHERE rt.topic_progress_id = utp.id
                             AND rt.scheduled_date = %s
                         )""",
                    (target_date, today),
                )

                for row in cur.fetchall():
                    cur.execute(
                        """INSERT INTO revision_tasks
                           (student_id, topic_progress_id, topic_title, scheduled_date, interval_days, status)
                           VALUES (%s, %s, %s, %s, %s, 'pending')""",
                        (row["student_id"], row["id"], row["topic_title"], today, interval),
                    )
                    count += 1

            # Mark overdue as missed
            cur.execute(
                """UPDATE revision_tasks SET status = 'missed'
                   WHERE status = 'pending' AND scheduled_date < %s""",
                (today,),
            )
            conn.commit()

    return count
