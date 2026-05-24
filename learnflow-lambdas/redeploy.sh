#!/bin/bash

# ═══════════════════════════════════════════════════════════════════════════════
# LearnFlow Lambda Redeployment Script
# ═══════════════════════════════════════════════════════════════════════════════
#
# Usage:
#   ./redeploy.sh          → Redeploy all via CDK
#   ./redeploy.sh ai       → Quick redeploy AI processor only
#   ./redeploy.sh task     → Quick redeploy Task processor only
#
# ═══════════════════════════════════════════════════════════════════════════════

set -e

# ─── Configuration (edit these as needed) ──────────────────────────────────────

# AWS
PROFILE="learnflow"
REGION="ap-south-1"

# Lambda Function Names (rename here if needed)
AI_FUNCTION_NAME="learnflow-ai-processor"
TASK_FUNCTION_NAME="learnflow-task-processor"

# Paths
LAMBDA_ROOT="$(cd "$(dirname "$0")" && pwd)"
BACKEND_ROOT="$(dirname "$LAMBDA_ROOT")/learnflow-backend"

# Function directories
AI_DIR="functions/ai_processor"
TASK_DIR="functions/task_processor"

# ─── Colors ────────────────────────────────────────────────────────────────────

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

# ─── Helper Functions ──────────────────────────────────────────────────────────

print_config() {
    echo -e "${CYAN}Configuration:${NC}"
    echo "  Profile:        $PROFILE"
    echo "  Region:         $REGION"
    echo "  Lambda Root:    $LAMBDA_ROOT"
    echo "  Backend Root:   $BACKEND_ROOT"
    echo "  AI Function:    $AI_FUNCTION_NAME"
    echo "  Task Function:  $TASK_FUNCTION_NAME"
    echo ""
}

deploy_function() {
    local func_name=$1
    local func_dir=$2

    echo -e "${YELLOW}📦 Packaging ${func_name}...${NC}"

    cd "$LAMBDA_ROOT"

    # Create zip with function code + shared module
    rm -f /tmp/lambda-deploy.zip
    cd "$func_dir"
    zip -r /tmp/lambda-deploy.zip . -x "*.pyc" "__pycache__/*" > /dev/null
    cd "$LAMBDA_ROOT"
    zip -r /tmp/lambda-deploy.zip shared/ -x "*.pyc" "__pycache__/*" > /dev/null

    echo -e "${YELLOW}⬆️  Deploying ${func_name}...${NC}"
    aws lambda update-function-code \
        --function-name "$func_name" \
        --zip-file fileb:///tmp/lambda-deploy.zip \
        --profile "$PROFILE" \
        --region "$REGION" \
        --no-cli-pager > /dev/null

    rm -f /tmp/lambda-deploy.zip
    echo -e "${GREEN}✅ ${func_name} deployed successfully${NC}"
}

# ─── Main ──────────────────────────────────────────────────────────────────────

echo ""
echo -e "${YELLOW}🚀 LearnFlow Lambda Redeployment${NC}"
echo "═══════════════════════════════════════"
print_config

case "${1:-all}" in
    ai)
        deploy_function "$AI_FUNCTION_NAME" "$AI_DIR"
        ;;
    task)
        deploy_function "$TASK_FUNCTION_NAME" "$TASK_DIR"
        ;;
    all)
        echo -e "${YELLOW}📦 Deploying all via CDK...${NC}"
        cd "$LAMBDA_ROOT/infra"
        cdk deploy --all --profile "$PROFILE" --require-approval never
        cd "$LAMBDA_ROOT"
        echo -e "${GREEN}✅ All deployed via CDK${NC}"
        ;;
    config)
        echo "Done."
        ;;
    *)
        echo -e "${RED}❌ Unknown target: $1${NC}"
        echo ""
        echo "Usage: ./redeploy.sh [ai|task|all|config]"
        echo "  ai     - Quick redeploy AI processor"
        echo "  task   - Quick redeploy Task processor"
        echo "  all    - Full CDK deploy (default)"
        echo "  config - Show configuration only"
        exit 1
        ;;
esac

echo "═══════════════════════════════════════"
echo -e "${GREEN}Done!${NC}"
echo ""
