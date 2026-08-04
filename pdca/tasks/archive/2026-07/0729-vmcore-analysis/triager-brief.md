# Triage Brief

## Classification
- **category**: bug
- **scenario_type**: research
- **reason**: 分析已发生的内核崩溃，定位根因

## Verification
- vmlinux 存在: `/home/black/shqddb2/kernel-rpm/usr/lib/debug/lib/modules/3.10.0-1160.83.1.el7.x86_64/vmlinux`
- vmcore 存在: `/tmp/vmcore-mnt/vmcore`
- crash 工具可用: `/usr/bin/crash`
- tmux session 0 已运行，0:0.0 窗格可用
- 内核源码树存在

## Dedup
- 归档任务中无重复
- knowledge 中无相关记录

## Information Gaps
- vmcore 原始路径与用户指定不同，实际 vmcore 在 `/tmp/vmcore-mnt/vmcore`
- vmlinux 路径与用户指定不同，实际在 `/home/black/shqddb2/kernel-rpm/usr/lib/debug/lib/modules/3.10.0-1160.83.1.el7.x86_64/vmlinux`

## Recommended Next Steps
P1 → P2 → P3 → P6 (快速路径，因任务明确不需复杂澄清)
