# ADR-0009: 执行循环与技能调用采用独立可验证合约

日期: 2026-07-31
状态: Accepted

## 背景

T0160 已将场景到 Do 路径的映射变为可执行 contract，但不能证明 development/bugfix 内部先测试后实现，也不能验证 flow/skill 是否以合法调用类型互相引用。现有 frontmatter 包含 asset 名称和 invocation 类型，SKILLS-INDEX 只展示它们，无法拒绝 direct manual edge 或失效用户入口。

## 候选方案

### A. 继续以 Markdown 约定执行顺序和调用类型

- 优点：无新增结构化资产。
- 缺点：顺序和边漂移只能由会话中的 AI 或人工发现，不能稳定故障注入。

### B. 扩展现有 route contract，或在每个 frontmatter 复制所有边和 alias

- 优点：文件数量较少。
- 缺点：把路径选择、循环顺序和调用图混为一体；复制 invocation 类型会产生多事实源。

### C. 两个独立 contract，frontmatter 继续负责 asset 类型

- 优点：执行顺序、alias/边和 asset 类型职责分离；resolver 可独立验证 Markdown 一致性和稳定错误码。
- 缺点：新增 schema、resolver、fixture 和 worker 迁移成本。

## 决策

选择 C。新增 execution contract 仅覆盖 development/bugfix 的 test-first 循环与最小验证语义；新增 invocation contract 仅保存 alias 与调用边。frontmatter 仍是 asset `name` 与 `invocation` 的唯一来源。flow/automatic asset 只能调用 automatic worker，manual asset 保持用户入口角色。

不新增所有外部任务的 phase-gate 回执 schema。真实 runner 出现前，contract fixture 只证明文档、导航和调用权限的确定性行为；后续若引入 runner，必须另行用配对实验验证真实效果。

## 影响

- 已在 P6 最终确认后实施 schema、resolver、flow/skill 迁移和 fault-injection fixture。
- 已更新内容 baseline，且由 resolver、fixture 和审计共同防止 baseline 掩盖行为回归。
- 这项决策提高流程可判定性，不得用作真实模型成功率提升的结论。
