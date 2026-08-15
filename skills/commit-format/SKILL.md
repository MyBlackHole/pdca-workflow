---
name: commit-format
description: |
  按照仓库规范生成 Git 提交信息。当用户要求"commit"、"提交"、"生成提交信息"时触发。
---

# 提交信息格式化

## 触发条件

用户准备提交代码时使用此技能。

## 步骤

### 1. 分析变更

```bash
git diff --cached --stat     # 查看变更文件概览
git diff --cached            # 查看详细变更
```

判断：
- 变更涉及哪个 scope（模块/项目）
- 变更类型是什么（feat/fix/refactor/...）
- 是否有 breaking change
- 关联哪个 issue

### 2. 确定 type + scope

通用 type：

| 变更内容 | type |
|---------|------|
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
