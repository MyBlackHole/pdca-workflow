---
schema: pdca.asset/v1
id: knowledge:information-architecture/project-cleanup-boundary
layer: knowledge
summary: 项目冗余清理必须以 canonical 来源、可重建性和静态分析证据为边界
tags: [maintenance, cleanup, provenance, dead-code]
scenarios: [default, technical-design]
phases: [plan, do, check, act]
applies_when: [需要清理已有 PDCA 记录和运行时状态的项目]
excludes_when: [无法确认内容来源或仍有活跃进程持有运行时文件]
source_ids: [experience:T0020--07-26-清理项目冗余文件-目录与代码]
confidence: high
status: active
---

# 项目冗余清理边界

清理前先区分四类内容：

1. 已由 evidence blob 等 canonical 资产完整保存的重复副本，可以删除副本，但保留历史 manifest 的来源字段以维护 provenance。
2. 确认为空且未跟踪的目录可以删除；Git 不记录空目录，运行时可按需重建。
3. 确认无活跃持有者且可重建的零字节锁文件可以删除；不要删除运行时状态和索引数据库。
4. 代码只能在静态分析、引用检查和完整测试共同支持时删除。仅因低频引用、体积或名称相似，不足以证明代码冗余。

清理完成后必须验证证据 manifest、构建、测试和工作树，失败时优先恢复可追溯的源码副本，不重写历史记录。
