---
schema: pdca.asset/v1
id: knowledge.ai-efficiency.contract-test-pattern
summary: 契约测试模式——用"机器可读清单 + 一致性断言"把文档/术语/seam 声明与实际实现的一致性做成可回归验证的硬指标（T0231/T0232/T0233 三例已验证）
tags: [ai-efficiency, contract, testing, pdca, seames, vocabulary]
scenarios: [plan, check]
phases: [plan, check]
source_ids: [T0233-0809-seam-contract, T0231-0809-followup-frontier-batch-spread, T0232-0809-ticket-dag-design-twice]
---

# 契约测试模式（Contract Test Pattern）

## 核心做法

把"声明 vs 实际"的一致性做成**机器可读 + 契约测试守护**的硬指标。
三个已验证实例：

| 实例 | 声明 | 清单格式 | 契约测试 | 结果 |
|------|------|---------|---------|------|
| **source 术语**（T0231） | 交互记录用 `source: "grilling"` | 文档内固定字符串 | 断言 flow 文档不残留 `"grill"` | SourceConsistencyContractTest |
| **词汇契约**（T0232） | 接口设计文档只用 module/interface/seam/adapter/depth | 禁用词表（component/service/API/boundary） | `check-design-vocab.py` 拒绝表外词 | DesignVocabContractTest |
| **seam 契约**（T0233） | PRD 声明测试接缝 | `- seam: <测试> -> <被测>` 行 | `seam_contract.py` 断言文件存在 + 模块一致 | SeamFileExistenceTest |

## 模式要点

1. **机器可读清单**。声明必须是确定性可解析的格式（固定子节/固定前缀/固定
   词表），自由文本无法被契约测试守护。
2. **一致性断言**。契约测试对比"声明"与"实际"（实际测试文件、实际文档、
   实际词表），不测声明本身。
3. **范围限定**。契约只约束有实际产物可对比的场景（如 seam 契约只限
   development/bugfix），避免假阴性。
4. **不追溯**。历史产物缺清单信息即跳过，契约守护未来（同 T0232 schema
   旧任务不强制补齐）。
5. **去重**。契约测试应引用实现的纯函数（parse/check），不重复定义，
   避免两处漂移。

## 可证明方式

- 纯函数（解析 + 校验）四类边界 fixture：正常/缺失/不一致/无声明跳过。
- 与 T0230 轮数模型测试、T0232 DAG 测试同构：确定性、无模型依赖、可回归。

## 日志约定（与门禁兼容）

- seam 契约放 flow-plan P3.5（P3 后 P4 前），P6 门禁检查子节存在。
- `scripts/seam_contract.py` 可独立运行（stdin/文件 + --base-dir）。
- register-evidence 的 `--replace` 要求新 `--file` 不同名（改名 v2 规避）。

## 复用场景

- 任何"文档声明 vs 实际实现"的一致性守护：API 合约、路由契约、命名规范。
- CI 门禁：对每个 development spec 运行 seam_contract.py。
