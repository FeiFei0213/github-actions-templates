import pytest
from scripts.pr_review.utils import truncate_text, retry


def test_truncate_text_short():
    """短文本不截断"""
    text = "hello world"
    assert truncate_text(text, max_lines=100) == text


def test_truncate_text_long():
    """超过 max_lines 时截断并加提示"""
    lines = "\n".join(f"line {i}" for i in range(200))
    result = truncate_text(lines, max_lines=100)
    assert result.count("\n") <= 101
    assert "已截断" in result


def test_truncate_text_empty():
    """空字符串返回空字符串"""
    assert truncate_text("", max_lines=100) == ""


def test_retry_succeeds_on_first():
    """第一次成功时直接返回"""
    call_count = {"n": 0}

    def fn():
        call_count["n"] += 1
        return "ok"

    assert retry(fn, times=3) == "ok"
    assert call_count["n"] == 1


def test_retry_succeeds_on_second():
    """第一次失败，第二次成功"""
    call_count = {"n": 0}

    def fn():
        call_count["n"] += 1
        if call_count["n"] == 1:
            raise Exception("fail")
        return "ok"

    assert retry(fn, times=3, wait=0) == "ok"
    assert call_count["n"] == 2


def test_retry_raises_after_max():
    """超过重试次数后抛出异常"""
    def fn():
        raise Exception("always fail")

    with pytest.raises(Exception, match="always fail"):
        retry(fn, times=2, wait=0)
