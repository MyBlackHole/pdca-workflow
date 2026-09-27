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

## 方法边界

Do 的授权、Plan predecessor、返工准入、started receipt 与 running 状态由 CONFIRM/GATE/REWORK/
TRANSITION/STATE 处理。本页只定义 **Do run 已开始之后** 的实施方法。

## 本阶段自主执行

按SCENE建立真实本体／投影／审查对象。保存原输入、变更与执行证据，必要调试与重试在原目标范围内自主进行；先复现、提出可推翻假设、做最小区分实验，修复后运行必需回归。涉及存储／并发等专业检查按需读work-methods，不把角色名当专业证明。

建模写对象、关系、约束及实例／来源；投影保持固定源与映射；验证场景的Do执行只读审查。写业务、模型或过程记录之前核对集中records/resources内的预约和真实后端权利；多资源先完整取得，结果未知不盲重试。范围不足、新不可逆副作用或oracle改变先停并沟通，不自行扩张。

## 结果包

固定本 run 的产物清单、实际命令/结果、mapping、证据、失败与 limitation；
失败也保留，不能为成功而修改 expected/oracle。结果包交给 TRANSITION-01 记录本 run 完成，
不由 Do 方法自动启动 Check/Act。
