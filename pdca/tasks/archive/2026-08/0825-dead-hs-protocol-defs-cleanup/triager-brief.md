# Triage Brief — 0825-dead-hs-protocol-defs-cleanup

- **category**: enhancement
- **scenario_type**: development
- **summary**: 清理 dmsbtex/libobk 握手协议层零引用死定义（早期协议设计残留，T3956 归一时暴露）。
- **current behavior**: 两头文件存在 16 项零引用宏/枚举/结构（DM_HS_MAGIC/VERSION/MAX_PAYLOAD/FIXED_SIZE/OK_TIME/OK_PLAIN、dm_hs_message_t、dm_hs_result_t、dm_hs_operation、dm_hs_flags 及 OBK 对应项），误导读者以为存在 magic/version 协议语义。
- **desired behavior**: 仅保留有引用的定义，头文件与实际帧格式一致。
- **key interfaces**: dmsbtex 握手协议头、libobk 握手协议头；实际帧编解码不受影响。
- **acceptance criteria**:
  - 运行全量 xmake 构建通过，无新增警告。
  - 运行 dmsbtex/libobk/rdbcomm session test 与 rpc mixed_mtls_integration 全部通过。
  - grep 确认被删符号全仓库零残留引用。
- **out of scope**: OPT_NULL/OPT_MAXNUM（值偏移风险）；libs 死测试文件清理；任何行为变更。
- **information gaps**: 无（清单已逐项验证）。
- **dedup results**: T3956 只归一了结果码，未清理这些残留；无重复任务。
- **recommended next steps**: 小任务直接顺序执行：删除 → 构建 → 回归 → 提交。
