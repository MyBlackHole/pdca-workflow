# T0161 研究依据

## 外部比较

`mattpocock/skills` 的 `implement` 将已约定的测试 seam、频繁的定向验证、最终全量测试和 review 串成一个实现入口；其 `to-tickets` 还把调用/执行单元设计为可独立验证的垂直切片。该项目的用户调用与模型调用分层是本任务调用图的直接参考，而不是完整流程的替代。

- [上游 README：可组合技能与调用模型](https://github.com/mattpocock/skills)
- [上游 implement](https://github.com/mattpocock/skills/blob/main/skills/engineering/implement/SKILL.md)
- [上游 to-tickets](https://github.com/mattpocock/skills/blob/main/skills/engineering/to-tickets/SKILL.md)

## 本地事实

- `flow-do` 目前在 A2/B2 描述编码或修复，随后才在 A3/B3 描述 TDD/回归测试。
- `tdd` 已定义预先约定的 Seam 和 Red-Green，但其相对 flow 顺序未被机器验证。
- `SKILLS-INDEX` 仅从 frontmatter 展示 invocation 类型；manual direct edge 与 `/grill-me` 失效入口不会被现有检查拒绝。
- T0160 已证明“独立 JSON contract + 公共 resolver + 真实文档/故障夹具”可在不引入模型 runtime 的前提下提高流程 oracle 的可证伪性。

## 证据边界

本任务可证明 contract、导航和文档一致性检查能捕获指定漂移。它不能证明真实模型成功率、token、延迟或成本提升；这些需要固定 Agent runner、保留任务集和前后配对实验。
