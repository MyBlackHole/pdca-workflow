---
schema: pdca.asset/v1
id: ontology:domain/skill-teach
name: teach
summary: Teach the user a new skill or concept, within this workspace.
description: Teach the user a new skill or concept, within this workspace.
invocation: manual
type: domain
layer: Knowledge
status: active
relations:
  specializes:
    - ontology:concept/pdca-task
  relates_to:
    - ontology:concept/domain-modeling
    - ontology:concept/skill-mechanics
    - ontology:concept/writing-for-agents
attributes:
  - name: applicability
    desc: 教授新技能/概念的多session有状态教学
    constraint: 用户显式要求学习某主题时触发；以当前目录为教学工作空间
    testable_signal: "检查本文件含 Teaching Workspace 且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验 attributes 非空"
  - name: workspace_structure
    desc: 教学工作空间结构
    constraint: 含 MISSION.md/reference/*.html/RESOURCES.md/learning-records/*.md/lessons/*.html/assets/* /NOTES.md
    testable_signal: "grep -q 'Teaching Workspace' ontology/domain/skill-teach.md 且 grep -q 'MISSION.md' ontology/domain/skill-teach.md"
  - name: lesson_discipline
    desc: 课程纪律
    constraint: 每课为单HTML、自包含、短赢、ZPD内、链引用与主源、提醒追问
    testable_signal: "grep -q 'Zone Of Proximal Development' ontology/domain/skill-teach.md"
---

# Teach — 连续教学（Teaching Workspace）

> 来源 `mattpocock/skills` `productivity/teach`（stateful, disable-model-invocation）。当前目录即教学工作空间，学习状态以文件落盘，多 session 推进。

## Teaching Workspace

- `MISSION.md`：学习动机与目标，牵引所有教学；格式见 `MISSION-FORMAT.md`
- `reference/*.html`：压缩知识——cheat sheets/算法/语法/术语表，美观可打印，跨 lesson 复用
- `RESOURCES.md`：资源清单，附引用格式 `RESOURCES-FORMAT.md`
- `learning-records/*.md`：学习记录（类ADR），`0001-<slug>.md` 递增，格式 `LEARNING-RECORD-FORMAT.md`，用于计算 ZPD
- `lessons/*.html`：课程主单元，单HTML自包含，`0001-<slug>.html` 递增，短赢、ZPD内、链锚点、荐主源、提醒追问
- `assets/*`：lesson间复用组件（样式/quiz/模拟器/图表），默认复用，先读 assets 再写 lesson
- `NOTES.md`：用户偏好与工作笔记 scratchpad

## Philosophy

学习三支：**Knowledge**（高信任源获取）、**Skills**（交互课习得）、**Wisdom**（社群实战中生）。资源未丰时先丰 `RESOURCES.md`，不信参数知识。

**Fluency vs Storage Strength**：流畅 ≠ 存储。以 desirable difficulty 建存储：retrieval practice / spacing / interleaving。

## Lessons

美观（Tufte）、短赢、ZPD内、链其他 lesson/reference、荐高信任主源、提醒追问。必要时 `open` 课文件。复用 `assets`，新可复用件落 `assets/` 而非内联。

## Assets

首件为共享样式表；后续按需扩展组件库。

## The Mission

每课紧扣 mission；mission不清先追问用户补 `MISSION.md`；mission变更需更新并记 learning record，确认后生效。

## Zone Of Proximal Development

无指定主题时读 `learning-records` + mission 定 ZPD，教授最相关且 ZPD内的一课。

## Knowledge / Skills / Wisdom

- **Knowledge**：课前仅教够用知识，附引用，difficulty敌
- **Skills**：difficulty工具，经交互+紧反馈环（quiz/实操）练存储；quiz答案等长无提示
- **Wisdom**：社群委派——荐高声誉论坛/subreddit/本地班，尊重用户拒绝

## Reference Documents

课中同步产 reference，压缩可快查（语法/算法/流程/术语表），lesson 链入。

## 已知坑

- 未丰资源时不空讲；每主张附主源引用
- 未清 mission 不开课，先补 MISSION.md
