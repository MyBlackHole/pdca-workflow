---
schema: pdca.asset/v1
id: ontology:domain/skill-commit-format
name: commit-format
summary: Commit changes with structured format following conventional commits.
description: 按照仓库规范生成 Git 提交信息。当用户要求"commit"、"提交"、"生成提交信息"时触发。
invocation: manual
type: domain
layer: Knowledge
status: active
relations:
  specializes:
    - ontology:concept/pdca-task
  relates_to:
    - ontology:concept/writing-for-agents
    - ontology:concept/triage
  testable_signal: "检查本文件内容完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空且不含泛化短语"

---


--------|------|
| 新功能 | `feat` |
| 修复 bug | `fix` |
| spec 变更 | `spec` |
| skill 变更 | `skill` |
| 模板变更 | `template` |
| pdca 工具 | `pdca` |
| 重构 | `refactor` |
| 性能优化 | `perf` |
| 测试 | `test` |
| 文档 | `docs` |
| 依赖/配置/杂项 | `chore` |

scope 为模块名，`kebab-case`。不确定时不加 scope。

### 3. 编写提交信息

```
<type>(<scope>): <description>

<body>

<footer>
```

- description 不超过 50 字符，祈使句，首字母小写
- body 说明"为什么做"，多行用空行分隔
- footer 写 breaking change 或 issue 引用

### 4. 确认

展示生成的提交信息让用户确认后再执行 `git commit`。

## 示例

```
fix(rpc): 修复 TLS 握手超时未重试

当 TLS 握手第一次超时时，客户端直接返回错误
而非重试。根据 RFC 标准，握手超时应至少重试一次。

增加一次自动重试，间隔 500ms。

Closes #123
```

```
feat(auth): 添加 OAuth 登录支持

BREAKING CHANGE: `POST /auth/login` 改为 `POST /api/v1/auth/login`
```

## 已知坑

- 提交前检查 `git status`/`git diff`，只 stage 预期文件，勿提交 secrets；仓库 hook 拒绝时修复后新提交而非 amend 失败提交。
