# T0163 Triage Brief

## 分类

- category: enhancement
- scenario_type: research
- phase: plan

## 查重结果

- 未发现已有“PostgreSQL/MySQL 逻辑导出转换 Parquet 性能 POC”的独立 active/archive task。
- 已有相关知识资产: `knowledge/data-formats/parquet-technical-reference.md`。
- 已有相关仓库文档: `parquet-production-cases.md`，包含 PostgreSQL/MySQL 到 Parquet 的方案对比、类型映射和风险。

## Claim 验证

- 仓库内已有调研结论建议后续执行 PG/MySQL 转换 PoC 验证。
- 当前仓库仅包含 Markdown 调研资料，未发现可执行 POC 脚本或性能实测报告。
- 因此该任务不是重复实现，而是从调研进入可复现实验验证。

## 信息缺口

- 本机是否已有 PostgreSQL/MySQL 服务或是否允许使用容器启动测试实例。
- 最终数据规模是否以本机资源为准，或需要模拟更接近生产的大表。
- 是否要求测试特定工具链，例如 MySQL Shell、DuckDB、PyArrow 或 Spark。

## 推荐下一步

- Plan 阶段先按“本地可复现实验优先，默认 100 万行，可降级 10 万行”的方案终审。
- 用户确认后进入 Do，读取 research 与 evidence 技能，执行实验并产出报告。
