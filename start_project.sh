#!/bin/bash

# LearnFlow — Start Project (separate tabs, fully independent)
# Usage: ./start_project.sh

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/learnflow-backend"
FRONTEND_DIR="$PROJECT_ROOT/learnflow-frontend"

# Launch frontend tab (runs regardless of backend status)
gnome-terminal --tab --title="Frontend" -- bash -c "
cd $FRONTEND_DIR
echo '🚀 Frontend → http://localhost:5173'
echo ''
npm run dev
exec bash
"

# Launch backend tab (runs regardless of frontend status)
gnome-terminal --tab --title="Backend" -- bash -c "
cd $BACKEND_DIR
source venv/bin/activate
echo '🚀 Backend → http://localhost:8000'
echo ''
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
exec bash
"

echo "✅ Both tabs opened — Backend & Frontend run independently"
