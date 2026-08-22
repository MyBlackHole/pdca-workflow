# 设计 — libobk 握手 body 字节序网络序改造（M5，T0362）

## 目标
将 libobk 握手协商帧（`{result u16, algorithm u16, ca_cn[200]}`）的 `uint16_t` 字段统一为主机序↔网络序转换，与 rdbcomm/dmsbtex/rpc 约定一致，消除跨字节序架构握手错位风险。

## 字节序约定
- 线上（wire）格式：`result`、`algorithm` 均为**网络序（大端）**。
- 本机处理：`uint16_t` 主机序；发送前 `htons`，接收后 `ntohs`。
- 数值语义不变：`HS_ALG_DEFAULT=0` / `HS_ALG_TLS_SM4_GCM_SM3=1` / `HS_ALG_TLS_AES_256_GCM_SHA384=2` 经 `htons`/`ntohs` 对称还原。

## 改动清单
| 角色 | 文件 | 位置 | 改动 |
|------|------|------|------|
| 客户端发送 | `libobk/lib/sbt/libobk.c` | `sbt_session_client_init` L137-138 | `uint16_t req_alg = htons(ctx->tls_algorithm); memcpy(req, &req_alg, 2);` |
| 客户端接收 | `libobk/lib/sbt/libobk.c` | L163-164 | `memcpy(&result, resp, 2); result = ntohs(result);`；`memcpy(&halg, resp+2, 2); halg = ntohs(halg);` |
| 服务端接收 | `libobk/lib/logic/oracleCmdTbl.c` | L873-874 | `memcpy(&halg, buffer+sizeof(activeioHeader), 2); halg = ntohs(halg);` |
| 服务端发送 | `libobk/lib/logic/oracleCmdTbl.c` | L98-99 / L113-114 / L126-127 | 发送前 `uint16_t s_r = htons(result); uint16_t s_a = htons(halg); memcpy(resp,&s_r,2); memcpy(resp+2,&s_a,2);` |

## 头文件依赖
- `libobk/lib/sbt/libobk.c` 已 `#include <arpa/inet.h>`（`htons`/`ntohs` 可用）。
- `libobk/lib/logic/oracleCmdTbl.c` 若未直接 include `arpa/inet.h`，补 `#include <arpa/inet.h>`（经 `protocol.h` 间接可用则无需）。

## 测试策略
- `libobk_session_test`：同架构下 `htons`/`ntohs` 对称，客户端（`sbt_session_client_init`）与服务端（`sbt_session_server_handshake`）同步改造后自洽，全用例应 PASS（含 OK_MTLS 成功路径与拒绝路径）。
- 新增构造断言：在测试中显式校验「线上字节为网络序」——可选，验证 `htons(algorithm)` 落盘（如小端机上 `algorithm=1` 线上为 `0x01 0x00`）。
- 跨模块一致性：`grep` 核对 rdbcomm/dmsbtex/rpc 已网络序，libobk 改造后一致（AC-3）。

## 风险与缓解
- 破坏性：外部 oracle 备份客户端（非本仓库）按主机序解析 libobk 服务端 resp，升级后字节序反转失败。缓解：发布说明标注需对端同步升级；本仓库内客户端/服务端同步改造无回归。
- 算法白名单语义（T0359 fail-closed）不受影响：枚举值经对称转换还原，拒绝/采纳逻辑不变。

## 验收对照
- AC-1：握手 `algorithm`/`result` 收发统一网络序（客户端 htons 发送 / ntohs 接收；服务端 htons 发送 / ntohs 接收），无裸 memcpy 主机序 `uint16_t` 字段。
- AC-2：`libobk_session_test` 全用例 PASS。
- AC-3：libobk 与 rdbcomm/dmsbtex/rpc 握手字段均网络序（`grep` 一致）。
