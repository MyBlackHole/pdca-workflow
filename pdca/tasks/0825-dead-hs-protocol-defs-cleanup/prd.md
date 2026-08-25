# 清理 dmsbtex/libobk 握手协议层死定义残留

## 问题

T3956 归一握手结果码后暴露：dmsbtex/protocol.h 与 libobk/include/protocol.h 存在一批零引用的协议层定义，为早期协议设计（规划了 magic/version/payload 帧字段）的残留物。实际帧实现（network_header_t+body / activeioHeader+body）不含这些字段，死定义误导读者以为存在对应协议语义。

## 已验证事实

全仓库（含 tests）零引用清单：

- dmsbtex/protocol.h：`DM_HS_MAGIC`、`DM_HS_VERSION`、`DM_HS_MAX_PAYLOAD`、`DM_HS_FIXED_SIZE`、`DM_HS_OK_TIME`、`DM_HS_OK_PLAIN`、`enum dm_hs_operation`（2 成员）、`enum dm_hs_flags`（3 成员）、`dm_hs_message_t`、`dm_hs_result_t`
- libobk/include/protocol.h：`OBK_HS_MAGIC`、`OBK_HS_VERSION`、`OBK_HS_MAX_PAYLOAD`、`OBK_HS_FIXED_SIZE`、`enum obk_hs_operation`（2 成员）、`enum obk_hs_flags`（3 成员）

保留项已确认有引用：`DM_HS_MAX_NAME`(10)、`OBK_HS_MAX_NAME`、`OBK_HS_RESP_BODY_SIZE`(6)、`HS_FLAG_MTLS_REQUEST`(13)、`HS_OK_PLAIN`(8)、`activeio_cmd`(含 active_handshake)。

## 方案

纯删除上述死定义及随之孤立的注释行；不改动任何有引用符号；不改线上字节流。

## Seam 分析

### 声明的测试接缝

- seam: dmsbtex/test/session_test.c -> ../network.c
- seam: libobk/test/session_test.c -> ../lib/sbt/libobk.c
- seam: rpc/tests/mixed_mtls_integration.cpp -> ../rpc-client.cpp

（纯删除任务：seam 沿用现有回归测试，无新增测试产物。）

## 测试决策

复用现有回归测试验证零行为变更：三模块 session test + mixed_mtls_integration + e2e 关键场景。

## 验收标准

- [ ] AC-1: 运行全量 xmake 构建，通过且无新增编译警告。
- [ ] AC-2: 运行 dmsbtex/libobk/rdbcomm session test 与 rpc mixed_mtls_integration，全部通过。
- [ ] AC-3: grep 全仓库确认被删 16 项符号零残留引用。

## 范围外

- dmsbtex 匿名 enum 中 `OPT_NULL`/`OPT_MAXNUM` 零引用但删除会引发 OPT_BACKUP/RESTORE 值偏移风险，非握手层内容，不在本任务处理。
- libs/tests/rpc_handshake_test.c 死测试文件（引用已删除头文件）属另一清理项。
