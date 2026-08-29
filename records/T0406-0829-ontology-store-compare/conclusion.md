# T0406 结论（Check 阶段）

- record: T0406-0829-ontology-store-compare
- 阶段结论：调研比较完成，推荐方案已定，证据链收敛验证通过。

## 验收对照
| AC | 内容 | 证据 |
|----|------|------|
| AC-1 | ≥5 维度对比报告 + 真实样本 | `t0406-report` |
| AC-2 | 原型转 OWL/TTL 映射完整度与脆弱度 | `t0406-prototype` |
| AC-3 | 明确推荐方案 + 理由/风险 | `t0406-report` §5 |
| AC-4 | ONTOLOGY_GUIDE 草案（兼容吸收版） | `t0406-guide` |
| AC-5 | 声明不动 SSOT v3/现有节点 | `t0406-report` §6 |
| AC-6 | 证据登记 + convergence map | manifest + `convergence-map` |

`validate-convergence` 结果：`valid: true, issues: []`。

## 推荐方案：兼容吸收（不替换 SSOT v3）
- 机器权威保持不变：`pdca.asset/v1` frontmatter + YAML `relations:` 块（受 `ontology-validate` 强制校验）。
- 人读增强可选：frontmatter 增 `domain`/`docType`/`tags`；正文 `[[wikilink]]` 作为 `relations` 的**派生视图**（非关系来源），并加 lint 防漂移。
- `_meta.yaml` 改为声明"文件夹为人类阅读索引；语义权威 = frontmatter + relations"。
- 可视化诉求由规划中的 `scripts/ontology_graph.py`（ADR-0031 的 pdca-graph）满足，输出 Obsidian 兼容图谱 + 孤岛检测。

## 关键证据（来自原型实测）
1. 提案在 frontmatter `superClass` 与正文 wikilink 双重表达同一关系 → 生成重复/歧义三元组。
2. 自由文本谓词（`subClassOf`/`guidedBy`/`dependsOn`）非受控词汇 → 需额外归一化层，否则 `pdca:subClassOf`≠`rdfs:subClassOf`。
3. 提案属性仅标注"数据类型 X"，丢失 SSOT `attributes` 的 `desc`/`testable_signal` 语义。
4. 正文 wikilink 拼写错误无内置校验（SSOT 的 AC-2 引用空悬检查依赖 `relations`，对正文 wikilink 无效）。

## 风险与边界
- 若正文 wikilink 与 `relations` 并存且无同步校验，会重演"双重表达"分裂 → 必须规定 `relations` 为唯一来源。
- 直接替换 SSOT 的代价（全量重写节点 + 重写 `ontology-validate`/`transition-phase` + 破坏 T0402/T0405 资产）远高于收益，且无证据显示提案在可校验性/OWL 升级上更优。

## Verdict
- outcome: **confirmed**
- 不动 SSOT v3、不改任何现有节点与脚本（见 AC-5）。
- 后续若采纳 `ONTOLOGY_GUIDE` 草案，应另立任务/ADR，不在本任务内实施。
