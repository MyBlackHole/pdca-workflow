---
schema: pdca.asset/v1
id: R0136-pdca-state-contract
phase: check
source_ids: [state-contract-fixtures, deletion-manifest, deletion-result]
---

## 上下文

检查严格状态合约、阶段门禁和不兼容历史清理是否满足 T0136 PRD。

## 假设与结果

- 严格 schema 与语义校验能拒绝伪确认、越界证据、时间倒置和矛盾状态：通过。
- 清理可限制为经过摘要锁定的明确目录并保护长期资产：通过。
- 13 个不兼容归档任务已删除；清理后复扫目标为 0。

## 分析

15 个单元测试全部通过。证据 schema 强制验收条件映射，证据路径解析后必须位于对应 record 的 `evidence/` 内；阶段转换只允许相邻推进并校验待写入对象。删除前逐项核验 manifest、数量和 digest，`records/`、`knowledge/`、`pdca/journal/` 未进入目标。

## 适用边界

11 个历史目录原本未被 Git 跟踪，依据用户明确授权完成不可逆删除。活跃任务区仍有 16 个旧格式目录，严格校验会拒绝它们；因不属于归档清理 manifest，本轮未删除且未添加兼容规则。

## 下一轮建议

仅在新增真实失败模式时增加不变量或夹具，避免无消费者的兼容分支。
