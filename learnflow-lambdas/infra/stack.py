"""AWS CDK Stack for LearnFlow Lambda Functions."""

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
            code=_lambda.Code.from_asset("../shared"),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_12],
            description="Shared utilities (db, llm, sqs, config)",
        )

        # --- SQS Queues ---
        roadmap_queue = sqs.Queue(
            self, "RoadmapQueue",
            queue_name="learnflow-roadmap-queue",
            visibility_timeout=Duration.seconds(300),
        )

        summarizer_queue = sqs.Queue(
            self, "SummarizerQueue",
            queue_name="learnflow-summarizer-queue",
            visibility_timeout=Duration.seconds(300),
        )

        quiz_queue = sqs.Queue(
            self, "QuizQueue",
            queue_name="learnflow-quiz-queue",
            visibility_timeout=Duration.seconds(300),
        )

        weak_topic_queue = sqs.Queue(
            self, "WeakTopicQueue",
            queue_name="learnflow-weak-topic-queue",
            visibility_timeout=Duration.seconds(120),
        )

        email_queue = sqs.Queue(
            self, "EmailQueue",
            queue_name="learnflow-email-queue",
            visibility_timeout=Duration.seconds(60),
        )

        # --- Common environment variables ---
        common_env = {
            "DATABASE_URL": "{{resolve:ssm:/learnflow/database-url}}",
            "HF_API_TOKEN": "{{resolve:ssm:/learnflow/hf-api-token}}",
            "SUPABASE_URL": "{{resolve:ssm:/learnflow/supabase-url}}",
            "SUPABASE_SERVICE_ROLE_KEY": "{{resolve:ssm:/learnflow/supabase-key}}",
            "MAIL_FROM": "{{resolve:ssm:/learnflow/mail-from}}",
            "ROADMAP_QUEUE_URL": roadmap_queue.queue_url,
            "SUMMARIZER_QUEUE_URL": summarizer_queue.queue_url,
            "QUIZ_QUEUE_URL": quiz_queue.queue_url,
            "WEAK_TOPIC_QUEUE_URL": weak_topic_queue.queue_url,
            "EMAIL_QUEUE_URL": email_queue.queue_url,
        }

        # --- Lambda Functions ---

        # Roadmap Generator
        roadmap_fn = _lambda.Function(
            self, "RoadmapGenerator",
            function_name="learnflow-roadmap-generator",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="handler.handler",
            code=_lambda.Code.from_asset("../functions/roadmap_generator"),
            layers=[shared_layer],
            timeout=Duration.seconds(120),
            memory_size=256,
            environment=common_env,
        )
        roadmap_fn.add_event_source(
            event_sources.SqsEventSource(roadmap_queue, batch_size=1)
        )

        # Note Summarizer
        summarizer_fn = _lambda.Function(
            self, "NoteSummarizer",
            function_name="learnflow-note-summarizer",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="handler.handler",
            code=_lambda.Code.from_asset("../functions/note_summarizer"),
            layers=[shared_layer],
            timeout=Duration.seconds(120),
            memory_size=256,
            environment=common_env,
        )
        summarizer_fn.add_event_source(
            event_sources.SqsEventSource(summarizer_queue, batch_size=1)
        )

        # Quiz Generator
        quiz_fn = _lambda.Function(
            self, "QuizGenerator",
            function_name="learnflow-quiz-generator",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="handler.handler",
            code=_lambda.Code.from_asset("../functions/quiz_generator"),
            layers=[shared_layer],
            timeout=Duration.seconds(120),
            memory_size=256,
            environment=common_env,
        )
        quiz_fn.add_event_source(
            event_sources.SqsEventSource(quiz_queue, batch_size=1)
        )

        # Revision Scheduler (daily cron)
        revision_fn = _lambda.Function(
            self, "RevisionScheduler",
            function_name="learnflow-revision-scheduler",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="handler.handler",
            code=_lambda.Code.from_asset("../functions/revision_scheduler"),
            layers=[shared_layer],
            timeout=Duration.seconds(60),
            memory_size=128,
            environment=common_env,
        )
        # Run daily at 6:00 AM IST (00:30 UTC)
        events.Rule(
            self, "RevisionScheduleRule",
            schedule=events.Schedule.cron(hour="0", minute="30"),
            targets=[targets.LambdaFunction(revision_fn)],
        )

        # Weak Topic Analyzer
        weak_topic_fn = _lambda.Function(
            self, "WeakTopicAnalyzer",
            function_name="learnflow-weak-topic-analyzer",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="handler.handler",
            code=_lambda.Code.from_asset("../functions/weak_topic_analyzer"),
            layers=[shared_layer],
            timeout=Duration.seconds(60),
            memory_size=128,
            environment=common_env,
        )
        weak_topic_fn.add_event_source(
            event_sources.SqsEventSource(weak_topic_queue, batch_size=5)
        )

        # Email Sender
        email_fn = _lambda.Function(
            self, "EmailSender",
            function_name="learnflow-email-sender",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="handler.handler",
            code=_lambda.Code.from_asset("../functions/email_sender"),
            layers=[shared_layer],
            timeout=Duration.seconds(30),
            memory_size=128,
            environment=common_env,
        )
        email_fn.add_event_source(
            event_sources.SqsEventSource(email_queue, batch_size=10)
        )

        # Grant SES permissions to email sender
        email_fn.add_to_role_policy(
            iam.PolicyStatement(
                actions=["ses:SendEmail", "ses:SendRawEmail"],
                resources=["*"],
            )
        )
