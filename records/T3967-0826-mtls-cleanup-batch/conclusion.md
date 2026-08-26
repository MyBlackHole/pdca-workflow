---
schema: pdca.asset/v1
id: T3967-0826-mtls-cleanup-batch
phase: check
source_ids: [ac-summary, hs-err-test, rdb-config-test, tls-cert-test, mixed-mtls-integration, dmsbtex-session-test, libobk-session-test, e2e-matrix]
---

## 上下文

落地 T3965 mTLS 整体分析确认的六项改进（P1/S1/C1/C2/C3 + sec_resolve 重复解析治理）。commit 104167b7（16 files, +391/-103），版本 rpc 3.6.4.27 / rdbcomm 1.0.2.5 / libobk 1.0.1.7 / dmsbtex 1.1.0.7。

## 假设与结果

| 假设 | 结果 |
|------|------|
| ccache LRU 可在现有测试资产下验证 | 成立：70 个 ca_cn 组合填满触发淘汰、全引用中 CCACHE_FULL，用例 PASSED |
| 算法解析归一后四模块锁定/未锁语义不变 | 成立：mixed AC1-9 与三 session_test 回归全过 |
| 旧 ini key 双读兼容 | 成立：rdb_config_test 别名双向用例通过 |
| 不引入通用缓存（用户裁定） | 遵循：撤销 sec_cache 实现；策略开关由调用方初始化时保存结果 |

## 分析

- **AC-1** ✅ LRU 淘汰与 CCACHE_FULL 行为经 tls_cert_test 新用例验证（tls-cert-test）
- **AC-2** ✅ 四模块 config init 迁移 hs_algorithm_config_resolve；hs_err_test 五分支（>0/0/-1/CLI 优先/env 命中）；mixed AC1-9 过（ac2 证据组）
- **AC-3** ✅ 别名双向等效：新 key 写旧 key 查、旧 key 写新 key 查均命中（rdb-config-test）
- **AC-4** ✅ SBT_* 宏单源 common.h；dmsbtex/libobk 头改引用；全量构建过；session_test 回归（ac4 证据组）
- **AC-5** ✅ 按用户裁定无通用缓存——调用方持有结果模式文档化于 rdb-config.h 注释（ac-summary）
- **AC-6** ✅ e2e 场景矩阵 19/19（e2e-matrix）

Grill 追问：
1. 别名回退是否影响性能/安全？→ 仅 global 层查找 miss 时多一次内存 strcmp，握手低频路径无感；不放宽任何校验。
2. release 归零保留条目是否泄漏？→ 上限 64 槽，LRU 淘汰时 cleanup；进程退出由 OS 回收。较原"即回收"策略多驻留最多 64 个 SSL_CTX，换取复用与可淘汰性，权衡合理。

## 适用边界

别名表仅覆盖当前两对历史 key；后续新增配置项应直接使用规范名。spec 化为增量 API，旧 6 参接口继续可用。

## 下一轮建议

- P2 reload 竞态在接入热轮换前补锁（分析报告遗留 MEDIUM）。
- SM2_Test_CA 测试资产补齐 sm2_ 前缀布局，解锁 SM2 锁定路径测试。

## 撤销记录（2026-08-26）

用户在 Check 确认环节要求自我审查后，又指示撤销最后提交。自查曾发现 int 别名层 atoi 脏值静默为 0 的 HIGH 问题（修正随撤销一并回退）；最终用户执行 `git reset --hard HEAD~1` 撤销 commit 2883d49a 全部改动，分支回到 4ef9c5c1（F-139 squash 基线）。六项改进的设计与验证记录保留于本报告，供后续按需重启。

verdict: {"outcome": "rejected", "reason": "用户指示撤销最后提交的全部修改，实现未保留；分析与设计记录留档备查", "verdict_id": "T3967-check-v2", "at": "2026-08-26T09:40:00+08:00"}
