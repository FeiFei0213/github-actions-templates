import requests
from .utils import truncate_text

GITHUB_API = "https://api.github.com"


def get_pr_files(repo: str, pr_number: int, token: str) -> list[dict]:
    """获取 PR 变更的文件列表（每页最多 100 个）"""
    url = f"{GITHUB_API}/repos/{repo}/pulls/{pr_number}/files"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    resp = requests.get(url, headers=headers, params={"per_page": 100}, timeout=30)
    resp.raise_for_status()
    return resp.json()


def get_python_diff(repo: str, pr_number: int, token: str, max_lines: int = 300) -> str:
    """获取 PR 中所有 .py 文件的 diff，截断至 max_lines 行。"""
    files = get_pr_files(repo, pr_number, token)
    py_files = [f for f in files if f.get("filename", "").endswith(".py")]

    if not py_files:
        return ""

    parts = []
    for f in py_files:
        filename = f.get("filename", "")
        patch = f.get("patch", "（二进制或无 diff）")
        parts.append(f"### {filename}\n```diff\n{patch}\n```")

    full_diff = "\n\n".join(parts)
    return truncate_text(full_diff, max_lines=max_lines)


def get_changed_py_files(repo: str, pr_number: int, token: str) -> list[str]:
    """返回 PR 中变更的 .py 文件路径列表（仅 added/modified/renamed）"""
    files = get_pr_files(repo, pr_number, token)
    return [
        f["filename"]
        for f in files
        if f.get("filename", "").endswith(".py")
        and f.get("status") in ("added", "modified", "renamed")
    ]
