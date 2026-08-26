# T3980 对话日志（按阶段）

## Plan
- 创建任务 T3980（review 场景），triager-brief 写就。
- Grill 5 问全确认：全维度审查（正确性/健壮性/安全/并发/可观测性）；范围=核心库 `libs/rdb-config.{c,h}` + 消费者(rpc/dmsbtex/libobk/rdbcomm) + Go `oss` 侧 + T0369 F1–F8 回归；CRITICAL/HIGH=0 为硬门槛；清理类归并 0826-cleanup-rdb-config-deadcode；纯评估不改代码。
- prd.md 写就 AC-1~AC-8 复选框；知识注入 audit-findings / compile-time-param-id-binding / oss_https_tls / process-context-held-switches。
- P6 终审批准进入 do。

## Do
- 通读核心库 `rdb-config.c`（573 行）与 T0369 审计基线。
- 核查消费者调用点、`RDB_CONFIG`/`DEFAULT_RDB_CONFIG_PATH` 单一来源（F3 ✅）、Go `oss/cmd/tls.go` `chooseStr` 优先级一致性（F1 ✅）。
- 发现：HIGH-1（`sec_walk_int` env 层 `atoi` 致 INT 安全开关审计/鉴权脏值 fail-open）、MEDIUM-1（F9 证书路径）、MEDIUM-2（写无锁）、MEDIUM-3（告警不重置）、LOW×3（ENOENT 静默/constructor 吞错/Go-C 布尔严格度分歧）。
- 写审查报告 `evidence/review-report.md`，登记证据 REVIEW-REPORT-2 与 convergence-map-2。

## Check
- 写 `records/.../conclusion.md`（逐条 AC ✅/❌ 指向证据 ID）。
- `meta.verdict.outcome=confirmed`（审查结论成立：不满足生产使用级别）。
- 用户 verdict=confirmed（维持 HIGH）。

## Act
- 沉淀知识 `knowledge/rdb-config/int-security-switch-failopen.md`（INT 型安全开关须 fail-closed 原则 + T3980 HIGH-1 案例）。
- `meta.disposition.outcome=projected`。
- 创建跟进任务 **T3981**（HIGH-1 整改，development）。
- 清理类项 MEDIUM-2/3、LOW-1/2/3 归并活跃任务 0826-cleanup-rdb-config-deadcode。
