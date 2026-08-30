# T0423 Triage Brief：knowledge/ 领域知识迁入本体后删除

- 触发：用户确认"先迁入本体再删（新任务）"——将 `knowledge/` 的 123 个领域知识文件析出为 `ontology/domain/*` 节点，校验通过后删除 `knowledge/`，使本体成为唯一知识权威。
- 现状：`knowledge/` 含 123 个真实领域知识文件（非 PDCA 元知识），分布在约 28 个域目录：
  `ai-efficiency/ backup/ backup-crypto/ benchmark/ build-config/ cli-help/ control-plane-nonblocking-ingress/ core/ core-tech-poc/ data-formats/ debugging/ editor-config/ kernel-debugging/ linux-epoll-eventloop/ lmdb/ mysql/ nbu/ network-bandwidth-control/ observability/ out-of-scope/ pg/ rdb-config/ report-center/ reporting/ rpc-rdbcomm/ tls/ tooling/ workflow/`。
  本体当前仅覆盖 PDCA 元概念（pdca/pdca-architecture/capability-protocol/phase/transition/evidence/gate…），未承载上述领域知识。
- 约束：`ontology-validate` 要求 type==父目录名、引用无悬空、关系无环、图无孤岛；新增域节点须向上连接到既有根，否则产生 island。
- 关键未决（需 grill）：粒度（每文件 vs 每域目录）、domain 根节点设计、manifest 索引处置、是否先试点部分域。

## 分类（初步）
- A 类（可整目录聚为一个域节点，约 28 个节点）：每个 `knowledge/<domain>/*.md` 合并为该域一个 `ontology/domain/<domain>.md` 节点。
- B 类（out-of-scope/README/manifest.jsonl）：索引与元文件，需单独处置。
- 风险：123 个细粒度节点会让本体膨胀且难维护；建议按域目录聚并。

## 验收判定（草案）
- 领域知识已析出进 `ontology/domain/*` 且 `ontology-validate` 通过、islands=0。
- `knowledge/` 已删除；活动文件对其引用改写。
- 证据链 + 收敛映射 valid:true。
