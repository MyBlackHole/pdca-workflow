---
schema: pdca.asset/v1
id: T0096-0727-knowledge-reorg
layer: experience
summary: 知识目录清理与产出管线修复
tags: [knowledge, cleanup, manifest, pipeline]
---

# 结论: T0096 — 知识目录清理与产出管线修复

## 发现

1. `knowledge/out-of-scope/` 和 `knowledge/drafts/` 是死目录/草稿残留
2. 7 个知识文件从未登入 manifest.jsonl，导致检索不可见
3. `knowledge/README.md` 引用已不存在的 `pdca task project-knowledge` CLI
4. `flow-act` 步骤 2 只写文件不登 manifest，是管线断裂的根因
5. `core/` 分类模糊：architecture.md 和 cli-behavior.md 本质是 pdca-flow 知识
6. 2 个 workflow 知识文件缺少 `schema: pdca.asset/v1` frontmatter

## 修复

| 修复项 | 说明 |
|--------|------|
| 清理空目录/草稿 | 删除 out-of-scope/、drafts/ |
| 补 frontmatter | workflow/ 下 2 文件 |
| 合并 core→pdca-flow | architecture、cli-behavior 搬家 |
| 补 manifest | 7 条知识登记，21 文件 = 21 条目全对齐 |
| 修 README | 去死 CLI，改为 flow-act 流程描述 |
| 修 flow-act 步骤 2 | 追加 manifest.jsonl 登记动作 |
