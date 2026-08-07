# T0226 跟进：rpc 复用连接空闲回收 + EOF 判定实现

## 背景

T0225（research）已选定方案并获 POC 实证（4 场景全通过，ADR-0016）：
客户端主动 FIN 主导空闲回收 + 服务端 read_timeout 兜底 + rpc_recv EOF 判定。
本任务落地代码。

## 目标

- 客户端 `rpc_conn` 增加 `last_used`/`idle_timeout`，空闲超阈值主动 close 发 FIN，
  复用路径 `rpc_conn_reconn_send_msg` 自动重连。
- `rpc_recv`（rpc-io.cpp:25）区分 `nread==0`（EOF/正常关闭，返回非错语义）与
  `nread<0`（网络错误），消除"客户端正常关闭被误报 bad network" 3 条 Error 噪音。
- rpc-config 增加 `idle_timeout` 配置（默认 < read_timeout=120000ms），两端对齐。

## 范围

- 仅改 F/131 rpc 目录：rpc-conn.h/cpp、rpc-io.cpp、rpc-config.h/cpp、rpc-server.cpp
  （回收日志可观测标记可选）。
- 不改协议、不引入连接池巡检。

## 验收标准（Plan 阶段细化）

- [ ] AC-1: 客户端空闲超阈值主动 close，服务端在 read_timeout 前经 POLLRDHUP 回收
- [ ] AC-2: rpc_recv 对 EOF 返回非错误语义，客户端正常关闭不再打印 3 条 Error
- [ ] AC-3: idle_timeout 可配置且默认 < read_timeout
- [ ] AC-4: 全量回归（含集成/单元）通过，fd 无泄漏

## 备注

- 复用 T0225 的 POC 仓库（POC/scenarios）作为回归参考。
- 相关 ADR：ADR-0016。