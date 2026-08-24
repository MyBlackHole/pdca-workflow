# 分析部署二进制 xtrabackup 是否处理 validate_first_page/重试逻辑

## 问题陈述

T0389 已从源码证明上游 xtrabackup 对表空间首页校验失败零重试（扫描路径）。
现需验证 GoldenDB 实际部署的二进制
`/home/black/Downloads/goldendb-xtrabackup/xtrabackup`（ELF aarch64, 787MB,
with debug_info, not stripped）是否定制处理了该验证问题或实现了重试逻辑，
并给出二进制级证据。

## 方案概述

符号表 + 定向反汇编取证（aarch64-linux-gnu-objdump）：
1. 版本/来源鉴定；2. 关键函数调用图重建（validate_first_page /
fil_open_for_xtrabackup / open_ibds / read_lsn_and_check_flags /
xb_fil_cur_read / open_or_create）；3. 循环回边甄别（真循环 vs 共享错误出口）；
4. backup 流程可达性判定。

## 已验证事实（P0 claim verification）

- 二进制含 `[gdb]` 前缀日志串、gdblib 构建路径、版本 8.0.25 → GoldenDB 定制构建；
  本地源码树为 Percona 官方 tarball，二者非同源。
- 关键字符串齐备："Checksum mismatch"、"in datafile"、
  "failed to read page after 10 retries"、"Database page corruption detected at page"。
- 符号存在：validate_first_page(0x1422100)、xb_fil_cur_read(0xda8ef8)、
  **read_lsn_and_check_flags(0x142e810)**、restore_from_doublewrite(0x141f9e8)。
  上游 HOTBACKUP 编译应排除前述 SysTablespace 函数 → 定制改动信号。
- 调用计数（反汇编 bl 目标解析）：
  - validate_first_page 内部：read_first_page×1、is_corrupted×1、
    restore_from_doublewrite×0；90 个大回边经内容甄别均为共享错误出口
    （ios_base/logger 初始化块），非循环 → 无内部重试，与上游一致。
  - fil_open_for_xtrabackup：open_read_only×1 + validate_first_page×1，
    0 回边 → 扫描路径仍零重试。
  - read_lsn_and_check_flags：read_first_page×2、validate_first_page×2、
    restore_from_doublewrite×1，9 回边 → retry×2+dblwr 恢复结构被编入。
  - SysTablespace::open_or_create 含 2 处直接调用 read_lsn_and_check_flags；
    xb_load_tablespaces 调用 check_file_spec + open_or_create → backup 流程可达。
  - xb_fil_cur_read：os_file_read_no_error_handling×2 + is_corrupted×1 +
    17 回边 → 拷贝路径 10 次重试保留。

## 验收标准

- [ ] AC-1: 报告给出二进制来源/版本鉴定结论及证据（[gdb] 字符串、构建路径、8.0.25）。
- [ ] AC-2: 报告对 6 个关键函数逐一给出调用计数与重试判定，附反汇编获取命令可复现。
- [ ] AC-3: 报告明确回答主问题——用户表空间 .ibd 扫描路径是否仍有重试（答案:否），
       并指出定制的实际改动点（ibdata 路径编入 retry×2+restore_from_doublewrite）。
- [ ] AC-4: 报告区分"循环回边"与"共享错误出口"的甄别方法，防止误判。
- [ ] AC-5: 结论映射生产影响：本案 .ibd 场景在定制版下行为是否改变（答案:未改变）。

## Seam 分析（research 场景）

### 声明的测试接缝
- seam: （research 场景无自动化测试产物；验收以报告内可复现反汇编命令为准）
