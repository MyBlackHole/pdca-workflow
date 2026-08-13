# Round 61 终审代码审查

审查范围：`src/transfer.hpp`、`src/transfer.cpp`、`src/backupctl.cpp`、`tests/unit.cpp`、`tests/benchmark_tree.sh`。
固定基线：`4f3aa8a`；规范来源：本任务 `prd.md`；编码依据：`docs/CODING_STYLE.md`。

## 标准轴

- C-style 约束：生产代码使用显式 callback/context，不引入 lambda、异常、`std::thread` 或 Reactor 越权调用。
- 边界安全：pack count、flags、item length、blob size、trailing bytes 均在 callback 前校验；单元覆盖空包、截断、越界、尾随和 callback fail-fast。
- 生命周期：callback 中仅把当前 blob 移交给 pool；pool 仍负责队列背压、首错锁存和线程 join；vector API 保留兼容实现。
- 线程安全：流式解码发生在接收线程，pool enqueue 仍通过既有 mutex/条件变量；无新增共享无锁状态。
- 统计一致性：每个合法 item 在 callback 中递增 pack 文件计数；失败传播会停止后续解析并恢复首错。

结论：未发现 Blocking 或 High 严重度问题；标准轴发现 0 项。

## 规范轴

- AC-1/AC-3：真实 TLS small-pack 集成覆盖 workers=0/4、hardlink、metrics、失败路径；旧 writer pool 约束保持。
- AC-2：`decode_small_file_pack_each` 按 wire 顺序回调，并对空包、截断、长度越界、非法 blob、trailing bytes 和 callback error fail-fast。
- AC-4：旧提交 binary 与新 binary 以 10000 文件、4 对交替样本比较耗时、files/s、峰值 RSS 和 queue 相关输出；workers=0 耗时劣化约 1.9%，workers=4 基本持平，strict+checksum 提升约 4.5%，峰值 RSS 均下降。
- AC-5/AC-6：Make TLS=1/TLS=0、CMake TLS OFF/ON、既有 tree/FSM 和 style 回归通过；wire protocol、默认 workers=0 和普通大文件路径未改变。

结论：未发现 PRD 缺失、范围蔓延或实现方式违约；规范轴发现 0 项。

最终门禁：Blocking=0；标准轴 0 项，规范轴 0 项。
