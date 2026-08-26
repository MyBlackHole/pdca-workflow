---
schema: pdca.asset/v1
id: T3980-0826-rdb-config-production-review
phase: check
source_ids: [REVIEW-REPORT-2, convergence-map-2]
---

## 上下文
本任务（T3980，review 场景）审查 `libs/rdb-config` 在 T3978/T3979 重构后是否满足生产使用级别。审查范围覆盖核心库 `rdb-config.{c,h}`、消费者（rpc/dmsbtex/libobk/rdbcomm）、Go `oss` 侧，并以 T0369 审计基线 F1–F9 做回归比对。

## 假设与结果
- 假设：T3979 的四层解析链已彻底替代旧 `sec_resolve_*`，安全开关应 fail-closed。
- 结果：**假设部分成立**。BOOL 开关已 fail-closed；但 INT 型安全开关（审计/鉴权）在 env 层仍走历史 `atoi`，脏值静默变 0 → **fail-open**，构成 1 个 HIGH 级确定性缺陷。
- 总体判定：**不满足生产使用级别**（CRITICAL/HIGH = 1，违反 AC-7 硬门槛）。

## 分析
- **AC-1** ✅ 审查报告已交付（REVIEW-REPORT-2）
- **AC-2** ❌ 核心库不满足生产就绪：HIGH-1 `sec_walk_int` env 层 `atoi` 使 INT 安全开关脏值 fail-open（REVIEW-REPORT-2）
- **AC-3** ✅ 消费者迁移功能正确（各调用点 param ID 与解析链路完整）；备注：消费者未对 `sec_get_int` 安全开关做 -1 校验，与 HIGH-1 同源（REVIEW-REPORT-2）
- **AC-4** ✅ Go/C 优先级对齐 F1（env > 文件）；备注：Go/C 布尔严格度分歧（LOW-3）（REVIEW-REPORT-2）
- **AC-5** ❌ T0369 回归部分失败：F5（`sec_walk_int` env 层未严格解析）、F6（`config_set_string` 无锁）未完全满足（REVIEW-REPORT-2）
- **AC-6** ✅ F9 重新评估完成，结论：仍 MEDIUM（`sec_walk_str` 直接返回 `getenv` 指针 + 证书路径未校验）（REVIEW-REPORT-2）
- **AC-7** ❌ CRITICAL/HIGH=0 门槛未达成（HIGH=1）（REVIEW-REPORT-2）
- **AC-8** ✅ 清理类发现（MEDIUM-2/3、LOW-1/2/3）已归并至活跃任务 `0826-cleanup-rdb-config-deadcode`（REVIEW-REPORT-2）

## 失败原因（rejected/partial 专用）
（本结论为 review 判定，非任务失败；不适用）

## 适用边界
- 威胁模型：env 通常运维可控；在容器/12-factor/CI 环境下 env 可被间接注入，此时 HIGH-1 可被利用使审计/鉴权静默关闭。
- 判定口径：以「安全控制 fail-closed」为生产级别硬标准；若组织接受 env 受信假设，可将该 HIGH 降级为 MEDIUM，则门槛达成。

## 下一轮建议
1. 必须（满足生产前）：HIGH-1 整改——将 `AUDIT_ENABLED`/`AUTH_KEYCHECK_ENABLED` 改为 `CFG_TYPE_BOOL` 或 `sec_walk_int` env 层改严格解析并使消费者 fail-closed。
2. 建议：MEDIUM-1 证书路径校验；MEDIUM-2 写锁；MEDIUM-3 告警重置。
3. 可选：LOW-1/2/3 可观测性与跨语言一致性打磨。
4. 跟进任务：在 `0826-cleanup-rdb-config-deadcode` 中落实清理类项。
