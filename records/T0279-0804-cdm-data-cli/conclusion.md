---
schema: pdca.asset/v1
id: T0217-0804-cdm-data-cli
phase: check
source_ids: [e1-cli-implementation, e2-cli-tests, e3-cli-smoke, convergence-map]
---

## 上下文

需求 140（CDM 报表中心）子任务 T0217：实现 `cdm-data-cli` 受控采集 CLI，供
collection-service 经既有 rpc 工具通道在 CDM 主机执行，输出 JSONL 契约行入库。
T0214 完成需求拆解；T0215 产出 CLI 子方案（唯一事实源）；用户 grill 决策
**从零重写**（忽略 `origin/feature/F-140-report-center` 历史实现）。CLI 落地
aio-cdm 本仓 `aio/report_collect/`，复用既有 ORM 只读。

## 假设与结果

| 假设 | 结果 |
|------|------|
| 三 Topic 子命令 + verify-credentials 输出符合 JSONL 契约 | ✅ 69 项测试 + 8 场景冒烟全绿 |
| 参数白名单生效，未知 Topic/参数结构化拒绝 | ✅ TOPIC_UNSUPPORTED / RPC_ARGUMENT_INVALID |
| Keyset 无 offset，task 增量 `>=` + task_run_key 并列键 | ✅ 复合排序一次 order_by(*exprs) 修复覆盖 |
| entity_key 按 `{backup_domain_id}:{source_table}:{source_id}` 组装 | ✅ 冒烟 12:data_source:7 |
| 复用既有 ORM 只读不改，字段缺失即失败 | ✅ OrmSourceReader + build_orm_reader 惰性装配 + REQUIRED_COLUMNS |
| 容量仅成功样本；verify-credentials 不恒 ok | ✅ 失败 Worker 不输出；无 runtime 明确 CLI_EXEC_FAILED |

## 分析

1. **双轴代码审查**（A4）：标准轴发现 7 项（fromisoformat 3.6 兼容、order_by 覆盖、
   脱敏 no-op、runner 死代码、TopicSpec 冗余、_EXEC_* 全局污染、bootstrap 死导入），
   规范轴发现 7 项（生产装配未接 ORM、verify-credentials 恒 ok、order_by 覆盖、
   错误码、--page-size 暴露、组层嵌套、ZFS/关系依赖）。全部甄别后修复 A 类 12 项；
   复审确认 Blocking=0。
2. **错误码对齐**：主方案 §6.4 第 3 类参数非法 → `RPC_ARGUMENT_INVALID`；
   未知 Topic → `TOPIC_UNSUPPORTED`；verify-credentials 未装配 → `CLI_EXEC_FAILED`（枚举内）。
3. **关键架构认知**：`total_tasks` 等采集器查询名是契约语义名，真实 ORM
   （TotalTask 表 aio_total_task）字段不含 `task_run_key`/`source_update_time`；
   `rel_*/backup_objects` 真实 ORM 无独立表 → 为**源端归一化视图**，生产由归一化层接入。
   已在实现清单与 evidence 中记录为已知限制。

## 适用边界

- 本环境无 flask/aio 依赖，CLI 核心层经惰性导入隔离可独立测试（--noconftest）。
- 生产装配（`_load_models` 语义名→模型映射、REQUIRED_COLUMNS 完整字段集、
  凭据 validator、target_version 版本匹配接线）需在 CDM 主机生产集成时核对补全。
- 关系解析、ZFS 判定字段依赖真实 aio 模型结构，属 T0218/部署阶段验证范围。

## 下一轮建议

1. T0216（Report DB Adapter）接续推进（plan 态，prd.md 已存在）。
2. 生产集成（CDM 主机）核对 `_load_models` 字段与 REQUIRED_COLUMNS 后关闭已知限制。
3. T0218（channel 调用）/ T0222（CLI/JSONL 侧压测）验收 Keyset 与超时分层。
