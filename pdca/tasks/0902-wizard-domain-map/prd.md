# P1补强：wizard向导与多上下文

## 背景

T0487审查认定mattpocock P0已全吸收，剩余P1仅`wizard`（HTIL bash向导）与`domain-modeling多上下文`未覆盖。wizard填补“需人工置备凭证/切流/迁移”场景的可执行向导空白；多上下文解决单`CONTEXT.md`无法表达多bounded context路由的问题。二者均为高复用基础能力，本次合为一PDCA任务叶→根交付。

## 目标

- 新增 `ontology/domain/skill-wizard.md`（user-invoked），复刻mattpocock `wizard/template.sh` 6 helpers与四阶段流程，使HTIL步骤可一键生成可复用向导脚本
- 扩展 `ontology/domain/skill-domain-modeling.md` 与 `ontology/concept/domain-modeling.md`，增加 `CONTEXT-MAP.md` 多上下文路由段，明确何时单/多上下文

## 范围

- 输入：mattpocock/skills `wizard/SKILL.md + template.sh`、`domain-modeling/SKILL.md` CONTEXT-MAP段、`SKILLS-INDEX.md`
- 输出：1个domain节点 + 1个concept深化 + 1个template脚本 + 校验全绿
- 不做：不改 `task.schema.json`，不引入 teach 连续教学（P2），不改生产业务代码

## 功能需求

1. skill-wizard 节点：`invocation: manual`，描述四阶段（Scope→Map→Author→Verify），六helpers（stage/say/open_url/ask/ask_secret/write_env/set_secret/finish）与`bash -n`门禁，`TOTAL_STAGES`计数与 `STAGES` marker 不可手改
2. template.sh：拷贝至 `scripts/wizard-template.sh`，保留library区identical，只改STAGES示例，含 `ENV_FILE/WRITTEN_ENV/WRITTEN_SECRET/SKIPPED` 与跨平台open
3. 多上下文：`skill-domain-modeling.md` 增加CONTEXT-MAP文件结构与路由决策树；`concept/domain-modeling.md` 增加多上下文判定条件
4. 索引：`scripts/generate-skills-index.py` 重生成 `SKILLS-INDEX.md` 含新增skill

## 非功能需求

- 门禁零回退：`ontology-validate 0 issues, islands 0, bash -n scripts/wizard-template.sh` 通过
- 可观测：`ontology_graph --format dot` 可见新边

## 验收标准

- [ ] AC-1 wizard节点已创建：`ontology/domain/skill-wizard.md` 存在且 `ontology-validate` 通过，且 `grep -q "template.sh" ontology/domain/skill-wizard.md`
- [ ] AC-2 wizard模板已落地：`scripts/wizard-template.sh` 存在且 `bash -n scripts/wizard-template.sh` 通过，且含 `TOTAL_STAGES/marker/library identical` 校验
- [ ] AC-3 多上下文已深化：`skill-domain-modeling.md` 与 `concept/domain-modeling.md` 含 `CONTEXT-MAP.md` 且可被 `grep` 命中，经 `ontology-validate` 通过
- [ ] AC-4 索引与图谱一致：`SKILLS-INDEX.md` 含 `skill-wizard` 且 `ontology_graph --format summary` `islands:0`
- [ ] AC-5 收敛可验证：`convergence.json` 回链AC与证据，`validate-convergence valid:true` 且 `SKILLS-INDEX` 已登记

## 关联本体节点

```
ontology:domain/skill-wizard
ontology:domain/skill-domain-modeling
ontology:concept/domain-modeling
ontology:concept/domain-model
ontology:concept/writing-for-agents
ontology:concept/skill-mechanics
```

## 拆分映射

- wizard节点与模板 -> ontology:domain/skill-wizard
- 多上下文深化 -> ontology:concept/domain-modeling
- 索引与图谱校验 -> ontology:domain/skill-wizard

## 风险与对策

- 风险：template.sh library区被手改导致方差。对策：AC-2 校验library identical与bash -n
- 风险：CONTEXT-MAP与单CONTEXT混淆。对策：明确路由决策树，何时单/多

## 开放问题

- teach是否引入另开P2任务，本任务不做
