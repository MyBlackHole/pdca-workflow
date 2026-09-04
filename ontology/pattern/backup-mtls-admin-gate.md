---
schema: pdca.asset/v1
id: ontology:pattern/backup-mtls-admin-gate
type: pattern
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/backup-mtls-admin-gate/1.0.0
summary: rpc 明文 admin 面需 mTLS 强制或 allow_list 校验，避免 sh -c 任意执行
relations:
  relates_to:
  - ontology:domain/backup
  specializes:
  - ontology:pattern
---

# mTLS Admin Gate

**来源：** T0488 C-01，`rpc/rpc-server.cpp:440-476,854`

**模式：** `MT_EXECUTE_SHELL_SCRIPT` 经 `sh -c` 直达，未前置 `auth_enabled` 校验。`mtls_enabled=0` 默认明文可达即 RCE；`mtls_enabled=1` 时 `handshake_done` 已认证。

**应用：** 明文部署下前置 `auth_enabled` / `allow_list`（拒 `;|&$()`），或强制 `mtls_enabled=1`。

**反例：** `aio-speed -h ip -p 6611 -c "任意命令"` 明文直达。
