# github-actions-templates

Python 仓库 PR 自动 Review 系统，使用 GLM-5 进行代码审查。

## 功能

- ✅ **ruff** 代码风格检查
- ✅ **bandit** 安全扫描
- ✅ **GLM-5** 自动生成 pytest 测试并运行
- ✅ **GLM-5** 综合中文 Review 评论（自动更新，不堆积）

## 使用方法

### 1. 添加 Caller Workflow

在你的 Python 仓库中创建 `.github/workflows/pr-review.yml`，内容复制自本仓库的 `caller-workflow-template.yml`。

### 2. 添加 GLM API Secret

仓库 **Settings → Secrets and variables → Actions → New repository secret**：

| Name | Value |
|------|-------|
| `GLM_API_KEY` | 你的智谱 AI API 密钥（bigmodel.cn） |

### 3. 创建 PR 即可触发

PR 创建或更新后，几分钟内自动出现中文 Review 评论。

## 注意事项

- 不支持来自 fork 仓库的 PR
- 生成的测试仅在 CI 中运行，不会提交到仓库
- 模型：智谱 AI GLM-5（`glm-4-5`）
