# 子任务拆分详细设计

## 概述

本文档详细描述了在本体树驱动的多代理 PDCA 工作流中的子任务拆分机制。当任务过大、边界不清或无法独立验收时，系统支持在实施阶段动态拆分子任务，以提高执行效率和质量。

## 1. 与现有设计的集成

### 1.1 节点状态索引扩展

在 `ontology-node-state` 中添加拆分相关字段：

```yaml
schema: pdca.ontology-node-state/v7
work_id: <本体树所属工作>
tree_revision: <冻结树版本>
node_id: <稳定节点 ID>
node_kind: container | implementable | aggregate

ontology_ref: <固定本体节点与 ontology_revision>
parent_ref: <父节点>
dependency_refs: []

implementation:
  task_refs: []
  delivery_refs: []
  mapping_refs: []
  state: not_ready | ready | awaiting_confirmation | running | delivered | failed | stale
  
  # 新增：任务拆分信息
  split_info:
    is_split: false
    parent_task_ref: null
    subtask_refs: []
    split_reason: null
    split_timestamp: null
    split_depth: 0
    max_depth_allowed: 3

verification:
  task_refs: []
  review_refs: []
  evidence_refs: []
  state: not_ready | ready | awaiting_confirmation | running | verified | failed | stale
  
  # 新增：验证拆分信息
  verification_split_info:
    is_split: false
    parent_verification_ref: null
    sub_verification_refs: []

derived_status: <由事实派生的总状态>
blocking_reasons: []
stale_reason: null
recomputed_from: []
recomputed_at: <时间>

confidence:
  overall: 0.0
  breakdown:
    - category: interface
      score: 0.0
      count: 0
    - category: constraint
      score: 0.0
      count: 0
    - category: test
      score: 0.0
      count: 0
  trend: stable
  last_updated: null
```

### 1.2 PDCA 集成点

```yaml
pdca_integration:
  split_decision_point:
    phase: "Do"
    trigger: "agent.confidence < 0.7 OR task.estimatedLOC > 500 OR task.estimatedTime > 40h"
    action: "请求用户批准拆分"
    approval_required: true
    
  split_execution_point:
    phase: "Do"
    action: "执行拆分，创建子任务"
    updates:
      - "更新父任务 split_info"
      - "创建子任务记录"
      - "更新依赖关系"
      
  split_coordination_point:
    phase: "Do"
    action: "协调子任务执行"
    updates:
      - "跟踪子任务进度"
      - "协调依赖关系"
      - "整合子任务结果"
```

## 2. 拆分标准

### 2.1 代码规模标准

```yaml
code_size_thresholds:
  small_task:
    max_loc: 100
    max_files: 3
    max_dependencies: 2
    description: "单一函数或小型模块"
    
  medium_task:
    max_loc: 500
    max_files: 10
    max_dependencies: 5
    description: "多函数模块或小型服务"
    
  large_task:
    max_loc: 1000
    max_files: 20
    max_dependencies: 10
    description: "复杂模块或中型服务"
    
  extra_large_task:
    max_loc: "> 1000"
    max_files: "> 20"
    max_dependencies: "> 10"
    description: "必须拆分"
```

### 2.2 复杂度标准

```yaml
complexity_metrics:
  cyclomatic_complexity:
    low: "< 10"
    medium: "10-20"
    high: "> 20"
    
  cognitive_complexity:
    low: "< 10"
    medium: "10-20"
    high: "> 20"
    
  dependency_depth:
    shallow: "< 3"
    moderate: "3-5"
    deep: "> 5"
    
  interface_count:
    simple: "< 5"
    moderate: "5-10"
    complex: "> 10"
```

### 2.3 时间标准

```yaml
time_thresholds:
  quick_task:
    max_hours: 4
    description: "可一次完成"
    
  medium_task:
    max_hours: 16
    description: "1-2天工作量"
    
  long_task:
    max_hours: 40
    description: "一周工作量，建议拆分"
    
  extended_task:
    max_hours: "> 40"
    description: "必须拆分"
```

## 3. 拆分流程

### 3.1 拆分决策流程

