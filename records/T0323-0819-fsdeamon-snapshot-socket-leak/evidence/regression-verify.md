# 回归验证记录（T0323 fsdeamon snapshot socket 泄漏修复）

## 环境
- 修复前进程 1553045：fd=30, 8811连接=20（经 I4~I9 累积泄漏）
- 修复后进程 1612588：基线 fd=14, 8811连接=4
- source: qemu-system-x86 (pid 1544482) 监听 127.0.0.1:8811

## AC-1 验证：连续 3 次增量 snapshot 连接数不增长
| 快照 | fd 数 | 8811 连接数 |
|------|------|------------|
| 基线 | 14 | 4 |
| J1 (inc) | 14 | 4 |
| J2 (inc) | 14 | 4 |
| J3 (inc) | 14 | 4 |

结论：通过。每次快照后 fd 与 8811 连接数保持稳定，无 CLOSE-WAIT 累积增长。

## AC-2 strace 验证：socket 均被 close
- strace -f -tt -p 1612588 -e trace=socket,connect,close,shutdown
- 修复后：socket(14) connect(14) [行20-21] -> close(14) [行30]；socket(17) connect(17) [行24-25] -> close(17) [行33]。全部配对关闭。
- 修复前对比：socket(26)/socket(31) connect 后线程退出无 close（泄漏）。

结论：通过。

## AC-3 fd 数前后一致
单次 snapshot 后 fd 数保持在 14（与基线一致），除 snapshot 临时文件 fd 外无增长。

## AC-5/AC-6
4 次增量快照（J1~J4）数据均成功返回，result=true，不影响快照正确性；
快照成功路径（SnapshotSync/SnapshotEnd）释放 ver/bak session，DEFAULT 常驻 3 连接保持。
