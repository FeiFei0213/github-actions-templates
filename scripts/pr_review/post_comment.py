import requests
from .utils import build_glm_client, retry, truncate_text

GITHUB_API = "https://api.github.com"
BOT_MARKER = "<!-- pr-review-bot -->"
MODEL = "glm-4-5"

REVIEW_SYSTEM_PROMPT = """你是一个资深 Python 代码审查专家，用中文输出 Markdown 格式的代码审查报告。

严格按以下结构输出，不要增减章节：

### 代码风格（ruff）
{ruff 检查结果摘要，如无问题写"✅ 无问题"}

### 安全扫描（bandit）
{bandit 检查结果摘要，如无问题写"✅ 无问题"}

### 自动生成测试结果
{测试运行结果摘要}

### 综合评审意见
{对代码质量、设计、逻辑的整体评价，3-5 条，每条一行}

### 改进建议
{具体可操作的改进建议，按优先级排列，指出文件名和行号}

规则：全程使用中文，语气专业友好，建议具体可落地。"""


def generate_review_comment(
    diff: str,
    ruff_report: str,
    bandit_report: str,
    test_report: str,
    api_key: str,
) -> str:
    """调用 GLM-5 生成综合中文 Review 评论"""
    client = build_glm_client(api_key)

    user_content = f"""代码变更（diff）：
{truncate_text(diff, max_lines=300)}

---
ruff 检查结果：
{truncate_text(ruff_report, max_lines=100)}

---
bandit 安全扫描结果：
{truncate_text(bandit_report, max_lines=100)}

---
自动生成测试运行结果：
{truncate_text(test_report, max_lines=100)}
"""

    def call_glm():
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": REVIEW_SYSTEM_PROMPT},
                {"role": "user", "content": user_content},
            ],
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()

    try:
        body = retry(call_glm, times=2, wait=5.0)
    except Exception as e:
        body = f"❌ AI Review 暂时不可用：{e}"

    return f"{BOT_MARKER}\n## 🤖 AI Code Review\n\n{body}"


def find_existing_comment(repo: str, pr_number: int, token: str) -> int | None:
    """查找 PR 中已有的 bot 评论，返回 comment_id 或 None"""
    url = f"{GITHUB_API}/repos/{repo}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    resp = requests.get(url, headers=headers, params={"per_page": 100}, timeout=30)
    resp.raise_for_status()
    for comment in resp.json():
        if BOT_MARKER in comment.get("body", ""):
            return comment["id"]
    return None


def post_or_update_comment(repo: str, pr_number: int, token: str, body: str) -> None:
    """发布新评论或更新已有的 bot 评论"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json",
    }
    existing_id = find_existing_comment(repo, pr_number, token)

    if existing_id:
        url = f"{GITHUB_API}/repos/{repo}/issues/comments/{existing_id}"
        resp = requests.patch(url, headers=headers, json={"body": body}, timeout=30)
    else:
        url = f"{GITHUB_API}/repos/{repo}/issues/{pr_number}/comments"
        resp = requests.post(url, headers=headers, json={"body": body}, timeout=30)

    resp.raise_for_status()
