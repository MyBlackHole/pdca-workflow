---
schema: pdca.asset/v1
id: T0354-0823-optional-handshake-align
phase: check
source_ids: [ac1-rdbcomm-matrix, ac2-dmsbtex-matrix, ac3-libobk-tests, ac4-full-build-test, ac5-branch-scan, convergence-map]
---

## 上下文

三项目（rdbcomm/dmsbtex/libobk）与 rpc 通信逻辑不一致：无条件强制协议握手。本任务按方案 Z' 对齐 rpc 决策树——握手内嵌消息循环、协商帧项目帧头封装、无降级约束，实现六象限行为矩阵。

## 假设与结果

- **AC-1** rdbcomm handshake_session_test：`PASS` — 明文零握手直通 / 按需 mTLS 升级+加密往返 / 无证书拒绝降级 三用例全过。
- **AC-2** dmsbtex_session_test：`PASS` — 四用例全绿（明文直通/强制 mTLS/坏目录 prepare 失败/无降级拒绝）；顺带修复测试线程 64MB 栈数组溢出。
- **AC-3** libobk session/protocol_test：`PASS` — exit 0。
- **AC-4** xmake build -r 零错误 + xmake test 40/40：`PASS`。
- **AC-5** 三项目条件分支 grep 断言：`PASS` — rdbcomm io.c `!mtls_enabled` 短路、dmsbtex network.c 条件化、libobk client 侧 `tls_mtls_enabled` 分支均存在。

## 分析

- 行为矩阵落地：明文×明文零握手零开销；server 无证书能力 + client 要加密 → ERR_MTLS_UNAVAILABLE 拒绝（不降级）；有证书能力 → 按需 OK_MTLS 升级；强制模式未握手明文业务帧拒绝。
- 协商帧 wire 格式变更（裸 AIOH → 项目帧封装），AIOH encode/decode/decide/首阶段分流函数全量清理，io 层精简为会话原语，净删约 600 行。
- 服务端证书 ctx 构建策略对齐 rpc：cert_dir 可用即构建（mtls_enabled 仅控制强制语义），构建失败非强制模式降级为明文服务并告警（F3 语义）。

## 适用边界

- mTLS 场景 wire 字节变化为破坏性变更，新旧版本混布不兼容，需三端同步升级。
- rpc 项目产品逻辑未改动。

## 下一轮建议

- dmsbtex _worker 循环的强制拒绝目前直接断开，可考虑回错误帧提升客户端诊断体验（低优先级）。
