# AC-2 strace 验证：socket 均被 close

命令: strace -f -tt -p 1612588 -e trace=socket,connect,close,shutdown

修复后快照（J4）关键序列：
- socket(14) connect(14 8811) [14:00:59.228395/.228593] -> close(14) [14:00:59.304925]
- socket(17) connect(17 8811) [14:00:59.257755/.258022] -> close(17) [14:00:59.304830]

修复前对比（旧进程 1553045，I9）：
- socket(26) connect(26 8811) 后线程退出，无 close(26)
- socket(31) connect(31 8811) 后线程退出，无 close(31)

结论：修复后快照期间所有新建到 8811 的 socket 均被 close，无未关闭 socket。
