# rpc_net_time_test 适配恢复后的长度前缀协议

## 问题

`xmake run rpc_net_time_test` 失败：`diag: server exited status=512`（伪服务端 `_exit(2)`，请求帧校验不过）。

根因：用户将 libs/rpc-net.c 的 `rpc_send/rpc_recv` 恢复为"原来的实现方式"——**4 字节长度前缀(htonl) + body** 分帧协议，与 rpc 模块 `rpc_send_io/rpc_recv_io`（rpc-io.cpp:339/239）及真实服务端一致。而 T0353 测试的伪服务端按无前缀实现编写（recv 直接收 8B、send 直发 20B），与新协议不匹配。

附带发现：恢复后的 `rpc_get_time` 仅校验 `uiResult != 0`，不校验响应 `uiMT`。原负路径用例"错误 mt 类型必须被拒"（resp_mt=0xdeadbeef + uiResult=0）在该实现下会被当成功解析，用例无法成立。

## 方案

仅改测试 `libs/tests/rpc_net_time_test.c` 适配真实协议，不动 rpc-net 实现：

1. fake_server 收请求：先收 4B 前缀（MSG_WAITALL，校验 ==8），再收 8B body（校验 uiMT/uiLEN）。
2. fake_server 发响应：先发 4B htonl(sizeof(msg_get_time_resp_t))=20，再发 20B body；body 按结构布局填充（uiResult 显式可配）。
3. 负路径语义调整：改为"业务失败响应（uiResult≠0）必须被拒"——与实现的实际检查逻辑一致；原"错误 mt 必拒"场景在恢复实现中不存在该校验，删除并在注释说明。

## 用户故事

1. 作为维护者，rpc_net_time_test 应当验证 libs/rpc-net.c 与服务端之间的真实线上协议，测试红即代表协议回归。

## Seam 分析

### 声明的测试接缝

- seam: libs/tests/rpc_net_time_test.c -> ../rpc-net.c

## 实现决策

- 不改 libs/rpc-net.c（用户已确认以恢复后的实现为准）。
- fake_server 增加 recv/send 全量循环辅助，避免短读/短写偶发。

## 测试决策

- 正路径 ×2（普通/大时间戳字节序往返）+ 负路径 ×1（uiResult≠0 被拒）；全部经真实分帧协议。

## 验收标准

- [ ] AC-1: 运行 `xmake run -D rpc_net_time_test`，输出 PASS 且退出码 0。
- [ ] AC-2: 伪服务端按 4B 长度前缀协议收发（grep 确认测试中存在 htonl(sizeof) 前缀收发且无裸 8B/20B 直读直写残留）。
- [ ] AC-3: timed_net_key 链路回归——e2e 场景矩阵相关场景（S9 keygen 等）通过，证明恢复实现与真实服务端兼容。

## 范围外

- 不给 rpc_get_time 增加 uiMT 校验（如需强化属实现变更，另立任务）。
- 不动 rpc-net.c 其余部分。
