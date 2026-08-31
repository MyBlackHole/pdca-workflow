---
schema: pdca.asset/v1
id: ontology:domain/ai-efficiency-contract-test-pattern
type: domain
layer: Knowledge
status: active
summary: 契约测试模式（Contract Test Pattern）
domain:
- ontology:domain/ai-efficiency
relations:
  specializes:
  - ontology:domain/ai-efficiency
  relates_to:
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 领域知识适用场景
  constraint: 见正文
  testable_signal: 运行 scripts/seam_contract.py 校验 PRD 声明的 seam 清单与实际测试文件的一致性，且契约测试套件 SourceConsistencyContractTest/DesignVocabContractTest/SeamFileExistenceTest 全部通过，不一致时退出非0并报告缺失项
---

---
schema: pdca.asset/v1
id: knowledge.ai-efficiency.contract-test-pattern
summary: 契约测试模式——用"机器可读清单 + 一致性断言"把文档/术语/seam 声明与实际实现的一致性做成可回归验证的硬指标（T0231/T0232/T0233 三例已验证，T0240 扩展为仓库级批量门禁）
tags: [ai-efficiency, contract, testing, pdca, seames, vocabulary]
scenarios: [plan, check]
phases: [plan, check]
source_ids: [T0233-0809-seam-contract, T0231-0809-followup-frontier-batch-spread, T0232-0809-ticket-dag-design-twice, T0240-0809-seam-ci-gate, T0241-0809-seam-doctor-gate, T0244-0809-pdca-flow-impl-review]
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

## 仓库级批量门禁（T0240 扩展）

单任务门禁（P6）防单个任务漏检；**仓库级批量门禁**防跨任务回归：

- `check-seam-contracts.py` 扫描活跃任务 spec 批量校验，任一失败退出非 0。
- **范围限定到活跃任务**（archive 不扫）：归档 spec 的 seam 指向的历史
  测试文件可能随外部项目生命周期移除（T0234 FastAPI 实例），且归档 spec
  为不可变记录不应修改——含归档校验会持续误报。
- 开发期即拦截：新任务 PRD 声明 seam 后、测试落地前，门禁即报
  "测试文件缺失"，防"声明了 seam 但测试未落地"的漏检。
- base-dir 默认 = 仓库根（不随调用者 cwd 变化），避免 --root 与
  --base-dir 不一致的配置坑。

**自动触发点（T0241）**：仓库无 CI 基础设施时，把契约校验接入既有体检入口
`pdca-doctor.py --json`（新增 `seam_contracts` 段，失败即 valid=false）。
doctor 是每次体检都跑的既有入口，无需 CI 也能自动拦截漂移。校验脚本用
`Path(__file__).parent` 定位（与被检 root 解耦），避免临时 root 无 scripts/
导致加载失败。

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

## CI 就绪度审查（T0244）

落地 CI 前审查 PDCA 流程实现，三个结论：

1. **门禁完整**：`pdca_core.gate_issues()` 覆盖 5 阶段 16 项检查
   （plan: final_confirmation；do: PRD+evidence+convergence；check:
   conclusion+verdict+check_confirmation；act: disposition；archive: 全量），
   无可绕过路径。`validate-workflow.py --gate` 可单任务批检。
2. **doctor 与门禁分离**：`pdca-doctor.py` 是"体检"（capabilities/references/
   timeline/seam），**不调用 gate_issues**——不检查任务门禁合规
   （convergence/verdict/disposition 存在性）。CI 若只跑 doctor 会漏掉
   门禁违规。
3. **CI 就绪度**：可直接落地 CI，但需补 doctor 门禁段。方案 A（推荐）：
   doctor 新增 `gate` 段聚合活跃任务 gate_issues（与 seam_contracts 同构）；
   方案 B：CI 额外跑 validate-workflow.py --gate。
   成本极低：纯 Python 标准库 + pytest，脚本均 `Path(__file__).parent`
   定位（T0241 已解耦，无 cwd 假设）。

**经验教训**：体检入口（doctor）与门禁校验（gate_issues）是两个不同概念，
接入 CI 时要确认自动化入口覆盖的是哪一类，避免"跑通了但没检查该检查的"。
