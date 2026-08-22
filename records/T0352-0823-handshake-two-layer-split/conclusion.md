---
schema: pdca.asset/v1
id: T0352-0823-handshake-two-layer-split
phase: check
source_ids: [ac1-rdbcomm-test, ac2-dmsbtex-test, ac3-libobk-tests, ac4-static-scan, ac5-full-build, check-xmake-test-all, convergence-map]
---

## 上下文

T0351 删除 libs/rpc-handshake 后三项目保留全量拷贝与共享前缀符号。本任务按 rpc 两层结构（协议层/IO 会话层）将握手逻辑拆分融入 rdbcomm(msg+io)/dmsbtex(protocol+network)/libobk(include/protocol.h+lib/protocol.c)，符号彻底项目化（rdb_hs_*/dm_hs_*/obk_hs_*），mTLS 客户端/服务端组合逻辑完整迁移，全仓共享库痕迹归零。

## 假设与结果

- **AC-1** rdbcomm 链接级握手会话测试：`PASS` — TIME/plain/mTLS 正向/强制拒绝四路径全过；fork+execl 形式 tool_integration 已移除。
- **AC-2** dmsbtex_session_test：`PASS` — AC-3 plain、AC-1 mTLS 正向、AC-4a/b 负路径全过；**存量 rc=-11 一并修复**（根因：make_cfg 从未填充 cert_dir）。
- **AC-3** libobk_session_test 与 libobk_protocol_test：`PASS` — 后者首次纳入构建目标，exit 0。
- **AC-4** 全仓 grep `rpc_hs_|rpc-handshake` 归零（digest 固化）；五份 handshake 文件不存在：`PASS`。
- **AC-5** xmake build -r 全量成功无新增警告：`PASS`。
- **超集验证** `xmake test` 39/39 全绿（含 rpc 项目全部测试）。

## 分析

- 两层拆分忠实映射 rpc 模式：协议纯函数（帧编解码/算法映射/decide）与 IO 会话原语（生命周期/读写分发/一体协商/首阶段分流）分层清晰；服务端决策树逐分支对照迁移，错误码语义一致。
- 过程中发现并修复三个存量缺陷（均非本任务引入但阻塞验收）：dmsbtex make_cfg 缺 cert_dir 填充（rc=-11 真因）、测试证书 CN 含空格被 ca_cn_valid 白名单拒绝（重建为 ED25519_Test_CA/SM2_Test_CA）、sbt_session_client_init 无前置校验导致负路径用例死锁。
- 附带修复两个 rpc 测试与实现脱节问题：mixed_mtls_integration 按"不要 fork+execl"要求重写为链接级（服务端决策树忠实复刻 + 真实 TLS 升级）；own_handshake 断言对齐 T0349 拒绝降级语义。

## 适用边界

- 协议字节与线上行为零变化仅针对三项目握手路径；libs/rpc-net.c 内联 TIME 帧（HS_NET_* 局部宏）未在本任务验证范围内。
- libobk 对外头签名类型改名（rpc_hs_session_t→obk_hs_session_t），结构布局不变，宿主程序需重编译。
- rpc 项目产品逻辑未触碰（仅测试代码与构建配置）。

## 下一轮建议

- libs/rpc-net.c 内联 TIME 帧存在头长疑点（HS_NET_FIXED_SIZE=16 与 AIOH 协议 18 字节头不一致，且 hs_put32(wire+14) 写入越界 2 字节），timed_net_key 校时链路建议立专项核实。
- dmsbtex network.h 中 dm_hs_session_t 定义于网络层头，若后续项目增多可考虑与会话原语一同抽至独立会话头（当前规模无需）。
