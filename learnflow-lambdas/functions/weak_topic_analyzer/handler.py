"""
Weak Topic Analyzer Lambda
Trigger: SQS (after quiz completion or revision miss)
Input: { "student_id": "uuid" }
Output: Analyzes quiz accuracy + revision performance to flag weak topics.
"""

import json
import sys
from datetime import datetime
sys.path.insert(0, "/opt/python")

from shared.sqs import parse_sqs_records
from shared.db import get_connection, get_cursor

# Thresholds
WEAK_ACCURACY_THRESHOLD = 0.6  # Below 60% accuracy = weak
MISSED_REVISION_THRESHOLD = 2  # 2+ missed revisions = weak


def handler(event, context):
    records = parse_sqs_records(event)
    results = []
    for record in records:
        result = _analyze_student(record["student_id"])
        results.append(result)
    return {"statusCode": 200, "body": json.dumps({"analyzed": len(results)})}


def _analyze_student(student_id: str) -> dict:
    """Analyze a student's performance and update weak topic flags."""
    weak_topics = []

    with get_connection() as conn:
        with get_cursor(conn) as cur:
            # 1. Check quiz accuracy per topic
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

            # 2. Check missed revisions per topic
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
                # Avoid duplicates
                existing = [w for w in weak_topics if w["topic_id"] == str(row["topic_id"])]
                if existing:
                    existing[0]["reason"] = "low_accuracy_and_missed_revisions"
                else:
                    weak_topics.append({
                        "topic_id": str(row["topic_id"]),
                        "title": row["title"],
                        "reason": "missed_revisions",
                        "missed_count": row["missed_count"],
                    })

            # 3. Upsert weak topics
            for wt in weak_topics:
                cur.execute(
                    """INSERT INTO weak_topics (student_id, topic_id, reason, detected_at)
                       VALUES (%s, %s, %s, %s)
                       ON CONFLICT (student_id, topic_id)
                       DO UPDATE SET reason = EXCLUDED.reason, detected_at = EXCLUDED.detected_at""",
                    (student_id, wt["topic_id"], wt["reason"], datetime.utcnow()),
                )

            # 4. Remove topics that are no longer weak
            cur.execute(
                """DELETE FROM weak_topics
                   WHERE student_id = %s AND topic_id NOT IN %s""",
                (student_id, tuple(wt["topic_id"] for wt in weak_topics) or ("__none__",)),
            ) if weak_topics else None

            conn.commit()

    return {"student_id": student_id, "weak_topics": len(weak_topics)}
