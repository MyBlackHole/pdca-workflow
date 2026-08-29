# T0404 设计草案（P2 对齐，未终审）

## 目标
构建**半自动本体归纳辅助**：从多源输入（knowledge 草稿 / 代码 / 外部资料）按规则与启发式抽取候选 frontmatter 骨架（`type` / `specializes` / 候选 `guides`），生成 PR/差异供人工 review，**不自动落盘本体**（保持 HITL）。

## 范围
- **入**：可插拔输入适配器；首版实现 `knowledge/` 草稿适配器，代码 / web 适配器为扩展点（满足"任何来源"的架构承诺）。
- **出**：候选 frontmatter 骨架 + 落盘为 PR/差异（不直写 `ontology/`）。
- **机制**：规则 / heuristic 优先（确定性、可复现）。
- **不出**：`attributes.testable_signal` 等属性由人工补；不自动生成以避免失真。

## 架构（三模块 + 复用）
- `adapter` 层：source → 归一化中间表示（候选节点列表）。
- `induction` 层：heuristic 规则——类型推断（受控词汇）、`specializes` 候选（按共性聚类/命名）、`guides` 候选（指向领域/过程实体）。
- `output` 层：生成 frontmatter + 写入 PR/差异。
- 复用 `scripts/ontology-validate.py` 作为候选落盘前的校验闸门。

## 初拟验收标准（P3 细化）
- AC-1：给定 `knowledge/` 草稿，产出候选 frontmatter，其 `type` 在受控词汇。
- AC-2：候选 `specializes` 经 `ontology-validate` 不报 `CYCLE` / `DANGLING_REF`。
- AC-3：产出为 PR/差异格式，不直接修改 `ontology/`。
- AC-4：规则/heuristic 确定性可复现（同输入同输出）。

## 关键取舍
- "任何来源"由适配器抽象承载，首版聚焦 `knowledge/` 草稿，代码/web 留接口，避免首版过载。
- 产出仅骨架，属性人工补，符合 SSOT v3"属性机读可派生测试"但生成责任留人。
- 与 T0402 的 `design.md §8 归纳工作流（AI）` 衔接：把"AI 手动归纳"升级为"工具辅助 + 人工审核"闭环。
