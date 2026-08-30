# T0420 triage

- 触发：T0419 全量删除 `docs/adr/`（32 个 ADR 文件 + 目录）后，`knowledge/` 下仍有 19 个文件引用已删 ADR。
- 范围：仅 `knowledge/`，不含 `scripts/SKILL/flows/docs/templates/ontology`（T0419 已处理）。
- 分类：
  - **A 类（16 个重定向桩）**：内容为"本文件已按 ADR-0030 物理归并至本体库：<node>"。这些文件本身已是 deprecated 重定向桩，指向本体节点；其中 `ADR-0030` 仅作历史原因说明，现该 ADR 已删，应改写为指向本体节点的决策背景（去掉 ADR 字面引用）。
    - 涉及：knowledge/tls/*（8）、knowledge/rpc-rdbcomm/*（2）、knowledge/nbu/gmssl-tlcp-mtls.md、knowledge/linux-epoll-eventloop/backupstream-plain-tls-ingress.md、knowledge/debugging/tls-exec-truncation-investigation-state.md、knowledge/oss/oss_https_tls.md、knowledge/dmsbtex/sbt_config_mtls_override.md、knowledge/tooling/cli-tls-mtls-configuration.md
  - **B 类（3 个真实知识文件）**：含对具体已删 ADR 的来源/溯源引用，应改为任务号或 records/ 溯源，去掉 ADR 字面引用。
    - knowledge/linux-epoll-eventloop/rpc-conn-idle-reclaim.md（ADR-0016）
    - knowledge/lmdb/vl32-no-mmap-build-gate.md（ADR-0022）
    - knowledge/ai-efficiency/skills-candidate-review.md（ADR-0007）
- 风险：纯文本改写，不改本体节点、不删知识文件，无功能影响；本体校验不受影响。
- 验收判定以 grep `ADR-[0-9]` 在 `knowledge/` 下归零 + `ontology-validate` 通过为准。
