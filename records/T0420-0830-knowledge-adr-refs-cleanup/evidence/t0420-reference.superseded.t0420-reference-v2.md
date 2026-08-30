# T0420 引用清理证据

## A 类（16 个重定向桩）：改写指向 ontology-creation-gate 决策背景
- knowledge/tls/mtls-handshake-netorder-libobk.md
- knowledge/tls/mtls-handshake-enum-unify.md
- knowledge/tls/mtls-four-module-supplementary-review.md
- knowledge/tls/tls_cert_reload_appdata_safety.md
- knowledge/tls/mtls-param-review-findings.md
- knowledge/tls/structured-mtls-failure-diagnostics.md
- knowledge/tls/mtls-server-alg-whitelist.md
- knowledge/tls/link-level-mtls-test-pattern.md
- knowledge/rpc-rdbcomm/unified-first-stage-mtls-time.md
- knowledge/rpc-rdbcomm/mtls-review-fd-session-boundary.md
- knowledge/nbu/gmssl-tlcp-mtls.md
- knowledge/linux-epoll-eventloop/backupstream-plain-tls-ingress.md
- knowledge/debugging/tls-exec-truncation-investigation-state.md
- knowledge/oss/oss_https_tls.md
- knowledge/dmsbtex/sbt_config_mtls_override.md
- knowledge/tooling/cli-tls-mtls-configuration.md

改写：「本文件已按 ADR-0030 物理归并至本体库」→「本文件已按 `ontology:concept/ontology-creation-gate` 决策背景物理归并至本体库」

## B 类（3 个真实知识文件）：溯源改写，去除 ADR 字面引用
- knowledge/linux-epoll-eventloop/rpc-conn-idle-reclaim.md：（原 ADR-0016-...）改为「相关决策已随 docs/adr/ 退役删除，见上方 records/ 记录」
- knowledge/lmdb/vl32-no-mmap-build-gate.md：Source 行移除 "and ADR-0022"（保留 T0249 任务号）
- knowledge/ai-efficiency/skills-candidate-review.md：「ADR-0007 流程显式更新」→「流程显式更新」

## 校验
- `grep -rn "ADR-[0-9]" knowledge/`：无结果（AC-5）
- `ontology-validate.py`：通过（输出见 t0420-validate.json）
