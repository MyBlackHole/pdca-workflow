# 代码差异证据（T0362 / M5 libobk 握手网络序改造）

`git diff --stat`（工作区，相对 T0359 已提交基线）：

- libobk/lib/sbt/libobk.c
  - L138 客户端发送：uint16_t req_alg = htons(ctx->tls_algorithm); memcpy(req, &req_alg, 2);
  - L165/L167 客户端接收：result = ntohs(result); halg = ntohs(halg);
- libobk/lib/logic/oracleCmdTbl.c
  - 补 #include <arpa/inet.h>
  - L880 服务端接收：halg = ntohs(halg);
  - 三条发送路径均 htons：L99-102（不可用分支）、L116-119（未知算法拒绝分支）、L129-132（OK 分支）
- libobk/test/session_test.c
  - 补 #include <arpa/inet.h>
  - L137/L230 服务端测试侧解析 req：halg = ntohs(halg);
  - L259 父进程发送 req：halg = htons(bad_halg[i]);
  - L277-283 父进程接收拒绝帧：result = ntohs(result); resp_halg = ntohs(resp_halg);

验收映射：AC-1（握手 algorithm/result 收发统一网络序，无裸 memcpy 主机序 uint16_t 字段）、AC-3（与 rdbcomm/dmsbtex/rpc 网络序约定一致）。
双轴审查发现的拒绝分支漏改 htons 与测试两侧漏 ntohs 已闭环修复。
