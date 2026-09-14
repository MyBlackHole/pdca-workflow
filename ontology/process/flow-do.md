---
schema: pdca.asset/v2
id: ontology:process/flow-do
type: process
semantic_kind: class
layer: Knowledge
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
status: active
authority: normative
revision: 4.0.0-rc.2
dcterms_modified: '2026-09-14'
summary: Do：只执行当前获准计划
---

# Do：只执行当前获准计划

## 进入前

当前Do run有真实用户phase_start操作；固定计划、oracle、输入及写域匹配，前置Plan已完成；Check后返修须有新的Do请求和run_id。原Agent／会话继续，不因进入Do新建。

## 本阶段自主执行

按SCENE建立真实本体／投影／审查对象。保存原输入、变更与执行证据，必要调试与重试在原目标范围内自主进行；先复现、提出可推翻假设、做最小区分实验，修复后运行必需回归。涉及存储／并发等专业检查按需读work-methods，不把角色名当专业证明。

建模写对象、关系、约束及实例／来源；投影保持固定源与映射；验证场景的Do执行只读审查。写业务、模型或过程记录之前核对集中records/resources内的预约和真实后端权利；多资源先完整取得，结果未知不盲重试。范围不足、新不可逆副作用或oracle改变先停并沟通，不自行扩张。

## 完成与等待

固定本run产物清单、实际命令／结果与限制；失败也保留，不能为成功而改expected。保存phase_completed并报告下一次Check将核验什么、使用哪版产物、有哪些缺项。随后等待用户启动Check。不得顺手写完Check和Act。
