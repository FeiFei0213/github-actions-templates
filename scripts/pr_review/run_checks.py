import subprocess
from .utils import truncate_text


def run_ruff(py_files: list[str]) -> str:
    """对指定文件运行 ruff check。无问题时返回 '✅ 无风格问题'。"""
    if not py_files:
        return "（无 Python 文件变更）"

    result = subprocess.run(
        ["ruff", "check", "--output-format=text"] + py_files,
        capture_output=True,
        text=True,
    )
    output = (result.stdout + result.stderr).strip()
    if not output:
        return "✅ 无风格问题"
    return truncate_text(output, max_lines=100)


def run_bandit(py_files: list[str]) -> str:
    """对指定文件运行 bandit 安全扫描。无问题时返回 '✅ 无安全问题'。"""
    if not py_files:
        return "（无 Python 文件变更）"

    result = subprocess.run(
        ["bandit", "-r", "--severity-level", "medium", "-q"] + py_files,
        capture_output=True,
        text=True,
    )
    output = (result.stdout + result.stderr).strip()
    if not output or "No issues identified" in output:
        return "✅ 无安全问题"
    return truncate_text(output, max_lines=100)
