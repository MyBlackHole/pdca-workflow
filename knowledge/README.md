# Knowledge Base

这里仅保存经过准入筛选、能够跨任务复用的活知识。信息按四层组织：
Evidence（原始事实）→ Experience（一次任务）→ Knowledge（跨任务结论）→ Skill（可执行步骤）。

规则：

1. 使用 `knowledge/<topic>/<semantic-slug>.md`，文件名不带日期。
2. 原始证据以内容摘要保存到 `records/<record-id>/evidence/`；单次任务经验写入
   `records/<record-id>/experience.md`。
3. 知识写入后必须在 `manifest.jsonl` 中登记（见 `flow-act` 步骤 2），
   记录 revision、摘要和来源 record 路径。
4. 知识可以修订；record 不应封存后修改。
5. 没有复用价值的实验只保留 record，不创建知识副本。
6. 新资产使用 `schema: pdca.asset/v1`，声明稳定 ID、summary、tags、scenarios、
   phases、适用/排除条件和 source IDs。
