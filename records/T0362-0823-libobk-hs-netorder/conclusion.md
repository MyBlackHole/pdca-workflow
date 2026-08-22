# 结论（T0362 / M5 libobk 握手网络序改造）

## 任务
libobk 握手 body `{result u16, algorithm u16}` 字节序改造为网络序（htons/ntohs），
与 rdbcomm/dmsbtex/rpc 既有约定统一。破坏性：外部 oracle 对端需同步升级（另排）。

## Do 阶段产物
- `libobk/lib/sbt/libobk.c`：客户端发送 `htons(ctx->tls_algorithm)`（L138），接收 `ntohs(result)`（L165）、`ntohs(halg)`（L167）。
- `libobk/lib/logic/oracleCmdTbl.c`：补 `#include <arpa/inet.h>`；服务端接收 `ntohs(halg)`（L880）；三条发送路径均 `htons(result/halg)`（L99-102、L116-119 拒绝分支、L129-132）。
- `libobk/test/session_test.c`：补 `#include <arpa/inet.h>`；服务端测试侧解析 req `ntohs(halg)`（L137、L230）；父进程侧 recv 拒绝帧 `ntohs(result/resp_halg)`（L277-283）且发送 req 用 `htons(bad_halg)`（L259）。

## 双轴审查与修复（Check 前置）
- 标准轴 + 规范轴均发现 Blocking 缺陷：服务端「未知算法」拒绝分支（原 L114-117）漏改 htons，wire 协议不对称；测试两侧 recv 未 ntohs，掩盖漏测。
- 已修复：拒绝分支补 htons；测试服务端侧与父进程侧补 ntohs/htons。复测 PASS。

## 验收映射（convergence-map）
- AC-1：握手 algorithm/result 收发统一网络序，无裸 memcpy 主机序 uint16_t 字段。→ passed（grep 确认无残留裸 memcpy）。
- AC-2：libobk_session_test 全用例 PASS。→ passed。
- AC-3：跨模块字节序一致（libobk 与 rdbcomm/dmsbtex/rpc 均网络序）。→ passed。

## 回归
全量 `xmake test` = 40/40 PASS，无回归。

## 判定
Do 实现满足 prd AC-1~AC-3，双轴审查 Blocking 项已闭环修复，建议 verdict=confirmed，进入 Act 归档。