```yaml
split_decision_process:
  step_1:
    name: "评估任务"
    action: "计算任务规模、复杂度、时间估算"
    output: "task_assessment_report"
    
  step_2:
    name: "检查拆分条件"
    action: "对比拆分标准，判断是否需要拆分"
    output: "split_recommendation"
    conditions:
      - "task.size > threshold"
      - "task.complexity > threshold"
      - "task.estimated_time > threshold"
      - "agent.confidence < 0.7"
      
  step_3:
    name: "用户确认"
    action: "展示拆分建议，等待用户批准"
    output: "user_approval"
    required: true
    
  step_4:
    name: "执行拆分"
    action: "按规则拆分任务，创建子任务"
    output: "subtasks_created"
    
  step_5:
    name: "协调安排"
    action: "安排子任务执行顺序和依赖"
    output: "execution_plan"
```

### 3.2 拆分方法

```yaml
split_methods:
  by_responsibility:
    description: "按职责拆分"
    example: "用户服务拆分为：认证、授权、用户管理"
    criteria: "每个子任务有单一职责"
    
  by_feature:
    description: "按功能拆分"
    example: "订单系统拆分为：创建、查询、取消、退款"
    criteria: "每个子任务实现独立功能"
    
  by_layer:
    description: "按层次拆分"
    example: "Web应用拆分为：前端、API、业务逻辑、数据访问"
    criteria: "每个子任务负责一个层次"
    
  by_dependency:
    description: "按依赖拆分"
    example: "核心逻辑拆分为：独立模块、依赖模块、集成模块"
    criteria: "减少子任务间依赖"
```

### 3.3 拆分约束

```yaml
split_constraints:
  depth_constraints:
    max_depth: 3
    depth_levels:
      level_1:
        name: "原始任务"
        description: "用户初始请求"
      level_2:
        name: "主要拆分"
        description: "第一次拆分产生的子任务"
        max_subtasks: 5
      level_3:
        name: "次要拆分"
        description: "子任务进一步拆分"
        max_subtasks: 3
        requires_special_approval: true
        
  size_constraints:
    min_node_size:
      loc: 50
      files: 1
    max_node_size:
      loc: 1000
      files: 20
    balance_goal:
      target_loc: 200-300
      target_files: 5-10
      
  dependency_constraints:
    max_dependencies_per_task: 5
    max_dependents_per_task: 10
```

## 4. 错误处理机制

### 4.1 错误类型分类

```yaml
error_types:
  split_errors:
    - type: "split_decision_failed"
      description: "拆分决策失败"
      severity: "high"
      
    - type: "split_approval_timeout"
      description: "用户批准超时"
      severity: "medium"
      
    - type: "split_execution_failed"
      description: "拆分执行失败"
      severity: "high"
      
  subtask_errors:
    - type: "subtask_dependency_conflict"
      description: "子任务依赖冲突"
      severity: "high"
      
    - type: "subtask_resource_conflict"
      description: "子任务资源冲突"
      severity: "medium"
      
    - type: "subtask_timeout"
      description: "子任务执行超时"
      severity: "high"
      
  integration_errors:
    - type: "integration_test_failure"
      description: "集成测试失败"
      severity: "high"
      
    - type: "interface_inconsistency"
      description: "接口不一致"
      severity: "high"
```

### 4.2 错误处理策略

```yaml
error_handling_strategies:
  split_failure:
    strategy: "checkpoint_recovery"
    actions:
      - "保存拆分状态到 checkpoint"
      - "恢复时从 checkpoint 继续"
      - "未完成拆分标记为 stale"
    rollback:
      enabled: true
      trigger: "user.request OR critical_failure"
      actions:
        - "合并子任务回父任务"
        - "恢复到拆分前状态"
        - "更新相关索引"
        
  subtask_failure:
    strategy: "cascade_failure"
    actions:
      - "暂停所有依赖子任务"
      - "通知父任务"
      - "请求用户决策：重试/跳过/终止"
    escalation:
      enabled: true
      trigger: "failure_count > 3"
      actions:
        - "升级到父任务处理"
        - "请求用户干预"
        
  conflict_resolution:
    strategy: "hierarchical_resolution"
    levels:
      - level: 1
        name: "自动协调"
        trigger: "子任务间可自动解决"
        actions:
          - "调整执行顺序"
          - "共享只读资源"
          
      - level: 2
        name: "父任务裁决"
        trigger: "自动协调失败"
        actions:
          - "父任务分析冲突"
          - "提出解决方案"
          - "执行裁决"
          
      - level: 3
        name: "用户决定"
        trigger: "父任务无法裁决"
        actions:
          - "向用户报告冲突"
          - "提供选项"
          - "等待用户决定"
```

