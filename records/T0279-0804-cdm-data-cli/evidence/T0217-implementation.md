# T0217 cdm-data-cli 实现清单

任务：cdm-data-cli 受控采集 CLI（Topic/JSONL/Keyset）
实现仓库：/home/black/Downloads/aio-cdm/aio/report_collect/（落地于 aio-cdm 本仓）
依据：cdm_report_center_cli_subscheme.md（CLI 子方案，唯一事实源）+ 主方案 §6.2/§3.5.x/§3.4.1 + T0217 prd.md（7 项 AC）

## 实现模块结构

| 模块 | 职责 | 契约锚点 |
|------|------|---------|
| core/errors.py | 稳定 CLI 错误码体系（TOPIC_UNSUPPORTED/RPC_ARGUMENT_INVALID/CLI_AUTH_FAILED/CLI_EXEC_FAILED/SOURCE_QUERY_FAILED/SOURCE_UPDATE_TIME_MISSING/ORM_VERSION_MISMATCH 等） | 子方案 §6 / 主方案 §6.4 |
| core/contracts.py | TopicSpec/TopicRegistry 固定注册表（resource/task/capacity；page_size 500/1000/500；task 需 cursor） | 子方案 §2.2/§2.3 |
| core/keys.py | assemble_entity_key（{backup_domain_id}:{source_table}:{source_id}，表名 regex 白名单）+ ArgumentPolicy 参数白名单 + BackupDomainId | 主方案 §3.5.2 |
| core/cursor.py | KeysetCursor（task 增量起点，>= 过滤，task_run_key 仅并列键不参与游标） | 子方案 §3 |
| core/timeutil.py | ISO 8601 解析（Python 3.6 兼容：fromisoformat + strptime 回退） | CDM 主机 Python 3.6 运行时 |
| core/serialization.py | JSONL 逐行输出（每行一记录，stdout 不混日志）+ 结构化 stderr 错误行 + BatchWriter | 子方案 §4/§6 |
| core/reader.py | SourceReader 抽象 + MemorySourceReader 测试替身 | 测试接缝 |
| core/orm_reader.py | OrmSourceReader 生产只读 ORM reader（惰性 import aio.db；require_columns 字段缺失即失败；一次 order_by(*exprs) 保并列键） | 主方案 §3.4.1 / AC-6 |
| core/imports.py | require_version_match（主/次版本一致）+ ModelFieldProbe（字段探测） | 主方案 §3.4.1 |
| orchestration/registry.py | TopicCollector 抽象 + CollectContext | — |
| orchestration/collector_factory.py | Topic → 采集器映射 | — |
| topics/resource/collector.py | 资源快照：data_source/host/backup_unit/instance/backup_object/protection_object/policy 维度 + 关系 | 子方案 §5.3/§5.4 |
| topics/task/collector.py | 任务事实增量：>= cursor 过滤；task_run_key 并列；source_update_time 缺失即 SOURCE_UPDATE_TIME_MISSING | 子方案 §5.5 |
| topics/capacity/collector.py | 存储 Worker 维度 + 当日容量样本；只输出成功 Worker；filters is_active=True | 子方案 §5.6 |
| cli/command.py | 直接子命令 resource/task/capacity/verify-credentials；白名单参数；StructuredGroup/Command 结构化错误 | 子方案 §2.1/§2.2/§6 |
| runtime/bootstrap.py | ReadonlyRuntime + build_orm_reader（惰性加载 aio 模型，model_map 键与采集器查询名一致） | AC-6 |
| runtime/auth.py | CredentialValidator 接口 + 测试替身 | AC-7 |
| entrypoint.py | 生产装配：build_orm_reader + build_runtime 注入；REQUIRED_COLUMNS 启动校验 | AC-6 |

## 测试矩阵（tests/report_collect/，69 项通过）

- test_core_contracts.py：entity_key 组装/白名单/Topic 注册表（TOPIC_UNSUPPORTED）/Keyset/时间解析（3.6 回退）
- test_serialization_reader.py：JSONL 逐行/无日志混入/UTF-8/BatchWriter 阈值与失败分支/版本匹配/字段探测
- test_orm_reader.py：字段校验/未知模型拒绝/复合 order_by 单次调用（AC-4 并列键）/关闭 session
- test_cli_contract.py：resource/task/capacity JSONL、task 需 cursor、capacity 拒绝 cursor、未知 Topic→TOPIC_UNSUPPORTED、未知参数→RPC_ARGUMENT_INVALID、verify-credentials 接受/拒绝/无 runtime、凭据不泄露、独立命令树
- test_dependency_boundaries.py：core/topics 层无 flask/aio.db 依赖
- test_collector_factory.py：Topic→采集器映射
- topics/resource/test_resource_collector.py、topics/test_task_capacity_collectors.py：采集器归一化

## 关键实现决策

- 从零重写（用户 grill 决策：忽略 origin/feature/F-140-report-center 历史实现）
- 惰性导入：core/orchestration/runtime/topics 零 flask 依赖，生产 ORM 仅在 CDM 主机运行时加载
- 直接子命令结构（cdm-data-cli resource/task/capacity/verify-credentials，子方案 §2.1）
- page_size 由 spec 固定（500/1000/500），CLI 不接收任意值（子方案 §2.2）
- 关系 rel_*/backup_objects 为源端归一化视图（真实 ORM 无独立表），生产集成时由归一化层接入

## 已知限制（需生产集成验证）

1. _load_models 语义名→aio 模型类映射（Endpoint/Host/BackupUnit_/Instance/ApplicationProtection/ApplicationPolicy/TotalTask/Storage）字段结构需在 CDM 主机核对
2. REQUIRED_COLUMNS 当前为最小字段集，完整字段集生产补全
3. target_version 版本匹配默认不触发（entrypoint 传 None），生产接线
4. 凭据 validator 生产由 CDM 账号系统注入，当前未装配时明确失败（CLI_EXEC_FAILED）
