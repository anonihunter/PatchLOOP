from enum import Enum
from typing import Any
from pydantic import BaseModel, Field

class Phase(str, Enum):
    RECEIVED = "RECEIVED"
    REPOSITORY_ANALYSIS = "REPOSITORY_ANALYSIS"
    ISSUE_DIAGNOSIS = "ISSUE_DIAGNOSIS"
    PLANNING = "PLANNING"
    IMPLEMENTATION = "IMPLEMENTATION"
    TESTING = "TESTING"
    FAILURE_ANALYSIS = "FAILURE_ANALYSIS"
    ADAPTATION = "ADAPTATION"
    RETRY = "RETRY"
    VERIFICATION = "VERIFICATION"
    FINAL_RESULT = "FINAL_RESULT"

class Attempt(BaseModel):
    number: int
    hypothesis: str = ""
    plan: str = ""
    actions: list[str] = Field(default_factory=list)
    test_command: str = ""
    test_result: dict[str, Any] = Field(default_factory=dict)
    failure_analysis: str = ""
    adaptation_strategy: str = ""
    diff: str = ""

class AgentState(BaseModel):
    job_id: str
    repo_url: str = ""
    branch: str | None = None
    issue: str = ""
    phase: Phase = Phase.RECEIVED
    attempt_number: int = 0
    repository_context: dict[str, Any] = Field(default_factory=dict)
    issue_analysis: str = ""
    plan: str = ""
    test_command: str = "pytest -q"
    attempt_history: list[Attempt] = Field(default_factory=list)
    final_status: str = "running"
    final_evidence: dict[str, Any] = Field(default_factory=dict)
    logs: list[dict[str, Any]] = Field(default_factory=list)

    def log(self, phase: Phase, message: str, data: dict[str, Any] | None = None):
        self.phase = phase
        self.logs.append({
            "phase": phase.value,
            "message": message,
            "data": data or {},
        })
