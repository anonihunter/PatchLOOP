import os
import shutil
import subprocess
from pathlib import Path
from git import Repo

IGNORE = {".git", ".venv", "venv", "__pycache__", "node_modules", ".next", "dist", "build"}

def clone_repository(url: str, destination: Path, branch: str | None = None):
    if destination.exists():
        shutil.rmtree(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    kwargs = {}
    if branch:
        kwargs["branch"] = branch
    Repo.clone_from(url, destination, **kwargs)

def _files(root: Path):
    out = []
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        if any(part in IGNORE for part in p.relative_to(root).parts):
            continue
        try:
            rel = str(p.relative_to(root))
            if p.stat().st_size <= 500_000:
                out.append(rel)
        except OSError:
            pass
    return sorted(out)[:1500]

def inspect_repository(root: Path) -> dict:
    files = _files(root)
    important = []
    for name in files:
        low = name.lower()
        if (
            name.endswith(".py")
            or "test" in low
            or name in {"README.md", "pyproject.toml", "requirements.txt", "setup.py", "pytest.ini"}
        ):
            important.append(name)
    return {
        "files": files,
        "candidate_files": important[:300],
    }

def read_file(root: Path, relative: str, max_chars: int = 30000) -> str:
    p = (root / relative).resolve()
    if root.resolve() not in p.parents:
        raise ValueError("Path escapes workspace")
    return p.read_text(errors="replace")[:max_chars]

def write_file(root: Path, relative: str, content: str):
    p = (root / relative).resolve()
    if root.resolve() not in p.parents:
        raise ValueError("Path escapes workspace")
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)

def git_diff(root: Path) -> str:
    p = subprocess.run(
        ["git", "-C", str(root), "diff", "--", "."],
        capture_output=True, text=True, timeout=30
    )
    return p.stdout[:100000]

def reset_workspace(root: Path):
    subprocess.run(["git", "-C", str(root), "reset", "--hard", "HEAD"], capture_output=True, text=True, timeout=30)
    subprocess.run(["git", "-C", str(root), "clean", "-fd"], capture_output=True, text=True, timeout=30)
