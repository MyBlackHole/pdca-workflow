# 跟进：mTLS 参数解析严格化 atoi/strstr（H2+H3，T0348）

## 问题陈述

- **现状**: `SBT_MTLS_ENABLE` 用 `atoi` 解析（dmsbtex/network.c:104、libobk.c:74），`=abc` 静默禁用 mTLS（fail-open）；四份算法名映射函数用 `strstr` 子串匹配（msg.c:115、protocol.c:69、rpc-protocol.cpp:208、libobk protocol.c:17），"sm2" 命中 SM4 且被 rpc/tests/rpc_own_handshake_test.cpp:56 固化。
- **目标**: 安全开关 fail-closed 解析；算法名 strcmp 全串精确匹配，未知名显式报错。
- **差距**: T0348 审查报告 H2/H3。

## 修复范围

| 项 | 位置 | 动作 |
|----|------|------|
| H2 | dmsbtex/network.c:104、libobk/lib/sbt/libobk.c:74 | 改严格解析（strtol 全串校验）；非法值**拒绝初始化/启动**并报错 |
| H3 | 四份 `*_algorithm_from_name` | strstr → strcmp 精确匹配；未知名返回 DEFAULT(0) 保持纯函数语义 |
| H3 配置侧 | sbt_tls_config_init / sbt_client_tls_config_init 等 | 加载时校验算法名合法性，未知名**拒绝初始化/启动**（与 CLI 行为一致） |
| H3 测试 | rpc/tests/rpc_own_handshake_test.cpp:56 | 删除 "sm2"→SM4 断言，改为精确匹配断言 |

## 用户决策（2026-08-22 对齐）

- mtls_enable 非法字符串 → **拒绝启动**（fail-closed）
- tls_algorithm 未知名 → **配置加载时拒绝**（fail-closed，早于协商）

### 声明的测试接缝
- seam: rpc/tests/rpc_own_handshake_test.cpp -> rpc/rpc-protocol.cpp
- seam: dmsbtex/test/session_test.c -> dmsbtex/protocol.c

## 验收标准

- [ ] AC-1: `SBT_MTLS_ENABLE=abc` 时 dmsbtex/libobk 拒绝启用 mTLS 并输出告警（不再静默明文）
- [ ] AC-2: 四模块算法名解析仅接受全串精确匹配，未知名称不命中任何算法
- [ ] AC-3: 既有合法配置路径回归通过

## 备注

行为变更点：依赖 "sm2" 宽松命中的部署需改用规范名——发布说明需标注。
