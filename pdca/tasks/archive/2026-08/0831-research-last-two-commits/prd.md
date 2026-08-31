# 调研最近两次提交（6195ba5d 与 740d55f0）内容与关联

## 背景

用户要求对 `aio-tools/6200/F/139` 仓库最近两次提交进行 PDCA research 调研。两次提交为：

- **HEAD `6195ba5d`（2026-08-31）**【B-T0451】`libs/tls_keygen: 修复签发 UAF 与序列号硬编码导致并发证书异常, 1.0.0.1 -> 1.0.0.2`
- **HEAD~1 `740d55f0`（2026-08-28）**【F-139】`TLS 安全链路整合：TLS/mTLS 全栈实现、配置收口、mTLS fail-closed 与版本号归一`（4180 files, +1319731/-3074，合并 0bf741f8..fef11220 区间全部改动）

两者存在引入-修复链：F-139 引入的 `tls_keygen` 签发链路缺陷被 B-T0451 修复。调研需覆盖提交本体、关联 PDCA 任务（T0451）、根因、影响面与版本语义。

## 目标

产出 `research` 型调研报告，回答：两次提交各改了什么、为什么改、如何验证、彼此关联、风险与后续建议。

## 验收标准

- [ ] AC-1：准确还原 6195ba5d 的变更清单、根因（UAF + 序列号硬编码）、修复方案、验证结果与版本变更（tls_keygen 1.0.0.1->1.0.0.2）
- [ ] AC-2：准确还原 740d55f0 的变更规模、核心改动分类（TLS/mTLS、配置收口、fail-closed、oss 集成等）、版本变更矩阵（libobk/rpc/dmsbtex/rdbcomm/tls_keygen/oss）
- [ ] AC-3：明确两次提交的关联关系（引入-修复链）与文件级重叠分析（仅 libs/tls_keygen.c 与 xmake.lua 重叠）
- [ ] AC-4：关联 PDCA 证据链（T0451 任务、prd/conclusion、回归测试）并给出可复现的 git 验证命令
- [ ] AC-5：给出风险评估与后续建议（是否需补充测试、文档、版本策略）
- [ ] AC-6：沉淀 pitfall 本体节点 `ontology/pitfall/tls-keygen-sign-uaf-serial.md`，覆盖 UAF 与序列号硬编码两陷阱，且 `ontology-validate` 通过、islands=0

## 非目标

- 不对 740d55f0 的 4000+ 文件做逐行审计，仅分类归纳

## 关联本体节点

```
ontology:concept/pdca-task
ontology:pitfall/tls-keygen-sign-uaf-serial
ontology:concept/pdca-ontology-ready
```

## 风险

- 740d55f0 为 squash 合并提交，区间内多分支并行，需以 commit message 与 git diff 为准，避免误归因
