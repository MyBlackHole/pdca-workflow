---
schema: pdca.asset/v1
id: ontology:domain/skill-wizard
name: wizard
summary: Generate an interactive bash wizard that walks a human through steps only they can perform.
description: Generate an interactive bash wizard that walks a human through steps only they can perform. Use when provisioning infrastructure, setting up credentials or CI secrets, walking an unfamiliar third-party dashboard, or running a one-off migration or cutover. Don't invoke this for steps the agent can perform itself.
invocation: manual
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/skill-wizard/1.0.0
relations:
  specializes:
    - ontology:concept/pdca-task
  relates_to:
    - ontology:concept/domain-modeling
    - ontology:concept/skill-mechanics
    - ontology:concept/writing-for-agents
attributes:
  - name: applicability
    desc: 人才可执行的置备/迁移/切换向导
    constraint: 仅当步骤必须由人类在外部控制台/凭证/网络中操作时触发；agent可自执行的步骤不走wizard
    testable_signal: "检查本文件内容完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空且不含泛化短语"
  - name: library_identical
    desc: 向导库区identical
    constraint: template.sh 的 STAGES marker 以上 library 区与上游 identical，不手改；仅改STAGES区
    testable_signal: "运行 bash -n scripts/wizard-template.sh 检查语法通过，且 grep -q 'Wizard library' scripts/wizard-template.sh"
  - name: stage_discipline
    desc: 单阶段单聚焦与进度可视
    constraint: 每个stage()清屏仅显示当前步骤，TOTAL_STAGES等于stage数，finish汇总WRITTEN_ENV/SECRET/SKIPPED
    testable_signal: "检查 scripts/wizard-template.sh 含 TOTAL_STAGES 与 finish 且通过 bash -n"
---

# Wizard — HTIL 向导

> 来源 `mattpocock/skills` `skills/engineering/wizard`（template.sh）与 T0487 P1 gap。Wizard 是 bash 脚本，将“人类才可做”的繁琐手动流程（置备基础设施、配凭证/CI secrets、走第三方控制台、一次性迁移/切流）变为分步可回放的向导，打开URL、告知点击与复制点、捕获值、写入 `.env`/GitHub secrets、每阶段确认、显示剩余阶段。

## 触发条件

当 provisioning / credentials / CI secrets / 第三方控制台 / 迁移/切流必须由人类操作时触发。不为 agent 可自执行的步骤生成向导。

## 四阶段流程

1. **Scope**：读 `.env/.env.example/README/docker-compose*/framework config/.github/workflows/*`（每个 `secrets.*`/`vars.*` 都是需捕获的值）；对迁移类，厘清现态→目标→不可逆动作；输出有序阶段列表与每阶段捕获值（来源/落点/.env或secret/是否secret），与用户确认
2. **Map**：为每阶段写人类精确路径（URL→点击→复制→填变量），未知UI不编造
3. **Author**：拷贝 `scripts/wizard-template.sh`，替换示例stage为真实stage，设 `TOTAL_STAGES`，使用 helpers：`stage/say/step/open_url/ask/ask_secret/write_env/set_secret/set_var/pause/confirm`；library区 identical 不改
4. **Verify**：`bash -n <script>` + `shellcheck`（如有）+ `chmod +x`，静态追踪每值落点与 `secrets.*` 一致性，不端到端执行

## 已知坑

- library区 identical 是方差控制核心，手改即漂移
- `ask_secret` 用于敏感值，`write_env` 持久化，`set_secret` 仅CI必需值
- ephemeral 默认，提交仅当需复用路径时并在README链接

## 与 ontology 衔接

- `ontology:concept/skill-mechanics` invocation=user-invoked
- `ontology:pattern/ontology-modular-reference` 清单透传：向导不单独立清单节点，阶段清单在领域attributes承载
