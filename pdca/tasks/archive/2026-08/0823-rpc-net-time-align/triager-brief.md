# Triage Brief — 0823-rpc-net-time-align

- **category**: enhancement
- **scenario_type**: development
- **summary**: rpc-net 的 time 客户端改为 MT_GET_TIME 协议只对接 rpc 服务端；rdbcomm 移除 time 获取协议全链路
- **current behavior**: libs/rpc-net.c 内联 AIOH TIME 帧（16 字节头越界缺陷）；rdbcomm 保留 request_time/OP_TIME 分支/time 子命令
- **desired behavior**: rpc_get_time 说 MT_GET_TIME 协议对接 aio-speedd；rdbcomm 无任何 time 协议代码
- **key interfaces**: rpc_get_time、rdb_hs_request_time、first_stage TIME 分支、工具 time 子命令
- **acceptance criteria**: 运行新增链接级解析测试得到 PASS；运行 rdbcomm grep 得归零；运行全量构建与相关套件得到成功
- **out of scope**: aio-speedd/aio-speed 改动、timed_net_key API、AIOH TIME 兼容
- **information gaps**: 无
- **dedup results**: T0352 conclusion 遗留建议转正，非重复
- **recommended next steps**: 终审后按切片 A/B 执行
