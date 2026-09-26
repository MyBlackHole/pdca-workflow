---
schema: pdca.asset/v2
id: ontology:concept/ontology-adoption
type: concept
semantic_kind: class
layer: Knowledge
dcterms_license: CC-BY-4.0
dcterms_created: '2026-09-12'
status: active
authority: normative
revision: 4.0.0-rc.2
dcterms_modified: '2026-09-26'
summary: ADOPT-01：显式采用固定版本
---

# ADOPT-01：显式采用固定版本

采用记录绑定定义id/revision、内容摘要、来源、适用目标、限制和用户已授权的计划／处置。活动任务使用原已固定版本；环境或库更新不静默升级。

新版本存在不阻止仍适用的旧任务；发现影响当前正确性的错误则记录影响并停止受影响动作，提出变更。源文件缺失／漂移不能仅根据摘要字符串继续。

参考资产的候选资格与归档恢复按 [REUSE-01](ontology-reuse.md#参考资产的生命周期) 核对。
采用记录固定的是实际修订及内容，而不是随库更新变化的 status；替代链接不自动改绑已采用定义。
