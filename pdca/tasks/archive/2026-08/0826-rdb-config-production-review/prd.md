# 审查 rdb-config 是否满足生产使用级别

## 问题陈述
T3978/T3979 将 rdb-config 重构为枚举参数 ID（`config_param_id_t` 14 条）+ `sec_get_*(id)` 单参 API + 集中注册表（`g_param_table[PARAM_COUNT]` 指定初始化器 + `sec_walk_*` 四层遍历）。需独立判定重构后的 rdb-config 是否满足生产使用级别。已有 T0369（sec_resolve_* 时代）生产审查，修复 F1–F8，本次必须确认这些修复在重构后未回归，并评估新架构是否引入新问题。

## 方案（审查方法）
- **全维度静态审查**：正确性 / 健壮性（fail-closed 严格性、边界、错误路径）/ 安全（注入、权限、敏感信息）/ 性能 / 可观测性 / 并发 / 测试覆盖；框架 = `code-review-checklist` + `secure-coding`。
- **对象**：核心库 `libs/rdb-config.{c,h}` + 关键消费者（`rpc` / `dmsbtex` / `libobk` / `rdbcomm` 的 `sec_get_*` 调用点）+ Go `oss` 侧配置解析。
- **回归**：T0369 F1–F8 修复在重构后是否仍然有效。
- **专项**：T0369 F9 遗留 env 注入风险（`sec_get_str` 是否仍直接返回 `getenv` 指针、证书路径是否校验）重新评估。
- **产出**：结构化审查报告（每条发现含 `文件:行`、严重度 `CRITICAL/HIGH/MEDIUM/LOW`、问题、建议）。
- **处置**：纯评估，Do 阶段不改代码；清理类发现归并 `0826-cleanup-rdb-config-deadcode`；功能/安全/健壮性缺口在 Act 阶段创建跟进任务。

## 用户故事
作为运维/开发者，我需要确信 rdb-config 在生产环境（多模块共享、并发 reload、不可信 env、海量配置）下行为正确、失败可预期、无安全漏洞。

## 实现/测试决策
- Do 阶段：仅静态审查 + 必要的小规模实证（构造 ini/环境变量复现边界），不修改生产代码。
- 判定门槛：CRITICAL/HIGH 严重度发现 = 0 → `verdict=满足`；否则 `verdict=不满足/部分`，列出 blocking 项。

## 范围外
- 不修复发现的问题（仅评估，Act 跟进）。
- 不审查非配置相关模块。
- reload 链路修复（T3979 PRD 范围外）仅作为审查观察项，不深入。

## 验收标准
- [ ] AC-1: 产出全维度结构化审查报告，覆盖正确性/健壮性/安全/性能/可观测/并发/测试，每条发现含 文件:行、严重度(CRITICAL/HIGH/MEDIUM/LOW)、问题、建议。
- [ ] AC-2: 核心库 libs/rdb-config.{c,h} 逐行审查，fail-closed 严格性/边界/错误处理/dump 安全/env 处理无 CRITICAL/HIGH 发现。
- [ ] AC-3: 关键消费者（rpc/dmsbtex/libobk/rdbcomm）sec_get_* 迁移正确性审查，无 CRITICAL/HIGH 发现。
- [ ] AC-4: Go oss 侧配置解析与 C 侧 sec_get_* 语义一致性审查（T0369 F1 回归），无 CRITICAL/HIGH 发现。
- [ ] AC-5: T0369 F1–F8 修复在重构后回归确认（静默截断/优先级/常量单一来源/隐式回退/脏值校验/并发锁/Go-inih 语义/命名），全部仍有效。
- [ ] AC-6: T0369 F9 遗留 env 注入风险专项评估（sec_get_str 是否仍直接返回 getenv 指针、证书路径是否校验），给出结论与处置建议。
- [ ] AC-7: 应用判定门槛：CRITICAL/HIGH=0 → verdict=满足；否则 verdict=不满足/部分，并列出 blocking 项与严重度分布。
- [ ] AC-8: 清理类发现归并 0826-cleanup-rdb-config-deadcode（转交清单），不混入本审查修复。

## 备注
- 知识注入：T0369 `review.md`/`conclusion.md`、knowledge 中 rdb-config 审计发现（如 `knowledge/rdb-config/audit-findings.md`）、T3978/T3979 结论。
- 参考规范：SEI CERT C、OWASP Code Review Guide、CWE Top 25。
