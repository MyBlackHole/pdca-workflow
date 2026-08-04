# 分析 vmcore 崩溃原因并关联内核源码

## Goal

通过 crash 工具分析 vmcore，定位内核崩溃根因，并关联到 `kernel-rpm/src/linux-3.10.0-1160.83.1.el7` 源码的具体位置（文件:行号）。

## 环境与资源

- **vmlinux**: `/home/black/shqddb2/kernel-rpm/usr/lib/debug/lib/modules/3.10.0-1160.83.1.el7.x86_64/vmlinux`
- **vmcore**: `/tmp/vmcore-mnt/vmcore`
- **源码树**: `/home/black/shqddb2/kernel-rpm/src/linux-3.10.0-1160.83.1.el7/`
- **tmux 目标窗格**: session `0`, window `0`, pane `0`（0:0.0）
- **crash 命令**: `crash /usr/lib/debug/usr/lib/modules/3.10.0-1160.83.1.el7.x86_64/vmlinux /nbudata/vmcore/vmcore`（但实际路径不同，采用实际路径）

## Requirements

- [ ] 通过 tmux 在 0:0.0 窗格执行 crash 命令加载 vmcore
- [ ] 使用 crash 命令 `bt` 获取崩溃线程堆栈
- [ ] 使用 `log` 或 `dmesg` 获取内核崩溃日志
- [ ] 使用 `dis` 反汇编关键帧
- [ ] 使用 `files` / `struct` / `task` 等命令获取崩溃上下文
- [ ] 堆栈每一帧精确匹配到源码位置
- [ ] 形成根因结论

## 验收标准

- [ ] crash 命令成功执行，无加载错误
- [ ] 堆栈回溯完整，至少显示崩溃函数及调用链
- [ ] 每个栈帧都关联了源码文件:行号
- [ ] 根因分析明确指出问题函数和崩溃机制

