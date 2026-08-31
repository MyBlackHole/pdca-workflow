# 调研报告：补完 domain 层 testable_signal 并打通三模式派生链路

## 调研目标

1. 量化 77 个无 `testable_signal` 的 domain 文件现状
2. 评估 `testable-signal-to-test-derivation` 三模式在 `skill-testing-strategy.md` 中的可引用性
3. 梳理 `ontology-clash-check.py` 升级为阻断门禁的方案

## 方法

1. 扫描 `ontology/domain/` 下全部 201 个 `.md` 文件，筛选无 `testable_signal` 的文件
2. 按主题域分类统计
3. 检查 `skill-testing-strategy.md` 对 `testable-signal-to-test-derivation` 的引用现状
4. 检查 `scripts/ontology-clash-check.py` 的当前行为

## 发现

### 77 个无信号文件分布

| 主题域 | 文件数 | 代表文件 |
|--------|--------|---------|
| other | 51 | `ai-efficiency.md`, `control-plane-nonblocking-ingress.md`, `skill-advance-phase.md` 等 |
| core | 2 | `core.md`, `core-tech-poc.md` |
| backup | 2 | `backup-crypto.md`, `backup.md` |
| pg/mysql/lmdb/nbu | 4 | `pg.md`, `mysql.md`, `lmdb.md`, `nbu.md` |
| report/rpc/tls/tooling | 6 | `report-center.md`, `rpc-rdbcomm.md`, `tls.md`, `tooling.md` |
| 其余 | 12 | 各 1 个文件 |

### 关键发现

1. **51 个文件属于 `other` 类别**，主要是独立主题入口文件（`ai-efficiency.md`, `control-plane-nonblocking-ingress.md` 等），这些文件作为主题概述，需补充概述性 `testable_signal`
2. **`skill-testing-strategy.md` 未引用 `testable-signal-to-test-derivation` 三模式**——当前仅描述测试框架选择和最佳实践，未涉及从本体信号到测试用例的派生链路
3. **`ontology-clash-check.py` 当前行为为"提示不阻断"**——`skill-to-tickets.md` 明确注释"该检查仅提示、不阻断拆解产出"

### 精化策略

| 文件类型 | 精化策略 |
|----------|---------|
| 主题入口文件（51 个 other） | 补充概述性 `testable_signal`，引用该主题的验收标准和验证命令 |
| 核心入口文件（`core.md`, `backup.md` 等） | 引用对应子主题的验证命令和检查清单 |
| 工具配置文件 | 引用工具版本约束和配置验证命令 |

## 结论与建议

### 结论

1. **77 个文件需补充 `testable_signal`**，其中 51 个为 `other` 类别，可按主题域批量精化
2. **`skill-testing-strategy.md` 需新增三模式引用章节**，打通 `testable_signal` → 测试用例链路
3. **`ontology-clash-check.py` 需升级为阻断门禁**，从"提示不阻断"改为"不通过则阻断"

### 建议

- **Phase 1 (research → development)**：按主题域批量精化 77 个文件的 `testable_signal`
- **Phase 2**：在 `skill-testing-strategy.md` 新增三模式章节
- **Phase 3**：升级 `ontology-clash-check.py` 为阻断门禁

## 参考资料

- `ontology/domain/` 下 77 个无信号文件
- `ontology/pattern/testable-signal-to-test-derivation.md`：三模式派生规范
- `ontology/domain/skill-testing-strategy.md`：测试策略（当前未引用三模式）
- `scripts/ontology-clash-check.py`：当前提示不阻断行为
- `skill-to-tickets.md`：本体一致性预检逻辑