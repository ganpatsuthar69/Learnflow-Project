"""AWS CDK Stack for LearnFlow Lambda Functions (2 functions)."""

from aws_cdk import (
    Stack,
    Duration,
    aws_lambda as _lambda,
    aws_sqs as sqs,
    aws_events as events,
    aws_events_targets as targets,
    aws_lambda_event_sources as event_sources,
    aws_iam as iam,
)
from constructs import Construct


class LearnFlowLambdaStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        # --- Shared Lambda Layer ---
        shared_layer = _lambda.LayerVersion(
            self, "SharedLayer",
            code=_lambda.Code.from_asset("../layers"),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_12],
            description="Shared utilities (db, llm, sqs, config)",
        )

        # --- SQS Queues (2 queues) ---
        ai_queue = sqs.Queue(
            self, "AIQueue",
            queue_name="learnflow-ai-queue",
            visibility_timeout=Duration.seconds(300),
        )

        task_queue = sqs.Queue(
            self, "TaskQueue",
            queue_name="learnflow-task-queue",
            visibility_timeout=Duration.seconds(120),
        )

        # --- Common environment variables ---
        common_env = {
            "DATABASE_URL": "{{resolve:ssm:/learnflow/database-url}}",
            "HF_API_TOKEN": "{{resolve:ssm:/learnflow/hf-api-token}}",
            "SUPABASE_URL": "{{resolve:ssm:/learnflow/supabase-url}}",
            "SUPABASE_SERVICE_ROLE_KEY": "{{resolve:ssm:/learnflow/supabase-key}}",
            "MAIL_FROM": "{{resolve:ssm:/learnflow/mail-from}}",
            "AI_QUEUE_URL": ai_queue.queue_url,
            "TASK_QUEUE_URL": task_queue.queue_url,
        }

        # --- Lambda Functions ---

        # 1. AI Processor (roadmap, summarizer, quiz)
        ai_fn = _lambda.Function(
            self, "AIProcessor",
            function_name="learnflow-ai-processor",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="handler.handler",
            code=_lambda.Code.from_asset("../functions/ai_processor"),
            layers=[shared_layer],
            timeout=Duration.seconds(180),
            memory_size=512,
            environment=common_env,
        )
        ai_fn.add_event_source(
            event_sources.SqsEventSource(ai_queue, batch_size=1)
        )

        # 2. Task Processor (email, weak topics, revision scheduler)
        task_fn = _lambda.Function(
            self, "TaskProcessor",
            function_name="learnflow-task-processor",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="handler.handler",
            code=_lambda.Code.from_asset("../functions/task_processor"),
            layers=[shared_layer],
            timeout=Duration.seconds(60),
            memory_size=256,
            environment=common_env,
        )
        task_fn.add_event_source(
            event_sources.SqsEventSource(task_queue, batch_size=10)
        )

        # Grant SES permissions to task processor
        task_fn.add_to_role_policy(
            iam.PolicyStatement(
                actions=["ses:SendEmail", "ses:SendRawEmail"],
                resources=["*"],
            )
        )

        # Daily cron for revision scheduler (6:00 AM IST = 00:30 UTC)
        events.Rule(
            self, "RevisionScheduleRule",
            schedule=events.Schedule.cron(hour="0", minute="30"),
            targets=[targets.LambdaFunction(task_fn)],
        )
