# Blog Repository Rules

## 写作规范
1. 任何来自参考来源的实体，在正文中第一次出现时，需要使用超链接。
2. 一些常见的 AI 领域术语，直接使用英文原文即可，无需翻译。

## 标签规范

- **严禁复用 knowledge-bank 标签**：博客文章（`src/content/posts/`）的 `tags` 不得与 `/Users/ZHao/WorkSpace/knowledge-bank/tags.json` 中的任何标签相同（包括 `top_level_tags`、`branches` 名称及其子路径，如 `LLM/inference`、`AI-Agent/tool-calling`、`MachineLearning`、`RSI`、`CaseStudy`、`Life` 等）。
- **当前博客标签白名单**：[`决策模型`, `知识库治理`]；其他文章保持 `tags: []`，不要擅自添加其他标签（除非用户明确要求）。
- **同步防线**：`scripts/sync_kb.py` 会读取 `knowledge-bank/tags.json`，在同步 `raw/out-blogs/` 时自动过滤与知识库重合的标签并打印告警；若源文章标签被全部过滤且博客侧已有合规标签，则保留博客侧已有标签。