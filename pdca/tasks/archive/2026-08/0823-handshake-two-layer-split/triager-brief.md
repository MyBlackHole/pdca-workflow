# Triage Brief — 0823-handshake-two-layer-split

- **category**: enhancement
- **scenario_type**: development
- **summary**: 三项目握手逻辑从 libs 全量副本重构为 rpc 式两层结构（协议层/IO 会话层）并彻底项目化命名
- **current behavior**: rdbcomm/dmsbtex/libobk 各持 libs 握手库全量拷贝文件，保留共享前缀符号 rpc_hs_* 与宏 RPC_HS_*（28 文件残留引用）
- **desired behavior**: 握手协议层融入各项目 msg/protocol 模块、会话层融入 io/network/sbt 模块、服务端分流内部化；符号 rdb_hs_*/dm_hs_*/obk_hs_*；全仓共享痕迹归零
- **key interfaces**: 握手帧编解码、算法映射、会话生命周期与读写分发、客户端协商、服务端首阶段分流
- **acceptance criteria**: 运行三项目现有测试套件得到全绿（存量失败经 stash 对照甄别）；运行全仓 grep "rpc_hs_|rpc-handshake" 得到 0 命中且五份 handshake 文件不存在；运行全量构建得到成功无新增警告
- **out of scope**: 协议字节变更、rpc 项目握手实现、time 链路迁移、存量测试失败修复
- **information gaps**: 无（前置 T0351 已完成删除，落点已核实）
- **dedup results**: 前置任务 T0351 已归档，本任务为其形态重构延续，非重复
- **recommended next steps**: 终审后按切片 A→D 推进 Do
