# LearnFlow Lambda Functions

Serverless workloads for LearnFlow, deployed on AWS Lambda.

## Architecture

```
learnflow-lambdas/
├── functions/
│   ├── ai_processor/       # All AI/LLM tasks (roadmap, summarizer, quiz)
│   └── task_processor/     # Utility tasks (email, weak topics, revision scheduler)
├── shared/                 # Shared Python utilities (db, llm, sqs, config)
├── infra/                  # AWS CDK infrastructure
├── .env                    # Environment variables
├── requirements.txt        # All dependencies
└── redeploy.sh             # Deployment script
```

## Functions

| Function | Queue | Trigger | Actions |
|----------|-------|---------|---------|
| ai_processor | learnflow-ai-queue | SQS | generate_roadmap, summarize_note, generate_quiz |
| task_processor | learnflow-task-queue | SQS + EventBridge cron | send_email, analyze_weak_topics, schedule_revisions |

## Deploy

```bash
source .venv/bin/activate
cd infra
cdk deploy --all --profile learnflow
```

## Quick Redeploy

```bash
./redeploy.sh ai       # Redeploy AI processor only
./redeploy.sh task     # Redeploy Task processor only
./redeploy.sh          # Full CDK deploy
```
