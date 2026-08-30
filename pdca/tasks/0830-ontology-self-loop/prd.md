# 本体论闭环：知识表达·任务拆分·测试依据·AI权威

## 背景
T0399 完成了知识表达按本体论重构，建立了本体图（239 nodes/489 edges/0 islands）和 SSOT v3。本轮目标是实现本体论闭环：本体知识支撑 PDCA 流程、本体关系驱动任务拆分、本体描述派生测试用例、本体作为 AI 执行的权威依据，形成"基于本体 → 产生新本体知识"的自举循环。

## 目标
1. 本体知识支撑 PDCA 流程（PDCA 流程本体化）
2. 本体关系驱动任务拆分（WBS 自底向上）
3. 本体描述派生测试用例（attributes → testable_signal）
4. 本体作为 AI 执行权威依据（PDCA 流程、本体创建门禁）
5. 闭环验证：每项产出回链本体，每条本体知识可追溯来源

## 验收标准
- [ ] AC-1：PDCA 四流程（plan/do/check/act）建模为 ontology/process/ 实体，specializes pdca-process
- [ ] AC-2：任务拆分可由本体关系树（composed_of/specializes）自底向上生成 WBS
- [ ] AC-3：本体节点 attributes 的 testable_signal 可派生测试用例
- [ ] AC-4：PDCA 流程由本体支撑，ontology-validate 校验通过
- [ ] AC-5：本体创建门禁（ontology-check）基于本体自身定义，self-booting
- [ ] AC-6：闭环验证——每条本体知识可追溯来源，每项产出回链本体节点
- [ ] AC-7：登记证据 + 收敛映射 valid:true

## 关联本体节点
```
ontology:concept/pdca-task
ontology:concept/pdca-continuous-improvement
ontology:concept/pdca-phase
ontology:domain/out-of-scope
```

## 非目标
- 不引入 OWL/RDF 形式本体与推理机
- 不改变现有 ontology/ 目录结构

## 设计要点
- 闭环本质：本体 → 知识 → 流程 → 任务 → 测试 → 验证 → 本体，每一步都产出新的本体知识
- 自举（self-booting）：ontology-validate.py 的规则本身由本体定义，校验器基于本体运行
- 权威性：AI 执行 PDCA 流程时，以本体为唯一权威依据，不依赖硬编码规则
- 可追溯：每条本体知识有 source_task 回链，每项产出有 ontology_node_type 回链