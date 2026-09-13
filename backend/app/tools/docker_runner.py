import os
import subprocess
from pathlib import Path


def run_tests(root: Path, command: str = "pytest -q") -> dict:
    timeout = int(os.getenv("TEST_TIMEOUT_SECONDS", "60"))

    # The command is intentionally restricted to pytest for this MVP.
    if not isinstance(command, str) or not command.strip().startswith("pytest"):
        command = "pytest -q"

    # On Render, run pytest directly inside the backend container.
    # Locally, use the Docker sandbox.
    cloud_mode = os.getenv("PATCHLOOP_CLOUD", "false").lower() == "true"

    if cloud_mode:
        args = ["sh", "-lc", command]
        cwd = str(root.resolve())
    else:
        args = [
            "docker", "run", "--rm",
            "--network", "none",
            "--cpus", "1",
            "--memory", "1g",
            "--pids-limit", "256",
            "-v", f"{root.resolve()}:/workspace",
            "-w", "/workspace",
            "patchloop-python:3.11",
            "sh", "-lc",
            command,
        ]
        cwd = None

    try:
        p = subprocess.run(
            args,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        return {
            "exit_code": p.returncode,
            "stdout": p.stdout[-20000:],
            "stderr": p.stderr[-20000:],
            "passed": p.returncode == 0,
            "failed": p.returncode != 0,
            "duration": None,
        }

    except subprocess.TimeoutExpired as e:
        return {
            "exit_code": 124,
            "stdout": (e.stdout or "")[-10000:]
            if isinstance(e.stdout, str)
            else "",
            "stderr": "TEST TIMEOUT",
            "passed": False,
            "failed": True,
            "duration": timeout,
        }