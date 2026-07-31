# T0161 Do 阶段双轴审查

审查范围：execution/invocation contract、schema、公共 resolver、flow/skill 迁移、fixture、内容审计接入和测试。

## 标准轴

- 解析器使用实际仓库文件、JSON schema 和稳定 JSON 错误码；路径经根目录约束，子进程调用未使用 shell。
- execution contract 通过公共 route resolver 交叉校验 route ID/anchor，避免两个各自有效的 contract 无声漂移。
- invocation contract 从 frontmatter 读取 asset name/invocation 类型；contract 只保存 alias 与调用边，避免类型事实复制。
- document verifier 对阶段 marker 要求恰好出现一次并保持顺序；对所有显式 skill 路径要求已声明边且目标为 automatic worker。
- 代码审查期间发现并修复：route cross-contract fail-open、entry document 可误指向 automatic asset、schema 未独立约束 canonical phases、重复 marker 可绕过顺序检查。

结论：Blocking 0，未发现残留的安全、正确性或可维护性阻断项。

## 规范轴

| 验收项 | 审查结论 |
| --- | --- |
| AC-1 至 AC-3 | versioned execution schema/resolver 覆盖 development/bugfix、非法场景、route/document/marker 漂移。 |
| AC-4 | flow-do A/B 均先 Seam/失败测试，再最小实现或修复、切片定向验证、最终全量验证和双轴审查。 |
| AC-5 至 AC-7 | invocation 类型由 frontmatter 唯一提供；alias、显式调用边、未知/非法边和文档漂移均由 resolver 验证。 |
| AC-8 至 AC-9 | triage/domain-modeling/handoff 抽为 automatic worker；manual 入口保留；ask-matt 仅暴露 `/grill` 等已声明 alias。 |
| AC-10 至 AC-12 | 公共 fixture 调用实际 resolver；单元测试、预算审计、索引、doctor、compile 均在验证矩阵中通过。 |

## 残余边界

本实现只保证显式文档、合约和阶段顺序的确定性约束，不测量真实模型成功率、token、延迟或成本；这与 PRD 的范围外声明一致，不作为通过结论的外推。