### 4.3 恢复机制

```yaml
recovery_mechanism:
  checkpoint_management:
    frequency: "每次拆分决策后"
    storage: "集中 records"
    retention: "永久保留"
    
  recovery_procedures:
    split_recovery:
      trigger: "拆分中断"
      steps:
        - "加载最新 checkpoint"
        - "验证拆分状态"
        - "继续未完成拆分"
        - "更新索引"
        
    subtask_recovery:
      trigger: "子任务失败"
      steps:
        - "分析失败原因"
        - "决定恢复策略"
        - "执行恢复操作"
        - "更新状态"
```

## 5. 版本控制

### 5.1 版本管理策略

```yaml
version_management:
  versioning_strategy:
    parent_task: "保持原版本"
    subtask_versioning: "parent_version.split_number"
    example: "1.0.0 → 1.0.0.1, 1.0.0.2, 1.0.0.3"
    
  version_components:
    major: "重大功能变更"
    minor: "新功能添加"
    patch: "bug修复"
    split: "任务拆分"
    
  version_history:
    tracking: "每次拆分都记录版本历史"
    storage: "集中 records"
    queryable: true
```

### 5.2 拆分历史追踪

```yaml
split_history:
  recording:
    required_fields:
      - "timestamp"
      - "reason"
      - "subtasks_created"
      - "user_approval"
      - "split_depth"
      - "parent_task_id"
      
    optional_fields:
      - "split_method"
      - "estimated_benefit"
      - "actual_benefit"
      
  storage:
    location: "集中 records/split_history"
    format: "JSON"
    versioned: true
    
  query:
    capabilities:
      - "按时间查询拆分历史"
      - "按原因查询拆分历史"
      - "按任务查询拆分历史"
      - "统计拆分效果"
```

### 5.3 回滚机制

```yaml
rollback_mechanism:
  triggers:
    - "user.request"
    - "critical_failure"
    - "split_benefit_not_achieved"
    
  procedures:
    simple_rollback:
      condition: "子任务未开始执行"
      actions:
        - "删除子任务记录"
        - "恢复父任务状态"
        - "更新索引"
        
    complex_rollback:
      condition: "子任务已开始执行"
      actions:
        - "暂停所有子任务"
        - "保存当前状态"
        - "合并子任务结果"
        - "恢复父任务状态"
        - "更新索引"
        
    partial_rollback:
      condition: "部分子任务完成"
      actions:
        - "保留已完成子任务"
        - "回滚未完成子任务"
        - "调整父任务状态"
        - "更新索引"
```

## 6. 资源管理

### 6.1 Agent 分配策略

```yaml
agent_allocation:
  strategy: "demand_based"
  
  rules:
    - "每个子任务分配独立 Agent"
    - "父任务协调资源使用"
    - "避免资源冲突"
    
  allocation_process:
    step_1:
      name: "评估资源需求"
      action: "分析子任务资源需求"
      output: "resource_requirements"
      
    step_2:
      name: "分配 Agent"
      action: "根据需求分配 Agent"
      output: "agent_allocation"
      
    step_3:
      name: "协调资源使用"
      action: "协调子任务间资源使用"
      output: "resource_coordination"
```

### 6.2 并行执行管理

```yaml
parallel_execution:
  configuration:
    max_concurrent_subtasks: 3
    min_time_between_starts: "1 minute"
    
  resource_sharing:
    shared_resources:
      - type: "readonly"
        example: "本体定义、接口契约"
        sharing: "允许并行访问"
        
    exclusive_resources:
      - type: "writable"
        example: "代码文件、配置文件"
        sharing: "独占访问"
        
    coordination_mechanism:
      - "共享状态通过父任务协调"
      - "独占资源通过锁机制管理"
      - "冲突时通过协调机制解决"
```

### 6.3 资源池管理

```yaml
resource_pool:
  agent_pool:
    min_agents: 1
    max_agents: 5
    scaling_strategy: "on_demand"
    
    scaling_rules:
      - trigger: "pending_subtasks > 3"
        action: "增加 Agent"
        increment: 1
        
      - trigger: "idle_agents > 2"
        action: "减少 Agent"
        decrement: 1
        
    monitoring:
      metrics:
        - "agent_utilization"
        - "task_completion_rate"
        - "resource_conflict_count"
```

