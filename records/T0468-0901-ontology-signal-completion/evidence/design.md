# 本体 testable_signal 补完与三模式派生链路设计（T0468）

> 决策：补完 77 个 domain 文件的 testable_signal 条目，在 skill-testing-strategy.md 引用三模式，升级 ontology-clash-check.py 为阻断门禁。

## 1. 补信号方案

基于 T0467 精化模板，为 77 个无信号文件补充 testable_signal：

| 策略 | 适用文件 | 信号模板 |
|------|---------|---------|
| 主题概述 | 51 个 other 类别 | 检查本文件 {关键词} 相关章节的完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空且不含泛化短语 |
| 核心入口 | core.md, backup.md 等 | 引用对应子主题的验证命令和检查清单 |
| 工具配置 | tooling.md, build-config.md 等 | 引用工具版本约束和配置验证命令 |

## 2. 三模式引用

在 skill-testing-strategy.md 新增章节，引用 testable-signal-to-test-derivation 三模式：

| 信号特征 | 派生模式 | 自动化载体 |
|----------|---------|-----------|
| 单属性约束可独立判定 | 属性断言 | ontology-validate.py + 自定义断言脚本 |
| 声明与实现需一致 | 契约测试 | seam_contract.py / check-design-vocab.py |
| 多产物需闭环回链 | 收敛验证 | register-evidence.py + validate-convergence.py |

## 3. 门禁升级

ontology-clash-check.py 从"提示不阻断"升级为阻断门禁：
- 发现冲突时 exit code=1
- 无冲突时 exit code=0
- skill-to-tickets.md 同步更新

## 4. 验证方案

- AC-1: 77 个文件补充 testable_signal，ontology-validate.py 通过
- AC-2: skill-testing-strategy.md 引用三模式，ontology-validate.py 通过
- AC-3: ontology-clash-check.py 升级，ontology_graph 0 islands
