---
schema: pdca.asset/v1
id: ontology:domain/skill-project-goal
name: project-goal
summary: Define and track project goals for PDCA cycles.
description: |
  将项目使命用于新任务规划和历史知识复用
  
invocation: manual
type: domain
layer: Knowledge
status: active
relations:
  specializes:
    - ontology:concept/pdca-task
  relates_to:
    - ontology:concept/domain-modeling
    - ontology:concept/triage
  testable_signal: "检查本文件内容完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空且不含泛化短语"

---


--
schema: pdca.asset/v1
id: conclusion:T0060--07-26-记录-pdca-项目主要目标与效率使命
layer: experience
summary: 固化 PDCA 项目的效率、准确性、知识经验和 skills 持续增强使命
tags: [project-goal, pdca, knowledge, experience, skills, ai-efficiency]
scenarios: [default]
phases: [do, check, act]
applies_when: [评估项目功能范围和设计方向时]
excludes_when: []
source_ids: [evidence:T0060--07-26-记录-pdca-项目主要目标与效率使命:sha256:a75ac45b8ccce80cc15963fbcb38e4ca67692a2938528f76d18f5ccc998c2d77, evidence:T0060--07-26-记录-pdca-项目主要目标与效率使命:sha256:30b96d3159b2991199b090a6bc8fdb1baac3ab638a44f2d48535d8f64468ac16]
confidence: high
status: active
---

# 结论

## 假设验证

成立。项目目标已同时记录在 README 和核心知识层，明确 PDCA、知识与经验管理、skills 管理、历史复用及经验生成 skills 的持续增强闭环。

## 结果

- README 提供面向使用者的项目使命和能力方向。
- `ontology/domain/core-project-goal.md` 提供可被 AI 检索的结构化目标、适用条件和设计原则。
- 目标统一指向提高 AI 使用效率、事情处理效率、准确性和可复用性。

## 边界

本任务只记录目标，不新增自动知识投影或 skill 生成策略；后续实现应以该目标作为需求判断依据。

## 已知坑

项目目标定义与追踪过程中可能遇到的目标漂移、度量缺失等问题。后续发现问题时在此记录，确保技能使用过程中遇到的问题能够被跟踪和解决。
