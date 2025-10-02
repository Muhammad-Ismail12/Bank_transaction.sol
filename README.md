# Doctor Appointment AI Agent (Python + OpenAI)

## Prerequisites
- Python 3.13+
- OpenAI API key

## Setup
1. Install dependencies:
```bash
python3 -m pip install --user -r requirements.txt
```
2. Set your environment variable:
```bash
export OPENAI_API_KEY="sk-..."
```

## Run
```bash
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## API
- POST `/api/chat` to converse with the agent.
- GET `/health` for health check.

## Notes
- This demo uses in-memory storage for appointments. Replace with your DB.