# LearnFlow Lambda Functions

Serverless AI workloads for LearnFlow, deployed on AWS Lambda.

## Architecture

```
learnflow-lambdas/
├── infra/                  # AWS CDK infrastructure
├── layers/                 # Shared Lambda layers (common deps)
├── functions/              # Individual Lambda functions
│   ├── roadmap_generator/
│   ├── note_summarizer/
│   ├── quiz_generator/
│   ├── revision_scheduler/
│   ├── weak_topic_analyzer/
│   └── email_sender/
└── shared/                 # Shared Python utilities across functions
```

## Functions

| Function | Trigger | Purpose |
|----------|---------|---------|
| roadmap_generator | SQS | Calls Mistral LLM to generate personalized roadmaps |
| note_summarizer | SQS | Summarizes notes/PDFs into key points, flashcards, MCQs |
| quiz_generator | SQS | Generates topic-aware quizzes via LLM |
| revision_scheduler | EventBridge (cron) | Daily job to calculate spaced repetition schedule |
| weak_topic_analyzer | SQS | Analyzes quiz/revision data to detect weak topics |
| email_sender | SQS | Sends transactional emails (OTP, notifications) |

## Deploy

```bash
cd infra
pip install -r requirements.txt
cdk deploy --all
```
