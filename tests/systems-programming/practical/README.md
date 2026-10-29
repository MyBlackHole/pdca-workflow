# systems-programming 的实体验收资产

本目录位于仓库的 `tests/`，不属于 `skills/systems-programming/`。
代码用于验证工程决策能否落到可运行的行为，不是 skill 正文、生产模块或必须采用的实现。
AI 正常加载 skill 时不会加载或执行这里的代码。

- [CASE.md](CASE.md) 与 [vstore.h](vstore.h)：无方案提示的“可借用版本缓存”业务题及固定 C ABI。
- [test_vstore.c](test_vstore.c)：对两份冻结实现使用相同的公共接口断言，覆盖版本、额度、跨线程归还、关闭和并发。
- [kernel/README.md](kernel/README.md)：使用本地 Linux 7.3 副本构建、在 QEMU 中运行的 KUnit 案例。
- [userspace/README.md](userspace/README.md)：此前异步队列案例及本轮动态诊断、资源/性能测量入口。
- [本轮报告](../../../docs/reviews/2026-10-29-practical-skill-validation.md)：任务隔离、实际结果、取舍和未覆盖条件。

版本缓存由两个新上下文分别实现。对照上下文不读取工程 skill 正文，实验上下文读取本技能及本题相关参考资料；
两者收到相同的业务题与头文件，不获知评审答案或彼此输出。对照仍受宿主通用指令影响，不能称为完全无指导。
两份实现及其自测冻结在本轮工作区，报告记录路径和摘要；不把模型生成的方案复制成 skill 的固定答案。

验证输出统一放在工作区的显式输出根。不要写入本资产目录或 `/tmp`；编译前设置
TMPDIR/TMP/TEMP，GCC 使用 `-save-temps=obj` 和显式输出路径。
例如，已存在的实现目录含 `vstore.c` 时：

```sh
assets=/home/black/.agents/pdca/tests/systems-programming/practical
output=/home/black/skill-work/validation/engineering-consolidation/practical-replay
implementation=/absolute/workspace/frozen-implementation
mkdir -p "$output/tmp" "$output/check"
export TMPDIR="$output/tmp" TMP="$output/tmp" TEMP="$output/tmp"
gcc -std=c11 -O2 -g -Wall -Wextra -Werror -Wpedantic -pthread -save-temps=obj -I"$assets" "$assets/test_vstore.c" "$implementation/vstore.c" -o "$output/check/test_vstore"
timeout 60 "$output/check/test_vstore"
```

统一测试观察公开契约，不要求哈希表、链表、池、锁外分配或某一种替换策略。
测试通过与有限动态诊断均不是全状态空间证明；一个模型样本也不能证明 skill 必然改善未来所有任务。
