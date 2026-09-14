# PatchLoop

## Adaptive Software Maintenance Agent

> **Issue → Understand → Diagnose → Plan → Implement → Test → Failure Analysis → Adapt → Retry → Verify → Result**

PatchLoop is an AI-powered software maintenance agent that autonomously attempts to fix issues in GitHub repositories.

Unlike a basic coding agent that stops when its first fix fails, PatchLoop follows an **adaptive repair loop**: it uses concrete test failure evidence to change its strategy, retry the repair, and independently verify the result.

---

## 🚀 Live Demo

<<<<<<< HEAD
**Frontend:** [https://patch-loop.vercel.app](https://patch-loop.vercel.app/)  
**Backend API:** [https://patchloop.onrender.com  ](https://patchloop.onrender.com/)
**Health Check:** [https://patchloop.onrender.com/api/health](https://patchloop.onrender.com/api/health)
=======
**Frontend:** https://patch-loop.vercel.app  
**Backend API:** https://patchloop.onrender.com  
**Health Check:** https://patchloop.onrender.com/api/health
>>>>>>> 2e138b7 (Readme File Updated)

---

## 💡 Why PatchLoop?

Traditional automated repair often looks like:

```text
Issue → Generate Fix → Run Tests → Done / Failed
```

PatchLoop treats failure as **feedback**:

```text
                 GitHub Issue
                      ↓
                 Understand
                      ↓
                   Diagnose
                      ↓
                     Plan
                      ↓
                  Implement
                      ↓
                    Test
                 ↙         ↘
              PASS          FAIL
                ↓             ↓
             Verify     Failure Analysis
                ↓             ↓
             Result          Adapt
                              ↓
                            Retry
                              │
                              └──→ Test
```

> **PatchLoop doesn't just retry. It uses actual test failure evidence to adapt its repair strategy.**

---

## ✨ Features

- 🤖 AI-powered repository analysis and issue diagnosis
- 📝 Automatic repair planning
- 🛠️ Autonomous code modification
- 🧪 Automated pytest execution
- 🔴 Concrete test-failure analysis
- 🧠 Adaptive retry strategy
- 🔄 Multiple repair attempts
- ✅ Independent final verification
- 📜 Auditable attempt history
- 🌿 Optional Git branch support
- 🐳 Docker-based local test isolation
- 🌐 Live Vercel + Render deployment

---

## 🧠 Adaptive Repair Example

Suppose a repository contains:

```python
def calculate_average(numbers):
    return sum(numbers) / len(numbers)
```

The issue requires `calculate_average([])` to return `0`.

A repair attempt may initially fail:

```text
FAILED test_calculate_average_empty

ZeroDivisionError: division by zero
```

PatchLoop converts that failure into new information:

```text
Failure
   ↓
ZeroDivisionError
   ↓
Empty-list case is not handled
   ↓
Adapt strategy
   ↓
Retry implementation
   ↓
Run tests again
   ↓
Verify
```

The core behavior is:

```text
FAILURE → EVIDENCE → ADAPTATION → RETRY → SUCCESS
```

---

## 🏗️ Architecture

```text
┌───────────────────────────────┐
│           Frontend            │
│        Next.js / Vercel       │
└───────────────┬───────────────┘
                │ HTTP API
                ↓
┌───────────────────────────────┐
│           Backend             │
│        FastAPI / Render       │
└───────────────┬───────────────┘
                │
       ┌────────┼────────┐
       ↓        ↓        ↓
    GitHub     LLM     Test Runner
     API     OpenRouter   pytest
                         │
                         ↓
                    Docker Sandbox
```

| Component | Technology |
|---|---|
| Frontend | Next.js |
| Frontend Hosting | Vercel |
| Backend | FastAPI |
| Backend Hosting | Render |
| LLM | OpenRouter / OpenAI-compatible API |
| Repository Access | Git + GitHub API |
| Test Framework | pytest |
| Local Isolation | Docker |
| Languages | Python / JavaScript |

---

## 📁 Project Structure

```text
PatchLOOP/
├── backend/
│   ├── app/
│   │   ├── agent/
│   │   │   ├── state.py
│   │   │   ├── llm.py
│   │   │   └── orchestrator.py
│   │   ├── tools/
│   │   │   ├── github.py
│   │   │   ├── repository.py
│   │   │   └── docker_runner.py
│   │   └── main.py
│   ├── Dockerfile
│   ├── Dockerfile.sandbox
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── app/
│   │   ├── page.js
│   │   └── globals.css
│   ├── package.json
│   └── ...
└── README.md
```

---

## ⚙️ Requirements

For local development:

- Python 3.11+
- Node.js 20+
- Git
- Docker
- OpenRouter (or another OpenAI-compatible) LLM API key
- GitHub token

---

## 🖥️ Local Setup

### 1. Clone

```bash
git clone https://github.com/anonihunter/PatchLOOP.git
cd PatchLOOP
```

### 2. Backend

```bash
cd backend
python -m venv .venv
```

**Windows**
```powershell
.venv\Scripts\activate
```

**macOS / Linux**
```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create `.env` from `.env.example` and configure:

```env
LLM_API_KEY=your_key
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_MODEL=openrouter/free

GITHUB_TOKEN=your_github_token

MAX_ATTEMPTS=3
TEST_TIMEOUT_SECONDS=60
WORK_ROOT=./workspaces

DEMO_ADAPTIVE_FAILURE=true
PATCHLOOP_CLOUD=false
```

Start the backend:

```bash
uvicorn app.main:app --port 8000
```

> **MVP note:** Do not use `--reload`. Repository workspace changes can trigger reloads and reset in-memory job state.

Backend: `http://localhost:8000`  
API docs: `http://localhost:8000/docs`

### 3. Frontend

In another terminal:

```bash
cd frontend
npm install
```

Create `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

Start:

```bash
npm run dev
```

Open `http://localhost:3000`.

---

## 🐳 Docker Test Sandbox

Local test execution uses a Docker sandbox.

Build it:

```bash
cd backend
docker build -f Dockerfile.sandbox -t patchloop-python:3.11 .
```

Verify pytest:

```bash
docker run --rm patchloop-python:3.11 pytest --version
```

PatchLoop runs repository tests with:

```bash
pytest -q
```

and applies CPU, memory, process, and network restrictions in local Docker execution.

> **Security note:** This is a hackathon MVP, not a hardened production sandbox. Do not run untrusted repositories on a machine containing sensitive secrets. A production version should use stronger isolation and dedicated workers/VMs.

---

## 🎬 Demo

Enter:

- GitHub repository URL
- Issue number or issue description
- Optional branch

PatchLoop then executes:

```text
Clone → Understand → Diagnose → Plan → Implement
                         ↓
                       Test
                         ↓
                Analyze Result
                    ↙       ↘
                 Pass       Fail
                  ↓           ↓
               Verify      Adapt
                  ↓           ↓
               Result      Retry
```

The UI shows the current phase, attempt number, test output, failure evidence, adaptation strategy, changes, verification, and final outcome.

### Recommended Demo

Use a small repository containing `calculator.py` and `test_calculator.py` with an issue such as:

```text
Fix calculate_average for empty lists.

The calculate_average function should return 0
when given an empty list.

For non-empty lists, it should return the
arithmetic average.

Make sure the existing test suite passes.
```

The strongest demonstration is:

```text
ATTEMPT 1
   ↓
Tests FAIL
   ↓
Failure Analysis
   ↓
Adaptation
   ↓
ATTEMPT 2
   ↓
Tests PASS
   ↓
Verification PASS
   ↓
RESOLVED
```

---

## 📊 Example Result

```text
Attempts:       2
Tests:          PASSED
Verification:   PASSED
Final Status:   RESOLVED
```

Example repair:

```diff
 def calculate_average(numbers):
+    if not numbers:
+        return 0
     return sum(numbers) / len(numbers)
```

---

## 🔐 Environment Variables

| Variable | Purpose |
|---|---|
| `LLM_API_KEY` | LLM provider API key |
| `LLM_BASE_URL` | OpenAI-compatible API endpoint |
| `LLM_MODEL` | Model used by PatchLoop |
| `GITHUB_TOKEN` | GitHub API access |
| `MAX_ATTEMPTS` | Maximum repair attempts |
| `TEST_TIMEOUT_SECONDS` | Test execution timeout |
| `WORK_ROOT` | Workspace directory |
| `DEMO_ADAPTIVE_FAILURE` | Enables the hackathon adaptive-failure demo |
| `PATCHLOOP_CLOUD` | Enables cloud execution mode |

**Never commit `.env` or API keys to GitHub.**

---

## 🌐 Deployment

PatchLoop uses:

```text
Frontend → Vercel
Backend  → Render
```

Frontend environment:

```env
NEXT_PUBLIC_API_URL=https://patchloop.onrender.com
```

The live deployment is:

<<<<<<< HEAD
- **UI:** [https://patch-loop.vercel.app](https://patch-loop.vercel.app/)
- **API:** [https://patchloop.onrender.com](https://patchloop.onrender.com/)
=======
- **UI:** https://patch-loop.vercel.app
- **API:** https://patchloop.onrender.com
>>>>>>> 2e138b7 (Readme File Updated)

---

## 🎯 Hackathon Problem

Software maintenance is more than generating code. An effective repair process must:

1. Understand an existing codebase
2. Identify the likely root cause
3. Make a targeted change
4. Run tests
5. Interpret failures
6. Change the approach when the first repair is wrong
7. Verify the final repair

PatchLoop focuses on this **closed-loop maintenance process**.

### Agentic Flow

| Stage | PatchLoop |
|---|---|
| Goal | Resolve the software issue |
| Decision | Determine what should change |
| Action | Modify the repository |
| Intermediate Result | Execute tests |
| Adaptation | Learn from failure evidence |
| Retry | Attempt another repair |
| Verification | Independently confirm success |
| Final Outcome | Return an auditable result |

---

## 🚧 MVP Limitations

PatchLoop is intentionally a hackathon MVP.

- Python/pytest-focused testing
- Limited language support
- In-memory job state
- No authentication or persistent database
- Cloud tests run inside the backend container
- Limited sandbox hardening
- Free/limited LLM models may have rate limits
- Complex repositories may require additional dependency handling

These trade-offs keep the focus on the adaptive repair loop.

---

## 🔮 Future Improvements

- Multi-language repository support
- Stronger sandbox isolation
- Persistent repair history
- Automatic GitHub Pull Request creation
- Automatic branch creation
- Human approval checkpoints
- Better patch minimization
- Repository-aware test selection
- Larger repair benchmarks
- Multi-agent diagnosis and review
- Cost and success-rate optimization

---

## 👥 Project

**PatchLoop — Adaptive Software Maintenance Agent**

GitHub: https://github.com/anonihunter/PatchLOOP  
<<<<<<< HEAD
Live Demo: [https://patch-loop.vercel.app](https://patch-loop.vercel.app/)
=======
Live Demo: https://patch-loop.vercel.app
>>>>>>> 2e138b7 (Readme File Updated)

### ⭐ One-Line Pitch

> **PatchLoop is an adaptive software maintenance agent that doesn't just retry failed fixes — it learns from test failures, changes its strategy, and verifies the repair.**
