import os
import httpx

def github_headers():
    token = os.getenv("GITHUB_TOKEN")
    h = {"Accept": "application/vnd.github+json"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h

def parse_repo(url: str):
    clean = url.rstrip("/").removesuffix(".git")
    parts = clean.split("/")
    if len(parts) < 2:
        raise ValueError("Invalid GitHub repository URL")
    return parts[-2], parts[-1]

async def get_issue(repo_url: str, issue: str) -> dict:
    owner, repo = parse_repo(repo_url)
    number = issue.strip().lstrip("#")
    if not number.isdigit():
        return {"title": "Provided issue", "body": issue, "number": None}
    url = f"https://api.github.com/repos/{owner}/{repo}/issues/{number}"
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.get(url, headers=github_headers())
        if r.status_code >= 400:
            raise RuntimeError(f"GitHub issue fetch failed: {r.status_code} {r.text[:500]}")
        d = r.json()
        return {"title": d.get("title", ""), "body": d.get("body", ""), "number": number}