## 7. 性能考虑

### 7.1 拆分开销分析

```yaml
overhead_analysis:
  decision_overhead:
    time: "< 5 seconds"
    complexity: "O(n) where n = task attributes"
    
  coordination_overhead:
    time: "< 10% of task time"
    complexity: "O(m) where m = number of subtasks"
    
  integration_overhead:
    time: "< 15% of total task time"
    complexity: "O(k) where k = number of dependencies"
```

### 7.2 优化策略

```yaml
optimization_strategies:
  caching:
    enabled: true
    strategy: "cache split decisions"
    benefits:
      - "避免重复计算"
      - "提高决策速度"
      
  asynchronous:
    enabled: true
    strategy: "异步协调机制"
    benefits:
      - "减少等待时间"
      - "提高并行效率"
      
  batching:
    enabled: true
    strategy: "批量处理子任务"
    benefits:
      - "减少协调开销"
      - "提高整体效率"
```

### 7.3 成本效益分析

```yaml
cost_benefit_analysis:
  split_benefits:
    - "并行执行提高速度"
    - "降低单个任务复杂度"
    - "提高失败隔离能力"
    - "提高代码质量"
    
  split_costs:
    - "协调开销"
    - "集成复杂度"
    - "管理成本"
    - "通信开销"
    
  break_even_analysis:
    min_benefit_threshold: "20% 效率提升"
    max_cost_threshold: "15% 额外开销"
    decision_rule: "if benefit > cost then split"
```

## 8. 测试策略

### 8.1 测试层次

```yaml
testing_levels:
  unit_tests:
    scope: "拆分决策逻辑"
    coverage: "90%"
    examples:
      - "测试拆分条件判断"
      - "测试拆分方法选择"
      - "测试依赖关系解析"
      
  integration_tests:
    scope: "拆分后协调机制"
    coverage: "80%"
    examples:
      - "测试子任务间协调"
      - "测试结果聚合逻辑"
      - "测试错误处理流程"
      
  performance_tests:
    scope: "拆分性能影响"
    coverage: "关键路径"
    examples:
      - "测试拆分决策时间"
      - "测试协调机制开销"
      - "测试并行执行效率"
      
  acceptance_tests:
    scope: "用户验收"
    coverage: "100%"
    examples:
      - "测试用户批准流程"
      - "测试拆分历史记录"
      - "测试回滚操作"
```

### 8.2 测试用例设计

```yaml
test_case_design:
  positive_tests:
    - "正常拆分流程"
    - "并行执行流程"
    - "结果聚合流程"
    
  negative_tests:
    - "拆分失败处理"
    - "子任务失败处理"
    - "冲突解决处理"
    
  boundary_tests:
    - "最小任务拆分"
    - "最大任务拆分"
    - "最大拆分深度"
    
  performance_tests:
    - "大量子任务拆分"
    - "高并发执行"
    - "资源紧张情况"
```

## 9. 示例

### 9.1 正常流程示例

```yaml
normal_flow_example:
  scenario: "用户认证系统拆分"
  
  initial_task:
    name: "用户认证系统"
    estimated_loc: 800
    estimated_files: 15
    estimated_time: 30 hours
    
  split_decision:
    trigger: "estimated_time > 20h"
    decision: "建议拆分"
    user_approval: true
    
  split_execution:
    subtasks:
      - name: "认证核心"
        estimated_loc: 300
        dependencies: []
        
      - name: "授权管理"
        estimated_loc: 250
        dependencies: ["认证核心"]
        
      - name: "会话管理"
        estimated_loc: 250
        dependencies: ["认证核心"]
        
  execution_plan:
    order: "串行执行"
    sequence: ["认证核心", "授权管理", "会话管理"]
    
  result:
    total_time: 25 hours
    improvement: "17% faster"
```

### 9.2 失败处理示例

```yaml
failure_handling_example:
  scenario: "子任务依赖冲突"
  
  conflict_detection:
    subtasks: ["授权管理", "会话管理"]
    conflict: "同时修改同一文件"
    
  resolution_process:
    level_1: "自动协调失败"
    level_2: "父任务裁决"
    decision: "调整执行顺序"
    
  result:
    resolution: "串行执行"
    impact: "增加2小时"
    user_approval: true
```

### 9.3 并行执行示例

