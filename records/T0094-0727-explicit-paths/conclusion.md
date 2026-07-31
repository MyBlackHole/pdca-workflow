---
schema: pdca.asset/v1
id: T0094-0727-explicit-paths
layer: experience
summary: 所有路径引用统一加 $PDCA_HOME 前缀
tags: [paths, PDCA_HOME, consistency]
---

# 结论: T0094 — 路径显式化

## 目标
消除隐含路径假设，19 个文件中的 74 处路径引用全部显式化。

## 结果
- 所有 flows/ skills/ pdca/ records/ templates/ 引用都以 $PDCA_HOME/ 为前缀
- 外部项目模式依赖此变更：$PDCA_HOME 指向管理中心
