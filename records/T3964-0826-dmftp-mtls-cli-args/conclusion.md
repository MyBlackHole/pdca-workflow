---
schema: pdca.asset/v1
id: T3964-0826-dmftp-mtls-cli-args
phase: check
source_ids: [ac-summary, dmsbtex-session-test, ac5-grep]
---

## 上下文

T3963 审查发现混合提交 004ebafe 漏了 dm-ftp（dmsbtex 部署名）的 CLI 参数覆盖。本任务复刻 T3959 模式补齐（commit d73f26a5，dmsbtex 1.1.0.6）。用户在实施中纠正 usage 文案：tls-algorithm 为锁定语义且默认空（unset = no lock），FileTransferAgent 同款错误文案一并修正。

## 假设与结果

| 假设 | 结果 |
|------|------|
| 复刻 T3959 模式可直接落地（两文件同构） | 成立：构建一次通过（仅 env 宏提升/调用点适配微调） |
| CLI 显式值覆盖 env/config 解析值 | 成立：场景 C/E 行为级证明 |
| 未传参数行为不变 | 成立：对照场景 B 正常监听；session_test ALL PASS |

## 分析

- **AC-1** ✅ --help 含 --mtls-enable/--tls-algorithm 与 "unset = no lock" 说明（ac-summary）
- **AC-2** ✅ 三组非法值均 exit=1 输出 "dm-ftp: invalid ..."（ac-summary）
- **AC-3** ✅ A~E 五场景行为级验证全符合预期：CLI mtls 生效、CLI 覆盖 env、算法白名单校验、CLI 算法覆盖非法 env（ac-summary）
- **AC-4** ✅ 对照组行为不变；dmsbtex_session_test ALL PASS；libobk_session_test 回归过（dmsbtex-session-test）
- **AC-5** ✅ dmsbtex 无旧签名调用残留（全部三参）（ac5-grep）

Grill 追问：
1. sbt.c 为何被改动？→ init_sbt_config 内部基线调用 sbt_tls_config_init 需同步新签名（一行适配 (-1,NULL)）；该文件同时含用户未完成改动，本提交仅携带此必要适配行。
2. usage 文案为何改 "Lock server to this algorithm"？→ 用户裁定 tls-algorithm 默认空、语义为锁定；原 "default" 措辞与 T3961 无默认值语义矛盾。

## 适用边界

适用于 dm-ftp 服务端单次启动配置；SBT 客户端库模式（init_sbt_config 文件路径）的配置文件键解析未变。

## 下一轮建议

- 四工具 CLI 参数矩阵现已对齐（aio-speedd/rdbcommd/FileTransferAgent/dm-ftp），可在 docs 沉淀一张运维参数对照表。
- libs/tests/certs SM2_Test_CA 前缀布局资产缺失问题仍待补（影响 SM2 锁定测试）。

verdict: {"outcome": "confirmed", "reason": "五条 AC 全过：dm-ftp CLI 参数+锁定语义+兼容性均有行为级证据", "verdict_id": "T3964-check-v1", "at": "2026-08-26T09:00:00+08:00"}
