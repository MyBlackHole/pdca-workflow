---
schema: pdca.asset/v1
id: ontology:concept/pdca-acceptance-criterion
type: concept
layer: Knowledge
summary: PDCA 验收标准（AC）元概念
status: active
relations:
  specializes:
  - ontology:concept/pdca
---
# pdca-acceptance-criterion

验收标准（AC）元概念。PRD 中以 `- [ ] AC-x:` 复选框声明的可验证条件。

- **含义**：每个 AC 必须能被至少一条 evidence 映射支撑；`conclusion.md` 中每个 AC 判定行须可 grep 到证据 ID。
- **理由**：把"完成"定义为可复核的证据映射，而非主观声称。

