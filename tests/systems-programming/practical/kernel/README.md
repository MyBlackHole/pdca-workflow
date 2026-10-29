# 内核态资源退出案例

本目录的 [KUnit 源码](systems-resource-test.c) 直接运行目标树的 workqueue、
completion 和 kthread API。它验证待执行取消、运行中同步取消、超时后继续保护资源、
禁止重排后恢复和先完成后等待；不是用户态 pthread 对内核语义的替身。

测试上下文与 payload 由 KUnit 管理，最后注册的清理 action 先释放等待门、停止辅助线程、
同步取消工作并销毁队列，再让 KUnit 释放内存。辅助线程报告取消结果后仍等候
`kthread_stop()`，避免完成通知先到、task_struct 却在清理前退出的问题。

原始 `/home/black/Documents/linux-7.3` 不带可核验的 Git 元数据，版本由 Makefile 标为
7.3.0；其上游 commit、未修改状态与“最新主线”身份均为 unknown。
构建只改工作区复制件，不改原树，也不向宿主装载模块。

## 构建与运行

使用新的输出根，避免重复向 Kconfig/Makefile 追加。以下路径是本机示例；重放时可换成
自己的工作区绝对路径。工具包括 Python 3、目标树 Kbuild 所需工具和 QEMU x86_64。
完整树副本和构建需要足够磁盘空间。

```sh
assets=/home/black/.agents/pdca/tests/systems-programming/practical/kernel
output=/home/black/skill-work/validation/engineering-consolidation/practical-kernel-replay
mkdir -p "$output/tmp" "$output/cache" "$output/runtime" "$output/logs" "$output/build"
export TMPDIR="$output/tmp" TMP="$output/tmp" TEMP="$output/tmp"
export XDG_CACHE_HOME="$output/cache" XDG_RUNTIME_DIR="$output/runtime"
export PYTHONDONTWRITEBYTECODE=1
cp -a --reflink=auto /home/black/Documents/linux-7.3 "$output/source"
cp "$assets/systems-resource-test.c" "$output/source/lib/kunit/systems-resource-test.c"
cat "$assets/Kconfig.fragment" >> "$output/source/lib/kunit/Kconfig"
cat "$assets/Makefile.fragment" >> "$output/source/lib/kunit/Makefile"
cd "$output/source"
python3 -B tools/testing/kunit/kunit.py build --arch=x86_64 --kunitconfig="$assets/.kunitconfig" --build_dir="$output/build" --jobs=8 > "$output/logs/build.log" 2>&1
timeout 120 qemu-system-x86_64 -nodefaults -m 1024 -smp 2 -accel tcg -kernel "$output/build/arch/x86/boot/bzImage" -append "console=ttyS0 kunit.enable=1 kunit.filter_glob=systems-resource kunit_shutdown=reboot" -no-reboot -nographic -serial stdio -monitor none -bios qboot.rom > "$output/logs/boot.log" 2>&1
```

[.kunitconfig](.kunitconfig) 启用 SMP（2 CPU）、KASAN、lockdep、原子上下文和 work 对象诊断。
应核对生成的 .config 和启动日志，而不只检查输入配置文件。KUnit 的 `ok/not ok`、
套件总计、退出情况及内核诊断需共同审查；QEMU 退出 0 本身不代表测试通过。

这六个软件场景不证明真实设备 IRQ/DMA/解绑、RT、其他架构、KCSAN 或错误注入矩阵。
`cancel_work_sync()` 也不是在任意并发生产者存在时永久禁止重排的手段；
禁止重排案例使用目标树提供的 `disable_work_sync()`。
