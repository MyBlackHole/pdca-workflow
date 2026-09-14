---
schema: pdca.asset/v2
id: ontology:process/flow-plan
type: process
semantic_kind: class
layer: Knowledge
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
status: active
authority: normative
revision: 4.0.0-rc.1
dcterms_modified: '2026-09-14'
summary: Plan：与你确认问题，再形成计划
---

# Plan：与你确认问题，再形成计划

## 进入前

本任务独立Agent已绑定；用户看到当前Plan目标并作匹配phase_start操作。必须先确认问题、范围／非目标、预期交付及约束；已有明确答案引用，不重复盘问。未批准时只沟通，不建本体、不改业务文件。

## 本阶段自主执行

读取当前SCENE方法与固定来源，区分事实、假设和未知。寻找可复用模型，确认版本及限制；确定本节点职责、直接子seed或leaf理由。提出方案、实质取舍、可独立验收的产物、AC/oracle、测试／反例、写域和停止条件。

计划覆盖真实本体源或对应场景对象，不允许把任务名称当交付证明。发现原目标含糊先问具体问题，不能自己改成“只做知识地图”。不要强凑复杂方案，不为每个操作创建孩子。

## 完成与等待

保存plan、基线、输入清单和必要模型seed草案，标phase_completed。向用户报告计划及待确认Do对象（计划版本、写入对象、限制、预期产物），然后停止。Plan完成不是Do授权；用户已在本轮明确批准该固定Do对象时才可启动，不能用最初“开始”代替。
