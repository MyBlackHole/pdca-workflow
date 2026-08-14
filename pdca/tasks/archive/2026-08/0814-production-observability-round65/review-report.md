# T0251 双轴代码审查

对比基点：当前 `HEAD`（T0249 LMDB no-mmap gate）与工作树变更。

## 标准轴

- Blocking：0。`tests/style_check.sh .` 通过；无 class/virtual/exception/std::thread/lambda 回归，入口文件行数仍在约束内。
- Blocking：0。文件 sink 使用 `O_NOFOLLOW`、`0600`、互斥保护和 bounded message/field；写失败降级 stderr，不把日志失败传播为传输失败。
- Warning：文本 sink 的字段值采用引号包裹以避免污染已有 `key=<number>` 进度解析；JSON sink 保持稳定字符串字段，属于兼容性取舍。

## 规范轴

- Blocking：0。覆盖 client/server 配置、stderr text 默认值、JSONL 必需字段、并发整行写入、轮转、权限、失败降级、token 不落盘和 lifecycle/transfer/incremental/checkpoint 事件。
- Blocking：0。Make TLS ON、CMake TLS ON/OFF、unit、logging integration、全量 integration 与 style 均有登记证据。
- Info：TREE checkpoint 的全量确认表仍是现有内存结构，明确留在后续独立任务；本轮没有把日志改造误报为内存问题的解决方案。

## 结论

标准轴发现 0 个 Blocking，规范轴发现 0 个 Blocking；允许进入 Check。后续应单独推进磁盘索引/流式恢复，不能把 `unordered_map` 扩容当作海量续传方案。
