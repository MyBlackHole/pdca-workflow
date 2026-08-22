# PRD — libobk 握手 body 字节序网络序改造（M5，T0348）

## 背景
T0348 审查报告 H4/M1/M5 三类中，H4（服务端算法白名单）与 M1（枚举/映射单一来源）已由 T0357、T0359 完成。本任务处理 M5：libobk 握手 body 字节序网络序改造。

libobk 同时承担 oracle 备份协议的**客户端**（`libobk/lib/sbt/libobk.c` 的 `sbt_session_client_init`）与**服务端**（`libobk/lib/logic/oracleCmdTbl.c` 的 `sbt_session_server_handshake`）。握手协商帧 body 为 `{result u16, algorithm u16, ca_cn[200]}`。

## 现状（主机序）
- 客户端发送：`memcpy(req, &ctx->tls_algorithm, 2)`（`libobk.c:138`）——裸主机序 `uint16_t`。
- 客户端接收：`memcpy(&result, resp, 2); memcpy(&halg, resp+2, 2)`（`libobk.c:163-164`）——主机序。
- 服务端接收：调用方由请求帧解析 `algorithm`（`oracleCmdTbl.c:863-875`）——主机序。
- 服务端发送：`memcpy(resp,&result,2); memcpy(resp+2,&halg,2)`（`oracleCmdTbl.c:98-99/113-114/126-127`）——主机序。
- 项目其它三模块（rdbcomm/dmsbtex/rpc）握手字段均使用网络序（`htonl`/`ntohl`），libobk 与之不一致（T0359 PRD 第 5 行）。

## 差距
同架构下 libobk 客户端/服务端主机序自洽；但跨字节序架构（如从 x86 小端切换到非小端对端）或与其余模块统一约定时会解析错位。M5 将其收敛为网络序，消除跨架构握手失败风险并统一项目协议风格。

## 方案
对 libobk 握手帧的 `uint16_t` 字段统一做主机序↔网络序转换：
- 客户端发送 `algorithm`：`htons(ctx->tls_algorithm)`。
- 客户端接收 `result`/`algorithm`：`ntohs(result)` / `ntohs(halg)`。
- 服务端接收请求 `algorithm`：`ntohs(...)`（解析处 `oracleCmdTbl.c:863-875`）。
- 服务端发送 `result`/`algorithm`：`htons(result)` / `htons(halg)`。
- 枚举值 `HS_ALG_DEFAULT=0` / `HS_ALG_TLS_SM4_GCM_SM3=1` / `HS_ALG_TLS_AES_256_GCM_SHA384=2` 不受影响（数值经 htons/ntohs 对称还原）。

## 范围
- 内：libobk 客户端（`libobk.c`）+ 服务端（`oracleCmdTbl.c`）握手字段网络序改造；`libobk_session_test` 适配验证。
- 外（破坏性）：**真实部署对端**（外部 oracle 备份客户端，非本仓库）按主机序解析 libobk 服务端 resp，升级本仓库后字节序反转将失败，需对端同步升级。本仓库内客户端/服务端同步改造自洽；外部对端升级作为发布说明与跟进，不在本任务代码范围。

## 验收标准
- [ ] AC-1: libobk 握手 `algorithm`/`result` 字段收发统一网络序——客户端发送 `htons`、接收 `ntohs`；服务端发送 `htons`、接收 `ntohs`；`grep` 确认握手路径无裸 `memcpy` 主机序 `uint16_t` 字段。
- [ ] AC-2: `libobk_session_test` 全用例 PASS（同架构 `htons`/`ntohs` 对称自洽，含 OK_MTLS 与拒绝路径）。
- [ ] AC-3: 跨模块字节序约定一致——libobk 与 rdbcomm/dmsbtex/rpc 握手字段均网络序（`grep` 核对）。

## 风险
- 破坏性协议变更：外部对端需同步升级（已在范围外声明）。本仓库内无回归风险（客户端/服务端同步）。
- 算法值 0/1/2 经 `htons`/`ntohs` 对称还原，白名单/拒绝语义不受影响（T0359 已落 fail-closed）。
