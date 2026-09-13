import asyncio
import json
import os
import uuid
from pathlib import Path

from app.agent.state import AgentState, Phase, Attempt
from app.agent.llm import LLM, LLMError
from app.tools.github import get_issue
from app.tools.repository import (
    clone_repository, inspect_repository, read_file, write_file,
    git_diff, reset_workspace
)
from app.tools.docker_runner import run_tests

MAX_ATTEMPTS = int(os.getenv("MAX_ATTEMPTS", "3"))
WORK_ROOT = Path(os.getenv("WORK_ROOT", "./workspaces")).resolve()

SYSTEM = """You are PatchLoop, an adaptive software maintenance engineer.
You work only on a Python repository and must make minimal, evidence-driven changes.
Never invent files or test results. Use the supplied repository snapshot.
When a test fails, treat the concrete failure output as evidence and change the
hypothesis/strategy rather than blindly repeating the same patch.

Return JSON when requested. Code edits must be represented as complete file content.
"""

class AgentOrchestrator:
    def __init__(self):
        self.job_id = str(uuid.uuid4())
        self.state = AgentState(job_id=self.job_id)
        self.root: Path | None = None
        self.llm = LLM()

    def public_state(self):
        return self.state.model_dump(mode="json")

    async def run(self, repo_url: str, issue: str, branch: str | None):
        self.state.repo_url = repo_url
        self.state.issue = issue
        self.state.branch = branch
        try:
            await self._run()
        except Exception as e:
            self.state.final_status = "failed"
            self.state.final_evidence = {"error": str(e)}
            self.state.log(Phase.FINAL_RESULT, "Agent stopped with an error.", {"error": str(e)})

    async def _run(self):
        self.state.log(Phase.RECEIVED, "Issue received.")
        self.root = WORK_ROOT / self.job_id
        self.root.parent.mkdir(parents=True, exist_ok=True)

        self.state.log(Phase.REPOSITORY_ANALYSIS, "Cloning repository.")
        clone_repository(self.state.repo_url, self.root, self.state.branch)
        context = inspect_repository(self.root)
        self.state.repository_context = context
        self.state.log(
            Phase.REPOSITORY_ANALYSIS,
            f"Repository inspected: {len(context['files'])} files.",
            {"candidate_files": context["candidate_files"][:50]},
        )

        issue_data = await get_issue(self.state.repo_url, self.state.issue)
        issue_text = f"Title: {issue_data.get('title','')}\nBody:\n{issue_data.get('body','')}"
        if self.state.issue and not issue_data.get("number"):
            issue_text = self.state.issue

        # Read likely project files for the initial model context.
        snippets = {}
        for name in context["candidate_files"][:30]:
            try:
                snippets[name] = read_file(self.root, name, 12000)
            except Exception:
                pass

        self.state.log(Phase.ISSUE_DIAGNOSIS, "Diagnosing issue from repository and issue text.")
        diagnosis = await self.llm.json(
            SYSTEM + "\nReturn keys: hypothesis, relevant_files, test_command.",
            json.dumps({
                "issue": issue_text,
                "repository_files": context["candidate_files"][:200],
                "file_snippets": snippets,
            }),
        )
        self.state.issue_analysis = diagnosis.get("hypothesis", "")
        self.state.test_command = "pytest -q"
        relevant = diagnosis.get("relevant_files", [])
        self.state.log(
            Phase.ISSUE_DIAGNOSIS,
            self.state.issue_analysis,
            {"relevant_files": relevant, "test_command": self.state.test_command},
        )

        self.state.log(Phase.PLANNING, "Creating repair plan.")
        plan = await self.llm.json(
            SYSTEM + "\nReturn keys: plan, files_to_change, tests_to_run.",
            json.dumps({
                "issue": issue_text,
                "hypothesis": self.state.issue_analysis,
                "relevant_files": relevant,
                "repository_files": context["candidate_files"][:250],
                "snippets": {k: snippets[k] for k in relevant if k in snippets},
            }),
        )
        self.state.plan = plan.get("plan", "")
        self.state.test_command = "pytest -q"
        self.state.log(Phase.PLANNING, self.state.plan, {"files_to_change": plan.get("files_to_change", [])})

        for attempt_no in range(1, MAX_ATTEMPTS + 1):
            self.state.attempt_number = attempt_no
            attempt = Attempt(number=attempt_no, hypothesis=self.state.issue_analysis, plan=self.state.plan)
            self.state.attempt_history.append(attempt)

            self.state.log(Phase.IMPLEMENTATION, f"Starting implementation attempt {attempt_no}.")
            await self._implement(attempt, issue_text)

            # ---------------------------------------------------------
            # DEMO MODE: intentionally introduce a controlled bad patch
            # on Attempt 1 so the adaptive loop can be demonstrated.
            # Disabled by default.
            # ---------------------------------------------------------
            if (
                attempt_no == 1
                and os.getenv("DEMO_ADAPTIVE_FAILURE", "false").lower() == "true"
            ):
                self._inject_demo_failure()

            diff = git_diff(self.root)
            attempt.diff = diff
            self.state.log(Phase.IMPLEMENTATION, "Patch applied.", {"diff": diff[-12000:]})

            self.state.log(Phase.TESTING, f"Running tests for attempt {attempt_no}.")
            result = await asyncio.to_thread(run_tests, self.root, self.state.test_command)
            attempt.test_result = result
            self.state.log(Phase.TESTING, "Tests completed.", result)

            if result["passed"]:
                self.state.log(Phase.VERIFICATION, "Targeted test command passed. Running verification.")
                verify = await asyncio.to_thread(run_tests, self.root, "pytest -q")
                attempt.test_result["verification"] = verify
                if verify["passed"]:
                    self.state.final_status = "resolved"
                    self.state.final_evidence = {
                        "attempts": attempt_no,
                        "tests": "passed",
                        "verification": "passed",
                        "diff": git_diff(self.root),
                    }
                    self.state.log(Phase.FINAL_RESULT, "Issue resolved and verified.", self.state.final_evidence)
                    return
                result = verify

            if attempt_no == MAX_ATTEMPTS:
                break

            self.state.log(Phase.FAILURE_ANALYSIS, "Analyzing failure evidence.")
            failure = await self.llm.json(
                SYSTEM + "\nReturn keys: failure_analysis, new_hypothesis, adaptation_strategy.",
                json.dumps({
                    "issue": issue_text,
                    "original_hypothesis": attempt.hypothesis,
                    "plan": attempt.plan,
                    "attempt": attempt_no,
                    "test_result": result,
                    "diff": attempt.diff[-20000:],
                }),
            )
            attempt.failure_analysis = failure.get("failure_analysis", "")
            attempt.adaptation_strategy = failure.get("adaptation_strategy", "")
            self.state.issue_analysis = failure.get("new_hypothesis") or self.state.issue_analysis
            self.state.log(
                Phase.FAILURE_ANALYSIS,
                attempt.failure_analysis,
                {"new_hypothesis": self.state.issue_analysis},
            )
            self.state.log(Phase.ADAPTATION, attempt.adaptation_strategy)
            reset_workspace(self.root)
            self.state.log(Phase.RETRY, f"Reset workspace and preparing attempt {attempt_no + 1}.")

        self.state.final_status = "unresolved"
        self.state.final_evidence = {
            "attempts": MAX_ATTEMPTS,
            "message": "Maximum attempts reached without verified resolution.",
            "last_diff": git_diff(self.root) if self.root else "",
        }
        self.state.log(Phase.FINAL_RESULT, "Issue could not be verified within the attempt limit.")

    async def _implement(self, attempt: Attempt, issue_text: str):
        # Give the model the current repository tree plus selected source files.
        context = self.state.repository_context
        candidates = context.get("candidate_files", [])[:80]
        source = {}
        for name in candidates:
            try:
                source[name] = read_file(self.root, name, 16000)
            except Exception:
                pass

        adaptation = ""
        if attempt.number > 1:
            prev = self.state.attempt_history[-2]
            adaptation = (
                f"Previous failure analysis:\n{prev.failure_analysis}\n"
                f"Previous adaptation:\n{prev.adaptation_strategy}\n"
                f"New hypothesis:\n{self.state.issue_analysis}\n"
            )

        response = await self.llm.json(
            SYSTEM + """
You are implementing a repair. Return:
{
  "actions": ["..."],
  "edits": [{"file": "relative/path.py", "content": "COMPLETE FILE CONTENT"}],
  "test_command": "pytest ..."
}
Only edit files necessary for the issue. Never use absolute paths.
Do not include markdown fences around JSON.
""",
            json.dumps({
                "issue": issue_text,
                "hypothesis": self.state.issue_analysis,
                "plan": self.state.plan,
                "attempt": attempt.number,
                "adaptation_context": adaptation,
                "repository_files": candidates,
                "source_files": source,
            }),
        )
        edits = response.get("edits", [])
        for edit in edits:
            path = edit.get("file")
            content = edit.get("content")
            if not path or not isinstance(content, str):
                continue
            write_file(self.root, path, content)
            attempt.actions.append(f"Modified {path}")
        self.state.test_command = "pytest -q"
        attempt.actions.extend(response.get("actions", []))

    def _inject_demo_failure(self):
        """
        Hackathon demo only.

        After the LLM creates a valid patch on Attempt 1,
        deliberately introduce a small regression so that
        the real test runner produces concrete failure evidence.

        Attempt 2 then receives that failure evidence and adapts.
        """

        calculator = self.root / "calculator.py"

        if not calculator.exists():
            return

        content = calculator.read_text(encoding="utf-8")

        # Only inject the fault if the expected repair exists.
        if "if not numbers:" in content and "return 0" in content:
            broken = content.replace(
                "if not numbers:\n        return 0",
                "if numbers:\n        return 0",
                1,
            )

            calculator.write_text(broken, encoding="utf-8")

            self.state.log(
                Phase.IMPLEMENTATION,
                "DEMO: Controlled regression injected for adaptive-loop demonstration.",
                {"reason": "Force Attempt 1 to produce real test failure evidence."},
            )