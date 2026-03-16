import time
from zhipuai import ZhipuAI


def truncate_text(text: str, max_lines: int) -> str:
    """截断文本至 max_lines 行，超出时附加提示"""
    if not text:
        return text
    lines = text.splitlines()
    if len(lines) <= max_lines:
        return text
    truncated = "\n".join(lines[:max_lines])
    return truncated + f"\n\n... （已截断，原文共 {len(lines)} 行，仅显示前 {max_lines} 行）"


def build_glm_client(api_key: str) -> ZhipuAI:
    """创建 GLM 客户端"""
    return ZhipuAI(api_key=api_key)


def retry(fn, times: int = 2, wait: float = 5.0):
    """重试函数，失败等待 wait 秒后重试，超过 times 次抛出最后一个异常"""
    last_exc = None
    for attempt in range(times):
        try:
            return fn()
        except Exception as e:
            last_exc = e
            if attempt < times - 1:
                time.sleep(wait)
    raise last_exc
