# T0229 Research Metadata

- record: T0229-0810-ob-backup-gm-encrypt-verify
- subject: OceanBase 4.2.1.1 backup encryption & GM(SM4) support verification
- scenario_type: research
- primary artifact: evidence/OceanBase_备份加密与国密SM4_验证报告.md (verify-report, SHA-256 b7496b6284d02cb25da81fc30ec1c3f1425c1e813bbf42766d3a496f4b98eaca)

## Acceptance coverage

| AC | Carried by | Note |
|----|------------|------|
| AC-1 | this registration (verify-report entry in manifest) | report registered under records/T0229-* /evidence/, digest included |
| AC-2 | verify-report §二-§三 evidence 一/二/三 | storage + transport dimensions with source line refs (ob_config.cpp empty value table, EVP_sm4, macro-block encrypt_id) |
| AC-3 | verify-report §七 | TDE→SM4 runbook (Oracle tablespace SM4-CBC/GCM + progressive_merge + MAJOR FREEZE + V$OB_ENCRYPTED_TABLES) |
| AC-4 | verify-report §八 + official KB | commands follow official KB "如何为全量备份集和增量备份集设置加密密码": SET ENCRYPTION ON IDENTIFIED BY ... ONLY / SET DECRYPTION IDENTIFIED BY / ALTER SYSTEM BACKUP [INCREMENTAL] TENANT; link https://www.oceanbase.com/knowledge-base/oceanbase-database-1000000001675876 |

## Core conclusions (summary)

1. Backup STORAGE encryption: four modes exist (PASSWORD=verify-only/plaintext, PASSWORD_ENCRYPTION=password-derived entropy/AES-family, TRANSPARENT_ENCRYPTION=source-TDE passthrough, DUAL_MODE=both). No "select SM4 for backup" switch: the algorithm value table is an empty placeholder; SM4 ciphertext is only reached by transparent encryption from a source SM4 TDE table.
2. The crypto engine EVP layer implements full SM4 modes; is_sm_algorithm() is declared without implementation -> SM4 enablement path is reserved for the security/enterprise build (OB_BUILD_TDE_SECURITY defaults ON). Enterprise runtime behavior cannot be proven from open source; verify against enterprise docs/releases.
3. Backup TRANSPORT encryption: OB→S3/OSS uses standard HTTP(S)/TLS with no GM suites; OB-internal TLS GM suites (ECC-SM2-WITH-SM4-SM3) exist only under the BabaSSL build and do not cover backup media paths. Transport-level GM requires a GM TLS gateway in front of the media.

## Sources

- Code: local OceanBase worktree (commit 3abcb163) src/share, src/storage, deps/oblib, deps/easy, deps/ussl-hook.
- Read-only probes on live cluster obv422167545556 (tde_method=none, no data touched); local podman community image limited (no Oracle mode).
- Official commands: https://www.oceanbase.com/knowledge-base/oceanbase-database-1000000001675876