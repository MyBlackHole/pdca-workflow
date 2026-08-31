# 本体 testable_signal 精化与派生链路设计（T0467）

> 决策：以 `tool-production-readiness` 为精化模板，将 120 个泛化信号精化为"动词+对象+判定"结构，并在 4 个已有具体信号的 domain 节点上验证三模式派生。

## 1. 精化方法

### 1.1 泛化信号识别

基于 research 阶段的扫描结果：
- 131 个 testable_signal 条目中，120 个（91.6%）为泛化描述
- 泛化短语："由领域实践与测试验证"、"符合领域最佳实践"
- 77 个文件完全不含 testable_signal

### 1.2 精化模板

以 `tool-production-readiness.md` 的 4 条信号为模板：

| 泛化信号 | 精化后信号 |
|----------|-----------|
| 由领域实践与测试验证 | 检查本文件"成熟度模型"章节含L1/L2/L3/L4四级定义，且每级含判定条件与门禁清单，与 records/.../research-report-v2.md 附录A一致 |
| 由领域实践与测试验证 | 校验本文件"检查清单"章节含B1/B2/B3/B4四级清单，且每条含勾选框与可重跑验证命令（如 trivy fs、syft、cosign verify、tool --json \| jq），与 records/.../checklist.md 条目一致 |

精化规则：
1. **动词开头**：检查/校验/运行/断言/验证/对比/抽样
2. **对象明确**：指定文件章节、维度、属性名
3. **判定条件**：含具体工具命令、路径引用或数值标准
4. **可回归验证**：信号描述的验证动作可通过脚本重跑

### 1.3 分域精化策略

| 域 | 信号数 | 精化策略 |
|----|--------|---------|
| core-* | ~30 | 按模块（btree/node/merge/journal 等）逐模块精化，引用具体代码路径 |
| backup-crypto-* | ~7 | 按加密算法（GM/SM/TAOCP）逐算法精化，引用 openssl/tpm2 工具命令 |
| benchmark-* | ~4 | 按基准测试场景（noise/streaming/writer-pool）精化，引用 pytest 脚本 |
| ai-efficiency-* | ~11 | 按评估维度（execution/friendliness/contract 等）精化，引用 seam_contract.py |
| build-config-* | ~2 | 按构建工具（xmake/go-module）精化，引用 cargo/go build 命令 |
| 其他 | ~66 | 按文件主题精化，引用具体验证命令或文件路径 |

## 2. 三模式派生验证

### 2.1 模式映射

| 具体信号 | 派生模式 | 典型动词 | 自动化载体 |
|----------|---------|---------|-----------|
| `tool-production-readiness` 维度信号 | 属性断言 | 检查/校验 | `ontology-validate.py` + 自定义断言脚本 |
| `ai-efficiency-contract-test-pattern` | 契约测试 | 对比/校验 | `seam_contract.py` |
| `ai-efficiency-knowledge-assets-and-ai-workflow` | 收敛验证 | 回链/覆盖 | `validate-convergence.py` |
| `skill-retrospective` | 属性断言 | 检查/验证 | 自定义断言脚本 |

### 2.2 验证方案

在以下 4 个节点上运行三模式派生验证：
1. `tool-production-readiness.md`：属性断言模式
2. `skill-retrospective.md`：属性断言模式
3. `ai-efficiency-contract-test-pattern.md`：契约测试模式
4. `ai-efficiency-knowledge-assets-and-ai-workflow.md`：收敛验证模式

### 2.3 验证标准

- 每个模式至少产出 1 条可运行的断言脚本
- 脚本退出码为 0 表示验证通过
- `ontology-validate.py` 通过且 `ontology_graph` 0 islands

## 3. 任务拆分

### 3.1 子任务 1：泛化信号精化

- 目标：将 120 个泛化信号精化为可执行断言
- 产出：精化后的 domain 节点文件
- 验收：`ontology-validate.py` 通过，精化后信号不含泛化短语

### 3.2 子任务 2：三模式派生验证

- 目标：在 4 个 domain 节点上验证三模式派生
- 产出：断言脚本 + 验证结果
- 验收：每个模式至少 1 条可运行断言，脚本退出码为 0

### 3.3 子任务 3：补充无信号文件

- 目标：为 77 个无信号文件补充 `testable_signal` 条目
- 产出：补充后的 domain 节点文件
- 验收：所有 domain 文件至少含 1 条 `testable_signal` 条目

## 4. 与流程衔接

- `skill-ontology-check` 步骤 6 的人工门禁将自动适配精化后的信号
- `testable-signal-to-test-derivation` 模式将作为精化信号的派生规范
- `ontology-clash-check.py` 确保精化后的信号不与既有本体节点冲突