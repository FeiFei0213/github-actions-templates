#!/usr/bin/env python3
"""PR Review 主入口，由 GitHub Actions 调用"""
import os
import subprocess
import sys
import tempfile

from .get_diff import get_python_diff, get_changed_py_files
from .run_checks import run_ruff, run_bandit
from .generate_tests import generate_tests
from .post_comment import generate_review_comment, post_or_update_comment, BOT_MARKER


def run_generated_tests(test_code: str) -> str:
    """将生成的测试写入临时文件并运行，返回结果摘要"""
    if test_code.startswith("# "):
        return f"（跳过：{test_code}）"

    # 语法预检：防止 GLM 返回带 markdown 标记的内容导致 SyntaxError
    try:
        compile(test_code, "<generated>", "exec")
    except SyntaxError as e:
        return f"⚠️ 生成测试存在语法问题，已跳过运行：{e}"

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", prefix="generated_test_", delete=False, encoding="utf-8"
    ) as f:
        f.write(test_code)
        tmp_path = f.name

    result = subprocess.run(
        [sys.executable, "-m", "pytest", tmp_path, "-v", "--timeout=10", "--tb=short"],
        capture_output=True,
        text=True,
    )
    output = result.stdout + result.stderr
    status = "✅ 通过" if result.returncode == 0 else "❌ 存在失败测试"
    return f"{status}\n\n```\n{output[-3000:]}\n```"


def main():
    repo = os.environ["GITHUB_REPOSITORY"]
    pr_number = int(os.environ["PR_NUMBER"])
    github_token = os.environ["GITHUB_TOKEN"]
    glm_api_key = os.environ["GLM_API_KEY"]
    target_repo_path = os.environ["TARGET_REPO_PATH"]

    print(f"🔍 开始 Review PR #{pr_number} in {repo}")

    print("📥 获取 PR diff...")
    diff = get_python_diff(repo, pr_number, github_token)
    py_files = get_changed_py_files(repo, pr_number, github_token)

    if not py_files:
        print("ℹ️  无 Python 文件变更，发布提示评论")
        post_or_update_comment(
            repo, pr_number, github_token,
            f"{BOT_MARKER}\n## 🤖 AI Code Review\n\nℹ️ 此 PR 无 Python 文件变更，跳过自动 Review。"
        )
        return

    abs_py_files = [os.path.join(target_repo_path, f) for f in py_files]

    print("🔎 运行 ruff 风格检查...")
    ruff_report = run_ruff(abs_py_files)

    print("🔒 运行 bandit 安全扫描...")
    bandit_report = run_bandit(abs_py_files)

    print("🧪 GLM-5 生成测试...")
    test_code = generate_tests(diff, glm_api_key)

    print("▶️  运行生成的测试...")
    test_report = run_generated_tests(test_code)

    print("✍️  GLM-5 生成综合评论...")
    comment_body = generate_review_comment(
        diff=diff,
        ruff_report=ruff_report,
        bandit_report=bandit_report,
        test_report=test_report,
        api_key=glm_api_key,
    )

    print("💬 发布评论到 PR...")
    post_or_update_comment(repo, pr_number, github_token, comment_body)
    print("✅ Review 完成！")


if __name__ == "__main__":
    main()
