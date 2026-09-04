---
schema: pdca.asset/v1
id: ontology:pattern/testable-signal-to-test-derivation
type: pattern
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/testable-signal-to-test-derivation/1.0.0
summary: testable_signal 到测试用例派生模式（属性断言/契约测试/收敛验证）
relations:
  specializes:
    - ontology:pattern
  guides:
    - ontology:concept/pdca-task
    - ontology:domain/ai-efficiency
  relates_to:
    - ontology:concept/ontology-asset
    - ontology:concept/ontology-validate
    - ontology:concept/ontology-rule-attr-testable
    - ontology:domain/skill-ontology-check
attributes:
  - name: applicability
    desc: 将本体 attributes.testable_signal 转化为可执行测试的适用场景
    constraint: 适用于声明了 attributes 的 KnowledgeArtifact 节点（pattern/principle/pitfall/fact/decision）
    testable_signal: 运行 python3 scripts/ontology-validate.py --ontology-dir ontology 检查本节点及关联 KnowledgeArtifact 的 attributes.testable_signal 非空且不含泛化描述，且图谱中可经 specializes 追溯至 ontology:pattern
---

# testable_signal 到测试用例派生模式

将本体中每条 `attributes[].testable_signal` 转化为可执行测试断言的可复用模式。解决"70% 信号为泛化描述无法直接派生断言"的信号质量问题（见 T0461 背景：178 信号中 125 泛化集中于 domain 层）。

> **关系说明（AC-6 约束）**：本 pattern `guides` 指向合法 DomainEntity/Process 类 `ontology:concept/pdca-task` 与 `ontology:domain/ai-efficiency`；对 `ontology:concept/ontology-asset`（type: concept，属 meta-ontology 非 DomainEntity/Process）使用 `relates_to` 而非 `guides`，避免 `GUIDES_RANGE` 告警。详见 `scripts/ontology-validate.py` AC-6 校验逻辑与 `ontology/concept/ontology-asset.md`。

## 三种派生模式

### 模式一：属性断言（Attribute Assertion）

- **适用**：原子属性约束（如枚举、正则、数值范围、非空）
- **做法**：为 `attributes[].constraint` 与 `testable_signal` 编写直接断言脚本，输入为节点 frontmatter 解析结果，输出 pass/fail。
- **判定标准**：`testable_signal` 必须包含动词+对象+判定谓词（例："检查 X 是否满足 Y，不满足时报告 Z"），脚本退出非 0 即失败。
- **示例**：
  ```python
  # 校验 testable_signal 非泛化
  assert "由领域实践与测试验证" not in signal
  assert any(v in signal for v in ["检查", "校验", "运行", "断言", "验证"])
  ```
  - **正例**：`运行 python3 scripts/ontology-validate.py 检查 attributes.testable_signal 非空且不含泛化短语，0 issues 通过`
  - **反例**：`由领域实践与测试验证`（无动词、无判定）

### 模式二：契约测试（Contract Test）

- **适用**：声明 vs 实际一致性（如文档清单 vs 文件存在、术语表 vs 实际用词、声明的 seam vs 实际测试）
- **做法**：声明侧为机器可读清单（固定子节/固定前缀/词表），契约测试对比清单与实际产物，不测声明本身。
- **判定标准**：`testable_signal` 显式描述契约脚本与比对对象，脚本需区分"一致/缺失/不一致/无声明跳过"四类边界。
- **示例（契约测试模式本体）**：
  - `ontology:domain/ai-efficiency-contract-test-pattern` 精化后信号：`运行 scripts/seam_contract.py 校验 PRD 声明的 seam 清单与实际测试文件的一致性，且 SourceConsistency/DesignVocab 契约测试均通过，不一致时退出非0并报告缺失项`
  - 派生用例：`test_seam_contract.py` → 解析 `spec.md` 中 `- seam: <测试> -> <被测>` 行 → 断言文件存在+模块一致 → 缺失报 `SeamFileExistenceTest` 失败
  - 复用要点：契约测试引用实现纯函数（parse/check），不重复定义清单解析，避免两处漂移

### 模式三：收敛验证（Convergence Verification）

- **适用**：任务收敛链 `meta.convergence → PRD AC → evidence` 的闭环完整性
- **做法**：`convergence.json`（`pdca.convergence/v1`）逐条把 `task.json#meta.convergence` 回链到 `PRD ## 验收标准` 的 `AC-N` 与已登记 `evidence id`，由 `validate-convergence.py` 机器校验。
- **判定标准**：`testable_signal` 描述收敛验证命令与判定谓词，每条 AC 必须被至少一条非 map evidence 覆盖，`convergence map` 本身不作为通过证据。
- **示例**：
  - 信号：`执行 python3 scripts/validate-convergence.py --task-dir pdca/tasks/<task> 检查每条 meta.convergence 的 text 与 PRD 一致且 evidence_ids 均已通过 register-evidence 登记且 criteria 含对应 AC-N，valid=true`
  - 派生用例：`test_convergence.py` → 加载 `task.json` + `records/<record>/evidence/manifest.jsonl` + `convergence.json` → 断言 `AC-1..AC-N` 全覆盖且 evidence 文件存在且 digest 匹配

## 选择指南

| 信号特征 | 派生模式 | 典型动词 | 自动化载体 |
|---------|---------|---------|-----------|
| 单属性约束可独立判定 | 属性断言 | 检查/校验/断言 | `ontology-validate.py` + 自定义断言脚本 |
| 声明与实现需一致 | 契约测试 | 对比/校验/覆盖 | `seam_contract.py` / `check-design-vocab.py` 等 |
| 多产物需闭环回链 | 收敛验证 | 回链/覆盖/登记 | `register-evidence.py` + `validate-convergence.py` |

## 示范精化映射（AC-3）

- `ontology:domain/ai-efficiency-contract-test-pattern`：原 `由领域实践与测试验证` → 精化为契约测试型信号（见上模式二示例），派生 `seam_contract` 契约测试用例
- `ontology:domain/ai-efficiency-knowledge-assets-and-ai-workflow`：原泛化信号 → 精化为收敛验证型信号 `检查资产 source_ids 非空且可追溯至 Evidence/Experience，并通过 retrieval/groundedness/relevance/completeness 四维评估抽样查询达标`，派生来源链完整性与 RAG 评估用例

## 与门禁衔接

- `ontology:concept/ontology-rule-attr-testable`（AC-4）仅校验非空；本 pattern 提供"非泛化"的人工判定补充，由 `ontology:domain/skill-ontology-check` 步骤 6 执行
- 新增 KnowledgeArtifact 时，门禁先跑 `ontology-validate.py`（机检非空），再人工复核每条 `testable_signal` 是否符合本 pattern 三模式之一的"动词+对象+判定"结构，拒绝泛化描述

## 反模式

- 泛化信号：`由领域实践与测试验证`、`符合领域最佳实践`（无可执行谓词，无法派生断言）
- 伪具体：仅加"通过测试验证"但未指明测试脚本/断言对象，仍不可派生
- 声明即测试：只测 signal 字符串存在，不测 signal 描述的实际行为是否发生
