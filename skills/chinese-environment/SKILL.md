---
name: chinese-environment
description: Use when setting up a project for Chinese-speaking developers, or when all output (docs, comments, commits) should be in Chinese
---

# Chinese Environment（中文环境）

## Core Rules

1. **AI 思考过程使用简体中文** — 内部推理、分析、规划、调试、代码审查等所有思考过程均使用简体中文
2. **AI → user 沟通使用简体中文**
3. **项目文档使用简体中文** — README、API 文档、changelog、spec、design docs
4. **代码保持英文** — 变量名、函数名、类名、类型名、API 签名保持英文
5. **代码注释用中文** — 使用 `// 备注:` 前缀；同时加载 `code-comments` 处理注释格式细节；保留原始英文注释
6. **Commit message 用中文** — 遵循 conventional commits 格式：`类型: 中文描述`
7. **项目 locale** — `zh_CN.UTF-8`，时区 `Asia/Shanghai`，编码 `UTF-8`

## Verification Checklist
- [ ] AI 思考/推理全程使用简体中文
- [ ] 所有文档为简体中文
- [ ] 所有代码标识符为英文
- [ ] Commit message 格式 `类型: 中文描述`
- [ ] 代码注释引用 `code-comments` 或使用 `// 备注:` 前缀
- [ ] 保留代码中原始英文注释
- [ ] locale 和时区设置为中国标准
