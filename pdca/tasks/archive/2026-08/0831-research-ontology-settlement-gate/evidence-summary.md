# T0465 实施证据摘要

## 修改文件

### 1. skill-research 补强
- 文件：`ontology/domain/skill-research.md`
- 新增：`## 本体沉淀决策（Act 门禁）` 章节，含分流判定（3条）、决策记录（conclusion.md + disposition）、本体化执行、校验命令
- 验证：`grep "本体沉淀决策" ontology/domain/skill-research.md` 应命中

### 2. flow-act 补强
- 文件：`ontology/process/flow-act.md`
- 阶段步骤 1/2/3 均追加 research 本体沉淀约束，门禁新增 `check-research-ontology-settlement`
- 验证：`grep "check-research-ontology-settlement" ontology/process/flow-act.md` 应命中

### 3. 校验脚本
- 文件：`scripts/check-research-ontology-settlement.py`
- 功能：校验 research 任务在 act/archive 的本体沉淀决策（conclusion ##本体沉淀 + disposition 显式词 + ontology 引用）
- 验证：见下回归

### 4. 正例本体
- 文件：`ontology/domain/tool-production-readiness.md`
- 验证：`ontology-validate OK`，`ontology_graph 350 nodes / 759 edges / 0 islands`

## 回归验证

### 正例：T0464 补本体后
```
$ python3 scripts/check-research-ontology-settlement.py --task-dir pdca/tasks/archive/2026-08/0831-prod-tool-dev-requirements-research
OK: research settlement decision present for T0464 (record=T0464-0831-prod-tool-dev-requirements-research, phase=archive)
exit:0
```

### 负例：漏本体沉淀章节
```
RESEARCH_SETTLEMENT_MISSING: conclusion.md missing '## 本体沉淀' section
RESEARCH_SETTLEMENT_MISSING: meta.disposition.reason must contain 'ontology' or 'records-only'
exit:1
```

### 正例：records-only 显式决策
```
OK: research settlement decision present for T9999 (record=FAKE-001, phase=act)
exit:0
```

## 关联
- 来源：T0464 复盘
- 正例：ontology:domain/tool-production-readiness
