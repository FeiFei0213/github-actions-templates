from .utils import build_glm_client, retry, truncate_text

SYSTEM_PROMPT = """你是一个 Python 测试专家。
根据用户提供的代码 diff，生成对应的 pytest 测试代码。

要求：
1. 只输出纯 Python 代码，不要有任何解释文字、markdown 代码块标记（不要输出 ```python 这样的标记）
2. 使用中文注释说明每个测试的目的
3. 每个测试函数只测试一个行为
4. 禁止在测试中使用：文件 IO、网络请求、os.system、subprocess
5. 如果 diff 中没有可测试的函数或类，只输出注释：# 无可测试的函数或类
6. 测试文件顶部加上必要的 import（使用 unittest.mock 处理依赖，不要真实调用外部服务）"""

MODEL = "glm-4-5"


def generate_tests(diff: str, api_key: str) -> str:
    """调用 GLM-5 根据 diff 生成 pytest 测试代码。"""
    if not diff.strip():
        return "# 无 Python 代码变更，跳过测试生成"

    client = build_glm_client(api_key)
    truncated_diff = truncate_text(diff, max_lines=200)

    def call_glm():
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"请为以下代码变更生成 pytest 测试：\n\n{truncated_diff}"},
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content.strip()

    try:
        return retry(call_glm, times=2, wait=5.0)
    except Exception as e:
        return f"# GLM 生成测试失败：{e}"
