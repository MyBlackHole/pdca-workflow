## 当前状态
- T0301（0818-pg-version-convert-test）已 confirmed 并完成 Act：知识沉淀 data-formats/t0301-pg-version-convert-test.md、disposition=projected、跟进任务 T0308 已创建。待执行：journal 追加、git 提交（含 disposition）、归档（advance-phase → archive + 移动目录）。
- 核心结论：PG 9.6/11/18 heap 头布局（24B，infomask2@18/infomask@20/t_hoff@22）与 varlena 编码（packed）各版本一致；CLOG 唯一差异为目录名（pg_clog/pg_xact）；三版本全量 1M×7 逐字段差异=0 + 聚合 PASS。
- 代码已统一：pg_heap_reader.c 删除版本分派（统一 PG_HEAP_* 常量），--pg-version 仅作源版本标注；pg_clog_legacy_pg9 转发目录参数化读取器。

## 未完成事项
- T0308（0818-pg-varlena-toast-followup）：扩展正式对照数据覆盖 4B 头 varlena（>127B）与 TOAST 外置（>2KB）路径；pgbin 参数统一为 `<heap> <clog_dir> <out> [--rows=] [--pg-version=]`。
- PG10/12/14/16 中间版本未实测（适用边界，非必做）。

## 已知约束
- 测试数据（heap/CLOG/parquet/SQL 基准）不进 pdca 仓库；容器 t0301-pg96/11、t0216-pg（user test/test，库 poct25）可复用。
- 版本事实以实测为准（pageinspect + 临时表），勿依赖二手文档推论（见知识沉淀"坑"）。
- 版本号紧凑化 atoi 陷阱（96>11 误判）——规范版本号解析。

## 推荐的下一步
- 完成 T0301 收尾：journal → git commit（含 disposition）→ advance-phase archive → 移动 pdca/tasks/0818-pg-version-convert-test 到 archive/2026-08/。
- 随后进入 T0308 Plan：设计含长文本列的 poc_orders 变体灌数与对照。

## 关键上下文文件列表
- $PDCA_HOME/records/T0301-0818-pg-version-convert-test/{conclusion.md,handoff.md,evidence/}
- $PDCA_HOME/knowledge/data-formats/t0301-pg-version-convert-test.md
- /home/black/Documents/database_转换_parquet/evidence/pg/versions/EVIDENCE.md（容器命令/对照表/数据摘要）
- /home/black/Documents/database_转换_parquet/bench/{gen_pg_versions.py,extract_version_pg.sh,verify_version_convert.py}
- /home/black/Documents/database_转换_parquet/src/pg/{pg_heap_reader.c,pgbin.cpp,pg_versions.h,pg_clog_legacy_pg9.c}

## suggested skills
- advance-phase（T0301 归档、后续 T0308 阶段推进）
- flow-plan / flow-do（T0308 新任务）
- register-evidence / validate-convergence（后续证据登记复用）
- 若做 4B 头/TOAST：pg_heap_reader.c 涉及 varlena_extended 分支，复用本仓库自解码经验