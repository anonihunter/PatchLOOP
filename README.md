# PatchLoop

Adaptive software maintenance agent MVP.

Flow:
Issue -> Understand -> Diagnose -> Plan -> Implement -> Test -> Failure Analysis -> Adapt -> Retry -> Verify -> Result

## Requirements

- Python 3.11+
- Node.js 20+
- Docker
- Git
- An OpenAI-compatible LLM API key

## 1. Backend

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
# source .venv/bin/activate

pip install -r requirements.txt
copy .env.example .env   # Windows
# cp .env.example .env   # macOS/Linux

uvicorn app.main:app --reload --port 8000
```

Edit `.env`:

```env
LLM_API_KEY=your_key
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4.1-mini
MAX_ATTEMPTS=3
```

## 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000

## 3. Docker

PatchLoop runs repository tests in an isolated Docker container. The host workspace is mounted into the container read/write. Do NOT use this MVP with untrusted repositories on a machine containing secrets. For a real deployment, use a hardened isolated worker/VM with network disabled, stronger resource limits, and secret isolation.

## Demo

Use a small Python/pytest repository with a reproducible issue.

Enter:
- GitHub repository URL
- issue number or issue description

The backend clones the repo, analyzes it, plans a fix, edits files, runs pytest in Docker, analyzes failures, resets between attempts, and produces an auditable attempt history.
