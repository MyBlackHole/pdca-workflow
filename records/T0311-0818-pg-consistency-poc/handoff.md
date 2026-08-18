## 当前状态
- T0311（0818-pg-consistency-poc）已 confirmed 并完成 Act：知识沉淀 2 份
  （data-formats/pg-heap-null-bitmap.md、data-formats/pg-consistency-verification-method.md）、
  disposition=projected、T0308 PRD 已补 POC 输入。待执行：journal 追加、git 提交
  （含 disposition）、归档。
- 核心结论：五维校验（行数/逐字段/聚合/schema/类型语义）+ mutation 12 类捕获率
  100%，方法可信；pgbin 对含 NULL 数据的转换原有 3 类缺陷（nullbit 判定反转、
  t_bits 偏移 23、NULL 语义丢失/未初始化 UB）已修复，含 NULL 转换正确，T0301
  三版本回归 PASS。

## 未完成事项
- T0308（0818-pg-varlena-toast-followup）：按 POC 输入承接 TOAST 值对照、4B 头
  varlena 正式对照、NULL 跨版本（9.6/11）回归、pgbin 参数统一。
- 类型全集（float/uuid/json/bytea）扩列（T0308 备注列为后续）。
- pgbin 修复（src/pg 三文件）待提交源码仓库（需用户确认）。

## 已知约束
- 测试数据（heap/parquet/SQL 基准/CLOG）不进 pdca 仓库；验证产物在源码仓库
  evidence/pg/consistency/。
- 校验用 duckdb 读 parquet（SQL 层规范化保留 DECIMAL 精度）；pyarrow 环境在
  /home/black/Public/aio/Idea/Parquet/.venv（T0301 verify 脚本依赖）。
- pageinspect 的 t_bits 输出为 bit 反转显示，以 heap 字节为准。

## 推荐的下一步
- 完成 T0311 收尾：journal → git commit（含 disposition）→ advance-phase archive
  → 移动 pdca/tasks/0818-pg-consistency-poc 到 archive/2026-08/。
- 源码仓库提交 pgbin 3 缺陷修复（pg_heap_reader.c/pgbin.cpp/pg_versions.h + 新脚本
  gen_consistency.py/verify_consistency.py/mutate_consistency.py + research-report）。
- 随后进入 T0308 Plan：按 POC 输入细化 PRD（TOAST 值对照 + 校验基线）。

## 关键上下文文件列表
- $PDCA_HOME/records/T0311-0818-pg-consistency-poc/{conclusion.md,evidence/}
- $PDCA_HOME/knowledge/data-formats/{pg-heap-null-bitmap.md,pg-consistency-verification-method.md}
- /home/black/Documents/database_转换_parquet/evidence/pg/consistency/{poc_consistency_heap,poc_consistency.sql.tsv,poc_consistency.parquet,research-report.md}
- /home/black/Documents/database_转换_parquet/bench/{gen_consistency.py,verify_consistency.py,mutate_consistency.py}
- /home/black/Documents/database_转换_parquet/src/pg/{pg_heap_reader.c,pgbin.cpp,pg_versions.h}

## suggested skills
- advance-phase（T0311 归档、T0308 阶段推进）
- flow-plan（T0308 细化 PRD）
- register-evidence / validate-convergence（后续证据登记复用）
- verify_consistency.py 做 T0308 校验基线；mutation 类可扩充