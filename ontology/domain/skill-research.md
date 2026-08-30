---
schema: pdca.asset/v1
id: ontology:domain/skill-research
name: research
summary: Conduct research on domain topics and best practices.
description: Investigate a question against high-trust primary sources and capture findings as a cited Markdown file in the repo. Use when the user wants a topic researched, docs or API facts gathered.
invocation: manual
type: domain
layer: Knowledge
status: active
relations:
  specializes:
    - ontology:concept/pdca-task
  relates_to:
    - ontology:concept/domain-modeling
    - ontology:concept/domain-model
---

---
name: research
description: Investigate a question against high-trust primary sources and capture findings as a cited Markdown file in the repo. Use when the user wants a topic researched, docs or API facts gathered.
---

1. Identify the primary sources — official docs, source code, specs, first-party APIs. Follow every claim to the source.
2. Investigate the question systematically.
3. Write findings to `research-report.md`:
   ```markdown
   ## 调研目标
   ## 方法
   ## 发现
   ## 结论与建议
   ## 参考资料
   ```
4. 每条关键结论附至少一条**可复核验证途径**（重跑命令/SQL/复现步骤/可回看的 file:line 引用）；无法给出途径的结论降级为"待验证假设"并标注置信度。
5. Register via `$PDCA_HOME/skills/register-evidence/SKILL.md`.

## Exit

Findings written to research-report.md and registered as evidence.

## 已知坑

- 只采信高信任 primary source；二手转述/低信源结论须标注置信度，勿当作事实。
