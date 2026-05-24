#!/bin/bash

# LearnFlow Lambda Redeployment Script
# Usage:
#   ./redeploy.sh              → Redeploy all Lambda functions
#   ./redeploy.sh roadmap      → Redeploy only roadmap_generator
#   ./redeploy.sh summarizer   → Redeploy only note_summarizer
#   ./redeploy.sh quiz         → Redeploy only quiz_generator
#   ./redeploy.sh revision     → Redeploy only revision_scheduler
#   ./redeploy.sh weak         → Redeploy only weak_topic_analyzer
#   ./redeploy.sh email        → Redeploy only email_sender

set -e

PROFILE="learnflow"
REGION="ap-south-1"

# Function name mapping
declare -A FUNCTIONS=(
    [roadmap]="learnflow-roadmap-generator"
    [summarizer]="learnflow-note-summarizer"
    [quiz]="learnflow-quiz-generator"
    [revision]="learnflow-revision-scheduler"
    [weak]="learnflow-weak-topic-analyzer"
    [email]="learnflow-email-sender"
)

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}🚀 LearnFlow Lambda Redeployment${NC}"
echo "-----------------------------------"

# If specific function requested
if [ -n "$1" ]; then
    FUNC_NAME="${FUNCTIONS[$1]}"

    if [ -z "$FUNC_NAME" ]; then
        echo -e "${RED}❌ Unknown function: $1${NC}"
        echo "Available: roadmap, summarizer, quiz, revision, weak, email"
        exit 1
    fi

    echo -e "${YELLOW}📦 Packaging $1...${NC}"

    # Package the function code
    FUNC_DIR="functions/${1/roadmap/roadmap_generator}"
    FUNC_DIR="${FUNC_DIR/summarizer/note_summarizer}"
    FUNC_DIR="${FUNC_DIR/quiz/quiz_generator}"
    FUNC_DIR="${FUNC_DIR/revision/revision_scheduler}"
    FUNC_DIR="${FUNC_DIR/weak/weak_topic_analyzer}"
    FUNC_DIR="${FUNC_DIR/email/email_sender}"

    # Create temp zip
    cd "$FUNC_DIR"
    zip -r /tmp/lambda-deploy.zip . -x "*.pyc" "__pycache__/*"
    cd - > /dev/null

    # Include shared module
    zip -r /tmp/lambda-deploy.zip shared/ -x "*.pyc" "__pycache__/*"

    echo -e "${YELLOW}⬆️  Deploying ${FUNC_NAME}...${NC}"
    aws lambda update-function-code \
        --function-name "$FUNC_NAME" \
        --zip-file fileb:///tmp/lambda-deploy.zip \
        --profile "$PROFILE" \
        --region "$REGION" \
        --no-cli-pager

    rm /tmp/lambda-deploy.zip
    echo -e "${GREEN}✅ $FUNC_NAME deployed successfully${NC}"

else
    # Deploy all via CDK
    echo -e "${YELLOW}📦 Deploying all functions via CDK...${NC}"
    cd infra
    cdk deploy --all --profile "$PROFILE" --require-approval never
    cd ..
    echo -e "${GREEN}✅ All Lambda functions deployed successfully${NC}"
fi

echo "-----------------------------------"
echo -e "${GREEN}Done!${NC}"
