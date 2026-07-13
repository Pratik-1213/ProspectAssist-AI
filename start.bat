@echo off
echo Starting ProspectAssist-AI Backend...
start cmd /k "cd backend && call venv\Scripts\activate && uvicorn main:app --host 0.0.0.0 --port 8000"

echo Starting ProspectAssist-AI Frontend...
start cmd /k "cd frontend && npm run dev"

echo Both services started!
