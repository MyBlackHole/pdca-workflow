## 当前状态
T0300（MySQL 四版本逐版本 .ibd→Parquet 转换测试）已 verdict=confirmed，Act 阶段收尾：
disposition=projected 已写入、知识沉淀完成（knowledge/data-formats/t0300-mysql-version-convert-test.md
登记 manifest）、证据已登记（records/T0300-0818-mysql-version-convert-test/evidence/）。

## 未完成事项
- 无（归档 mv 由 flow-act Ac8 完成；吞吐基准如需单实例重测为可选后续）

## 已知约束
- 测试数据（.ibd / *_sql.tsv / *.parquet，约 1.2G）保留在源项目 evidence/mysql/versions/，不入 git 与 pdca
- mysqlbin 输出按物理页序，不保证主键序（56/57/84 页序≠id 序）——顺序敏感消费须先按主键排序
- 多实例并行转换吞吐不可作基准（并行争用；单实例基准见 T0250 AC-5）
- 源项目已提交：69ff680（转换测试工具+记录）、1126c5d（页序陷阱补录 EVIDENCE.md）

## 推荐的下一步
- 结束本任务；新需求（如旧 BLOB type22 / PG9.x pg_clog / 版本级性能基准）走 Plan→Do→Check→Act 新任务

## 关键上下文文件列表
- knowledge/data-formats/t0300-mysql-version-convert-test.md（转换测试流程模板+页序陷阱+工具用法）
- records/T0300-0818-mysql-version-convert-test/conclusion.md（verdict confirmed）
- 源项目 bench/extract_version_ibd.sh、bench/verify_version_convert.py（可复用工具）
- 源项目 evidence/mysql/versions/T0300_version_convert.md（四版本转换测试记录）

## suggested skills
- chinese-environment（全中文项目）
- code-comments（源码中文注释）
- testing-strategy（全量对照/样本量）
