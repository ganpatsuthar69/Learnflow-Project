"""
Revision Scheduler Lambda (Spaced Repetition)
Trigger: EventBridge (daily cron at 6:00 AM IST)
Purpose: Calculate which topics need revision for each student based on SRS intervals (2/7/15 days).
"""

import json
import sys
from datetime import date, timedelta
sys.path.insert(0, "/opt/python")

from shared.db import get_connection, get_cursor

# Spaced repetition intervals in days
SRS_INTERVALS = [2, 7, 15, 30]


def handler(event, context):
    """Runs daily to schedule revisions for all active students."""
    today = date.today()
    scheduled = _schedule_revisions(today)
    return {"statusCode": 200, "body": json.dumps({"scheduled": scheduled})}


def _schedule_revisions(today: date) -> int:
    """Check completed topics and create revision tasks based on SRS intervals."""
    count = 0

    with get_connection() as conn:
        with get_cursor(conn) as cur:
            # Find topics completed by students that need revision
            for interval in SRS_INTERVALS:
                target_date = today - timedelta(days=interval)

                cur.execute(
                    """SELECT utp.id, utp.user_roadmap_id, utp.topic_id,
                              ur.student_id, t.title as topic_title
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

                rows = cur.fetchall()

                for row in rows:
                    cur.execute(
                        """INSERT INTO revision_tasks
                           (student_id, topic_progress_id, topic_title, scheduled_date, interval_days, status)
                           VALUES (%s, %s, %s, %s, %s, 'pending')""",
                        (row["student_id"], row["id"], row["topic_title"], today, interval),
                    )
                    count += 1

            # Mark overdue revision tasks as missed
            cur.execute(
                """UPDATE revision_tasks
                   SET status = 'missed'
                   WHERE status = 'pending' AND scheduled_date < %s""",
                (today,),
            )

            conn.commit()

    return count