```yaml
parallel_execution_example:
  scenario: "无依赖子任务并行执行"
  
  subtasks:
    - name: "模块A"
      dependencies: []
      estimated_time: 4 hours
      
    - name: "模块B"
      dependencies: []
      estimated_time: 5 hours
      
    - name: "模块C"
      dependencies: []
      estimated_time: 3 hours
      
  execution_plan:
    order: "并行执行"
    estimated_total_time: 5 hours
    
  result:
    actual_total_time: 6 hours
    improvement: "40% faster than sequential"
```

## 10. 度量标准

### 10.1 效果度量

```yaml
effectiveness_metrics:
  time_metrics:
    - "拆分后任务完成时间减少比例"
    - "拆分后总项目时间减少比例"
    - "拆分决策时间"
    
  quality_metrics:
    - "拆分后代码质量提升"
    - "拆分后测试覆盖率提升"
    - "拆分后缺陷密度降低"
    
  efficiency_metrics:
    - "并行执行效率提升"
    - "资源利用率提升"
    - "协调成本占比"
```

### 10.2 基准测试

```yaml
benchmarking:
  baseline:
    metrics:
      - "拆分前任务完成时间"
      - "拆分前代码质量"
      - "拆分前测试覆盖率"
      
  comparison:
    metrics:
      - "拆分后任务完成时间"
      - "拆分后代码质量"
      - "拆分后测试覆盖率"
      
  improvement_target:
    time_reduction: "20%"
    quality_improvement: "15%"
    coverage_improvement: "10%"
```

### 10.3 持续改进

```yaml
continuous_improvement:
  feedback_loop:
    - "收集拆分效果数据"
    - "分析拆分决策准确性"
    - "优化拆分策略"
    
  adjustment_mechanism:
    trigger: "效果未达预期"
    actions:
      - "调整拆分阈值"
      - "优化协调机制"
      - "改进测试策略"
      
  documentation:
    - "记录拆分经验"
    - "更新最佳实践"
    - "分享成功案例"
```

## 11. 实现步骤

### 11.1 第一阶段：基础功能

1. **实现拆分决策逻辑**
   - 定义拆分条件
   - 实现评估算法
   - 创建决策接口

2. **实现拆分执行逻辑**
   - 设计拆分方法
   - 实现子任务创建
   - 更新节点状态索引

3. **实现基本协调机制**
   - 设计协调协议
   - 实现状态跟踪
   - 创建报告接口

### 11.2 第二阶段：错误处理

1. **实现错误检测**
   - 设计错误类型
   - 实现检测机制
   - 创建错误报告

2. **实现错误处理**
   - 设计处理策略
   - 实现恢复机制
   - 创建回滚功能

3. **实现冲突解决**
   - 设计解决层次
   - 实现协调机制
   - 创建裁决接口

### 11.3 第三阶段：性能优化

1. **实现缓存机制**
   - 设计缓存策略
   - 实现缓存存储
   - 创建缓存查询

2. **实现并行优化**
   - 设计并行策略
   - 实现并发控制
   - 创建资源管理

3. **实现监控功能**
   - 设计监控指标
   - 实现数据收集
   - 创建报告生成

### 11.4 第四阶段：测试和文档

1. **实现测试套件**
   - 设计测试用例
   - 实现自动化测试
   - 创建测试报告

2. **编写文档**
   - 编写用户手册
   - 编写开发者文档
   - 创建示例教程

3. **发布和部署**
   - 准备发布版本
   - 部署到生产环境
   - 收集用户反馈

## 12. 总结

本设计提供了完整的子任务拆分机制，包括：

1. **与现有设计的集成**：通过扩展节点状态索引和 PDCA 集成点
2. **明确的拆分标准**：基于代码规模、复杂度、时间
3. **清晰的拆分流程**：评估→决策→确认→执行→协调
4. **完善的错误处理**：错误分类、处理策略、恢复机制
5. **完整的版本控制**：版本管理、历史追踪、回滚机制
6. **有效的资源管理**：Agent 分配、并行执行、资源池
7. **全面的性能考虑**：开销分析、优化策略、成本效益
8. **系统的测试策略**：测试层次、测试用例、测试方法
9. **实用的示例**：正常流程、失败处理、并行执行
10. **明确的度量标准**：效果度量、基准测试、持续改进

这个设计确保了子任务拆分功能的可实施性、可维护性和可扩展性，为复杂任务的分解和管理提供了完整的解决方案。