---
schema: pdca.asset/v1
id: T3965-0826-squash-f139-mtls-review
phase: check
source_ids: [ac1-squash, mtls-analysis]
---

## 上下文

用户要求将 00f12df7（含）之后 11 个提交合并为单个 F-139 提交，并整体分析其中 mTLS 修改。squash 完成（4ef9c5c1，tree 一致性无损验证）；分析覆盖证书层/协商层/会话 IO/配置分层全部 mTLS 代码。

## 假设与结果

| 假设 | 结果 |
|------|------|
| squash 仅合并历史不改内容 | 成立：git diff 原 HEAD 与新 HEAD 为空（TREE-IDENTICAL） |
| mTLS 栈存在可分级的问题/简化/优化点 | 成立：1 HIGH + 2 MEDIUM 问题、2 项可安全简化、4 项评估后无需动 |

## 分析

- **AC-1** ✅ squash 无损：`git diff d73f26a5 HEAD` 为空；原链保留 reflog；origin 同步需 force push（未主动执行）（ac1-squash）
- **AC-2** ✅ 报告三节齐备（mtls-analysis）：
  - 问题：P1 ccache 满容量语义误导且无淘汰(HIGH)、P2 reload 竞态潜伏(MEDIUM)、P3 失败路径 SSL_shutdown SIGPIPE 风险(MEDIUM)、P4/LOW
  - 可安全简化：S1 四模块算法解析块归一 libs（推荐后续任务）、S2 决策树双维护抽纯函数（需单独评审）、S3 LOW、S4 不建议
  - 优化：O1~O4 评估后均无需改动（错误路径/低频路径，现有实现合理）

Grill 追问：
1. P1 的实际触发面？→ 仅客户端进程使用≥65 种 (cert_dir,algorithm,ca_cn) 组合才触发，当前部署形态（单 cert_dir 单 ca_cn）不会命中——但作为库 API 是潜伏地雷。
2. squash 是否影响远端一致性？→ origin 在 004ebafe（旧链），push 需 --force-with-lease；原链对象在远端仍存在直至 GC。

## 适用边界

分析基于 squash 后快照 4ef9c5c1；P1/P2 的修复建议落地时另立任务走完整流程。

## 下一轮建议

- 立项修复 P1（ccache LRU 或专用错误码 TLS_CERT_ERR_CCACHE_FULL）。
- P2 接入热轮换前补 slot 锁或文档声明约束。
- S1 归一可并入下一个跨模块清理任务。

verdict: {"outcome": "confirmed", "reason": "squash 无损验证通过；mTLS 三节分析齐备且结论可执行", "verdict_id": "T3965-check-v1", "at": "2026-08-26T09:20:00+08:00"}
