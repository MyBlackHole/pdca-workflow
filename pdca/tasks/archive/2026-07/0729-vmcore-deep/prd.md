# 深入分析 vmcore 崩溃原因（dm 悬空指针追查）

## Goal

深入分析 dm_softirq_done 中 tio->ti 悬空指针的根因，定位具体的内存释放路径或竞争条件。

## 环境与资源

- **vmlinux**: `/home/black/shqddb2/kernel-rpm/usr/lib/debug/lib/modules/3.10.0-1160.83.1.el7.x86_64/vmlinux`
- **vmcore**: `/tmp/vmcore-mnt/vmcore`
- **源码树**: `/home/black/shqddb2/kernel-rpm/src/linux-3.10.0-1160.83.1.el7/`
- **tmux 目标窗格**: session `0`, window `0`, pane `0`（0:0.0）
- **上一轮产出**: `records/R0142-vmcore-analysis/`

## 已知事实（从 T0142 继承）

- 崩溃点: `drivers/md/dm-rq.c:361` = `dm_softirq_done+97`
- 崩溃指令: `mov 0x8(%rdi),%rdx`（`tio->ti->type` 解引用）
- CR2: `ffffbd16abacc048`, PTE=0
- RDI (tio->ti): `ffffbd16abacc040`
- R13 (tio)：`ffff9ff42a3f1a40`
- R12 (clone): `ffff9ff862cf9600`
- `tio->clone` 非 NULL，走的是 `dm_done` 路径

## Requirements

- [ ] `bt` 获取崩溃线程堆栈
- [ ] `bt -a` 获取所有 CPU 堆栈，查找操作 dm 设备的线程
- [ ] `struct dm_rq_target_io ffff9ff42a3f1a40` 检查完整内容
- [ ] `struct dm_target ffffbd16abacc040` 查看无效地址内容
- [ ] `struct request ffff9ff862cf9600` 查看 clone 请求内容
- [ ] `struct request <orig_rq>` 查看原始请求内容
- [ ] `log` 提取崩溃前后日志，查找 dm 相关操作
- [ ] `dev -d` 查看 dm 设备状态
- [ ] `rd` 读取 slab 信息检查 use-after-free 迹象
- [ ] 针对 Oracle ACFS/ADVM 模块的符号检查
- [ ] 每个栈帧对应源码位置
- [ ] 形成根因结论

## 验收标准

- [ ] crash 成功加载并提取完整信息
- [ ] 崩溃线程完整 bt 含寄存器状态
- [ ] 所有 CPU 状态已检查，排除并发竞争
- [ ] tio/clone/ti 结构体内容已检查并记录
- [ ] dm 设备表状态已检查
- [ ] 崩溃前后日志已检查
- [ ] slab 状态已检查
- [ ] 根因分析指向具体的内存释放点或竞争代码路径
