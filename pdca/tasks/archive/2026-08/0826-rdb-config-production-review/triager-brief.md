# Triage Brief — T3980 rdb-config 生产使用级别审查

## 分类
- scenario_type: review（评估性审查，Do 阶段不改代码）
- 目标：判定重构后（T3978/T3979：枚举 ID + sec_get_* 单参 API + 集中注册表）的 rdb-config 是否满足生产使用级别。

## 查重（P0）
- **T0369 / 0823-rdbcfg-config-audit**（2026-08-23，review）：sec_resolve_* 时代的 rdb-config 生产审查，产出 F1–F9，已修复 F1–F8（CONFIG_KV_MAX 静默截断、跨语言优先级不一致、常量重复、隐式第0层回退、atoi 脏值、并发竞态、Go/inih 语义分歧、命名混淆），F9（env 直接返回 getenv 指针、证书路径注入风险）留待安全专项。→ 本次为重构后复审，必须确认这些修复在 sec_get_* 新架构下仍然有效（回归），并评估新架构是否引入新问题。
- **T3978 / 0827-rdb-config-param-registry**：集中式参数注册表（五元组）落地。
- **T3979 / 0826-sec-get-param-api-refactor**：枚举 ID + sec_get_* 全面替代 sec_resolve_*（已归档）。
- **0826-cleanup-rdb-config-deadcode**（active）：清理 rdb-config.c 死字段/死函数/过时注释。→ 与本审查重叠，清理类发现应归并。

## Claim 验证（现状基线）
- 现状：libs/rdb-config.{c,h}，枚举 config_param_id_t（14 条）+ sec_get_int/bool/str(id) 单参 API + g_param_table[PARAM_COUNT] 指定初始化器 + sec_walk_* 四层遍历 + config_dump_params。
- 测试：param_registry_test 8/8、rdb_config_test 17/17（T3979 后）。
- 待审查：fail-closed 严格性、边界处理、并发（reload 锁 T0369 F6 已修，重构后是否保持）、env 注入（F9 遗留）、dump 安全性、错误处理完整性、消费者正确迁移、可观测性。

## 建议范围（待 Grill 确认）
- 维度：正确性/健壮性/安全/性能/可观测/并发/测试（code-review-checklist + secure-coding 框架）。
- 对象：核心库 + 关键消费者（rpc/dmsbtex/libobk/rdbcomm）+ Go oss 侧；含 T0369 F1–F8 回归确认。
- 判定：CRITICAL/HIGH = 0 为"满足"硬门槛；MEDIUM/LOW 记跟进。
- 处置：纯评估，发现留 Act 跟进；清理类归并 0826-cleanup。
