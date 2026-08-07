# T0225 Triager Brief — rpc 复用 socket 无关闭时机的空闲回收方案

## 分类
- category: `enhancement`
- scenario_type: `research`（分析并选定方案，产出设计决策，非直接改码）

## Claim 验证

已在源码中核实（非询问用户）：

- `rpc_conn`（rpc/rpc-conn.h:3）复用长连接，但结构体无 `last_used` / `idle_timeout` 字段。
- `sock_keepalive()`（rpc/rpc-io.cpp:207、289）是 **TCP 探活**，只能察觉对端死亡，无法与应用层"暂停业务后回收空闲连接"关联。`keepalive` 配置（rpc-config.cpp:42）语义是探活间隔，非回收超时。
- 关闭时机分散：`rpc/server.cpp` 的 `rpc_conn_close`（3370/3856/3915）、`rpc.cpp`（1927/2058/2165/2777）等均靠**错误/退出路径触发**，无"空闲超时"驱动的一次性剥离。
- 发送路径 `rpc_conn_reconn_send_msg`（rpc-conn.cpp:161）复用前仅检查 `is_usable` + 失败重连，缺少"空闲太久主动关闭再重连"的惰性回收判定。

结论：当前**无应用级空闲回收**，复用连接可能无限期悬空占用 fd。

## 候选方案（Plan 阶段将收敛为一种）

1. 惰性回收（取用点检查 `now - last_used > idle_timeout`，过期即 close 走既有重连路径）
2. 后台巡检（周期任务扫描池内空闲连接并 close）
3. 纯 TCP 依赖（自认 keepalive 足够，不新增应用层回收）— 备选/否定项

## 信息缺口（需 Grill）

- 复用粒度：客户端是**单常驻连接**（rpc.cpp 的 trans/session 一处持有）还是**多连接池**？决定 Lazy vs 巡检。
- 本任务是"出方案与选型 + 落点设计"即可，还是要求直接落地实现？
- 空闲回收的触发阈值期望（默认值）与是否需可配置。

## 查重

- 活跃任务无重复；`T0216`（0805 rpc-epoll worker 供给）主题为 worker 线程供给，与连接空闲回收正交，但同属 rpc 网络层，PRD 需声明边界。
- archive / knowledge 各栏目中无同名议题。

## 建议下一步

进入 Plan P1 澄清 + P2 Grilling（一次一问），闭合复用粒度与交付边界后出 PRD 与方案取舍，P6 终审。