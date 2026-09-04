---
schema: pdca.asset/v1
id: ontology:domain/skill-bug-analysis
name: bug-analysis
summary: Analyze bug reports and code failures to identify root causes and patterns.
description: 用于缺陷、异常和回归问题的根因分析；先收集证据，再区分假设、实验和过程原因。
invocation: manual
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/skill-bug-analysis/1.0.0
relations:
  specializes:
    - ontology:concept/pdca-task
  relates_to:
    - ontology:concept/domain-modeling
    - ontology:concept/failure-mode
  testable_signal: "运行 grep -q '缺陷根因分析' ontology/domain/pdca/skill-bug-analysis.md && python3 scripts/ontology-validate.py --ontology-dir ontology 2>&1 | grep -q 'OK'"

---


---
name: bug-analysis
description: 用于缺陷、异常和回归问题的根因分析；先收集证据，再区分假设、实验和过程原因。
---

# 缺陷根因分析

科学方法内核（Zeller 科学调试法）：观察失败 → 可证伪假设 → 预测 → 实验 → 结论。根因即“无之则失败不发生的最小差异”（closest possible world），须经实验验证，推理 alone 不得确立因果。

1. 明确现象、影响范围、首次出现时间和可复现条件（现象≠根因，先写失败的回归信号）。
2. 建立单一可验证、可证伪假设，记录双向预测与反证条件（格式：“若 X 是根因，则改 Y 失败消失、改 Z 失败加剧”）。
3. 收集最小充分证据：日志、输入、版本、调用路径和失败样本。
4. 用二分、对照实验或最小复现缩小根因范围，禁止直接把猜测当结论；每次实验单变量。
5. 区分三类根因：假设/设计错误、实现/环境错误、流程/证据遗漏；**根因≠现象**，必须追到代码/配置/流程层面且与诊断假设的双向预测一致。
6. 记录修复建议、回归验证和仍未排除的风险。

输出应包含：现象、复现、证据、假设、实验、根因、修复方向、验证标准。

## 修复前确认门禁

输出“根因+修复方向+验证标准”后，须向用户展示并获 `fix_confirmation:confirmed`（`captured:true`，CLI 落盘）方可进入代码修改；未确认不得改代码。

```bash
python3 "$PDCA_HOME/scripts/append-confirmation.py" --task-dir <task-dir> --source fix_confirmation --response confirmed --summary "<根因+方案+影响范围>"
```

## 已知坑

- 先收集证据再下结论，勿凭直觉臆测根因；忽略环境差异（版本/平台）常误导定位。
- 根因≠现象，未经实验验证的“根因”是猜测；未获 `fix_confirmation` 就改代码属绕过门禁。
