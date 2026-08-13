# Round 60 终审代码审查

审查范围：`src/backupctl.cpp`、`tests/tls_tree_small_pack_integration.sh`、`tests/benchmark_tree.sh`。
审查基线：固定点提交 `d1180eb init`；规范依据：`docs/CODING_STYLE.md`。

## 标准轴

- 线程安全：队列、错误闩锁、活动计数、峰值指标均由 `mu_` 保护；worker 不再并发写共享 `TransferStats`，由 `drain()` 合并局部统计。
- 生命周期：`SmallLocalWriterPool` 析构时停止并 join 全部线程；初始化失败路径复用同一回收逻辑。
- 错误传播：首个 worker 错误被保留，清空待处理队列并唤醒生产者；`enqueue()`/`drain()` 返回失败，GET 主循环不再处理后续 hardlink、目录元数据或 `TREE_END`。
- 背压：队列上限保持 `max(8, workers * 8)`，生产者在条件变量上等待，指标记录等待次数。
- 风格：未引入异常、lambda、`std::thread` 或新的 Reactor 越权调用；`git diff --check` 通过。

结论：未发现 Blocking 或 High 严重度问题。

## 规范轴

- AC-1/2/3：TLS 小文件 pack 集成覆盖 workers=0/4、计数边界、峰值边界、hardlink inode 和顺序屏障。
- AC-4：只读目标根触发确定性落盘失败；命令非零退出，后续 hardlink 不出现，线程由析构回收。
- AC-5：基准脚本执行 workers=0 对 workers=1/2/4/8 的四组配对，以及 checksum=1、durability=strict 下 0/4 配对；输出均值、最小值、最大值和 files/s。
- AC-6/7：默认 workers=0 路径、既有 tree/FSM 回归、GNU Make TLS=0/1、CMake TLS OFF/ON 均验证。

结论：规范实现与 PRD 一致，Blocking=0，建议进入 Check。
