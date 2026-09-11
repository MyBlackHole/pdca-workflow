# 3.3复用与演进单元测试

20个案例覆盖建模检索、采用、局部扩展、共享候选/发布、跨树迁移与返工。每例有固定正反例、预期、错误规则控制、观测和返工路径；共96个模型向量。模型只检验显式有限fixture语义，不替代实际文字兼容性审查或宿主授权。

| 案例 | 被测边界 | 权威 | 模型向量 |
|---|---|---|---:|
| [U01](U01.md) | 双工作树复用定义但不复用任务 | REUSE-01 / TREE-01 / TASK-01 | 4 |
| [U02](U02.md) | 同一树重复实例化不增加组成父 | REUSE-01 / TREE-01 | 4 |
| [U03](U03.md) | 复用优先但不伪造全库检索 | REUSE-01 | 5 |
| [U04](U04.md) | 同名不同单位或适用域不能直接复用 | REUSE-01 / ONTOLOGY-01 | 5 |
| [U05](U05.md) | 局部细化不能覆盖共享字节 | REUSE-01 / RESOURCE-01 | 4 |
| [U06](U06.md) | 更严格输入不等于可替换原接口 | REUSE-01 / CASE-01 | 4 |
| [U07](U07.md) | 旧树固定版本不追随latest | REUSE-01 / EVOLVE-01 | 5 |
| [U08](U08.md) | 只固定顶层文件不足以固定语义 | REUSE-01 / EVOLVE-01 | 4 |
| [U09](U09.md) | active与候选不能代替采用证据 | REUSE-01 / ADOPT-01 | 5 |
| [U10](U10.md) | 扩展细节的变更分类与case版本 | EVOLVE-01 / TEST-01 | 5 |
| [U11](U11.md) | 新建身份与已存在版本不能被覆盖 | EVOLVE-01 | 5 |
| [U12](U12.md) | 串行发布仍必须比较候选基准 | EVOLVE-01 / RESOURCE-01 | 5 |
| [U13](U13.md) | 合并后旧审查不能继续批准新内容 | EVOLVE-01 / REVIEW-01 | 4 |
| [U14](U14.md) | 发布授权是精确对象与动作的许可 | EVOLVE-01 / CONFIRM-01 / RESOURCE-01 | 6 |
| [U15](U15.md) | 不可变版本和完整提交先于发现视图 | EVOLVE-01 / RECOVERY-01 | 5 |
| [U16](U16.md) | 部分采用不能删除适用必需保证 | REUSE-01 / NODE-01 | 4 |
| [U17](U17.md) | 共享案例规范不共享PASS和授权 | REUSE-01 / TEST-01 / CONFIRM-01 | 6 |
| [U18](U18.md) | 发布新版本不等于强制迁移所有树 | ADOPT-01 / TREE-01 | 5 |
| [U19](U19.md) | 采用索引缺口和私有范围不可隐藏 | ADOPT-01 | 5 |
| [U20](U20.md) | 已知错误阻断采用但不造成全局交付死锁 | ADOPT-01 / EVOLVE-01 / REWORK-01 | 6 |

全部真实宿主结果NOT_RUN。维护者可使用独立附件验证器求值，不把Python放进工作流。外部结果与case的host_result分离。旧[控制案例](../protocol-regression/README.md)、[行为案例](../behavior-cases.md)和[范围案例](../../examples/range-task/README.md)继续回归。

双树实际字节fixture、显式版本与候选冲突演练见[示例](../../examples/ontology-reuse/README.md)。完整生产3N任务仍需真实宿主/Agent与用户确认，未生成示例成功任务。
