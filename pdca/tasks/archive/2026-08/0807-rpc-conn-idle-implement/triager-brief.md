# T0226 Triager Brief — rpc 复用连接空闲回收 + EOF 判定实现

## 分类
- category: `enhancement`
- scenario_type: `development`（落地 T0227 选定的实现）
- parent: T0227（研究父任务，已归档）
- 前置成果: ADR-0016、POC 仓库（4 场景全过）、prd.md（T0227）

## 来源（不重复调研）
- T0227 research-report: 方案=客户端 FIN 主导空闲回收 + 服务端 read_timeout 兜底 + rpc_recv EOF 判定
- ADR-0016: "不新增协议"，"仅固化决策方向，不改代码"
- POC: lib/rpcmock 已镜像 read_is_ready 语义

## 待实现落点（F/131 rpc 目录）
1. `rpc-conn.h`：新增 `last_used`/`idle_timeout` 字段
2. `rpc-conn.cpp`：send/recv 刷新 `last_used`；取用点检查空闲超阈值→主动 close 发 FIN
3. `rpc-io.cpp`：`rpc_recv` 区分 `nread==0`(EOF) 与 `nread<0`(网络错误)，EOF 返回非错语义
4. `rpc-config.h/cpp`：新增 `idle_timeout` 配置项（默认 < read_timeout=120000ms）

## 信息缺口（需 Grill / 或可从现有代码直接确认）
- `rpc_conn_reconn_send_msg` 空闲判定插入点确认（rpc-conn.cpp:161）
- `rpc_recv` EOF 返回码语义选择（0 或新增宏），避免破坏现有调用方（rpc-server.cpp:220 判 bytes<0）
- idle_timeout 默认值与是否需上限校验（对齐 rpc-config keepalive 的处理，rpc-config.cpp:42/72）
- 本任务是否也改 F/131 里 rpc.cpp 的多处 reconn 调用点，还是集中在 rpc-conn 层

## 查重
- T0227 为研究，不含实现；无重复实现任务。
- 0803-rpc-protocol-transport-refactor 为传输重构，正交。

## 建议下一步
- Plan P2 Grill：确认 idle_timeout 默认值、EOF 返回码设计、改动收敛面（集中 rpc-conn/rpc-io 层 vs 遍历调用点）。