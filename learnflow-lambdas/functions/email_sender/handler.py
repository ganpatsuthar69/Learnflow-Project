"""
Email Sender Lambda
Trigger: SQS
Input: { "to": "email", "subject": "str", "body": "str", "template": "otp|welcome|revision_reminder" }
Output: Sends email via AWS SES.
"""

import json
import sys
import boto3
sys.path.insert(0, "/opt/python")

from shared.sqs import parse_sqs_records
from shared.config import config

ses = boto3.client("ses", region_name=config.AWS_REGION)

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


def handler(event, context):
    records = parse_sqs_records(event)
    sent = 0
    failed = 0

    for record in records:
        success = _send_email(record)
        if success:
            sent += 1
        else:
            failed += 1

    return {"statusCode": 200, "body": json.dumps({"sent": sent, "failed": failed})}


def _send_email(payload: dict) -> bool:
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
        return True
    except Exception as e:
        print(f"Email send failed to {to_email}: {e}")
        return False
