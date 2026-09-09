---
schema: pdca.asset/v1
id: ontology:concept/pdca-acceptance-criterion
type: concept
layer: Knowledge
summary: PDCA 验收标准（AC）元概念
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/pdca-acceptance-criterion/1.0.0
relations:
  specializes:
  - ontology:concept/pdca
---
# pdca-acceptance-criterion

验收标准（AC）元概念。PRD 中以 `- [ ] AC-x:` 复选框声明的可验证条件。

- **含义**：每个 AC 必须能被至少一条 evidence 映射支撑；`conclusion.md` 中每个 AC 判定行须可 grep 到证据 ID。
- **理由**：把"完成"定义为可复核的证据映射，而非主观声称。

## AC章节映射规则（research类）

- **逐章映射**：research类任务的AC必须逐源文档章节编号映射（如“方案§3.2→AC-2”），每个AC注明覆盖的源章节；`conclusion.md`中AC判定行须能grep到源章节号。
- **禁用不可判定词**：AC正文禁用“完整、齐全、全面、充分”。
  - 坏例子：“落改点清单完整”。
  - 好例子：“S3落改点覆盖方案§3.2三态与§3.8清单表达”。
- **动因**：T2107的AC-2教训（来源records/T2107-0909-guomi-storage-research/conclusion.md）：AC-2“落改点清单”表述不可判定，复核依赖人工解读源章节，故新增本规则。

