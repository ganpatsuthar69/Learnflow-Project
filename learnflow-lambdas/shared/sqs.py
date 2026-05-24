"""SQS helper for publishing messages from the backend."""

import json
import boto3
from .config import config

sqs = boto3.client("sqs", region_name=config.AWS_REGION)


def send_message(queue_url: str, body: dict, delay_seconds: int = 0) -> str:
    """Send a message to an SQS queue. Returns MessageId."""
    response = sqs.send_message(
        QueueUrl=queue_url,
        MessageBody=json.dumps(body),
        DelaySeconds=delay_seconds,
    )
    return response["MessageId"]


def parse_sqs_records(event: dict) -> list[dict]:
    """Extract and parse message bodies from an SQS Lambda event."""
    records = []
    for record in event.get("Records", []):
        body = json.loads(record["body"])
        records.append(body)
    return records
