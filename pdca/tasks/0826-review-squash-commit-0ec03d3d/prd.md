# 全面审查提交 0ec03d3d 的设计/可读性/可维护性/可靠性/正确性

## 问题陈述

提交 `0ec03d3d`（TLS 安全链路整合，squash 自六个提交）包含约 3.6 万行第一方变更（273 文件），需在合入远程前做系统性质量审查。

## 审查对象与排除

- 对象：`git show 0ec03d3d` 中第一方变更——
  - `libs/`：tls_cert / tls_keygen / timed_net_key / rpc-net-protocol / common / logger / rdb-config 等 + libs/tests(36)
  - `rpc/`：server/client/conn/io/config/command/protocol/public + tests
  - `rdbcomm/`：client/server/io/msg/main + tests
  - `oss/`：cmd、main.go、test（**vendor 排除**）
  - `libobk/`、`fs-backup/`、`dmsbtex/`、`s3tools/`、`packages/o/openssl4`、根 xmake
- 排除：`third_party/openssl4`、`oss/vendor`（第三方代码，不审内容本身）

## 审查维度（用户指定）

1. 设计模式 2. 代码可读性 3. 代码可维护性 4. 代码可靠性 5. 正确性
附加轴（checklist 强制）：安全性、错误处理、测试覆盖、构建文件正确性。

## 方案

按模块分组并行深审（子代理），统一用 code-review-checklist 清单逐项检查；主 session 汇总为双轴报告：
- 标准轴：五维 + 安全 + 错误处理
- 规范轴：对照六源提交意图（TLS/mTLS 整合、rpc 开关上下文化、oss 开关化/单测、SAN 修复）验证实现一致性

产出 `review-report.md`：发现按 CRITICAL/HIGH/MEDIUM/LOW 分级，附 file:line 与修复建议；末尾给 Blocking 汇总与 verdict 建议。

## Seam 分析

本任务为审查场景，无代码产物；验证方式为报告存在性与发现可检索性。

### 声明的测试接缝

（无——review 场景，无被测模块）

## 验收标准

- [ ] AC-1: `records/T3975-0826-review-squash-commit-0ec03d3d/review-report.md` 存在且含五个用户维度的逐一结论段
- [ ] AC-2: 每条发现含严重度标签（CRITICAL/HIGH/MEDIUM/LOW）、file:line 定位与修复建议
- [ ] AC-3: 报告明确列出已覆盖的第一方模块清单与排除声明（third_party、oss/vendor）
- [ ] AC-4: 报告末尾有 Blocking（CRITICAL+HIGH）数量汇总与合并建议
