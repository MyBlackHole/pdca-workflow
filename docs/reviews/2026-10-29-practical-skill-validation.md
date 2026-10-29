# systems-programming 3.3.0 实体验收

日期：2026-10-29。基线提交：`355ac202d28512bd0a047bfdb4bc7322649ffc5f`。

本轮落实用户批准的四项验证：无方案提示的独立实现、真实内核案例、动态诊断、资源与性能基线。
规则入口与参考资料没有修改，技能版本仍为 3.3.0；未发现需要据此增加通用规则的失败。
结果说明本次样本能落实资源与并发原则，不证明 skill 必然优于通用模型或涵盖所有工程场景。

## 产物边界

- 可复用需求、测试源与构建入口放在 [tests/systems-programming/practical](../../tests/systems-programming/practical/README.md)，不放入 skill 正文或 references。
- 原始实现、编译产物、内核副本、临时目录、缓存与日志位于工作区：
  `/home/black/skill-work/validation/engineering-consolidation/practical-20261029-r2`，下文记为 W。
- `skills/systems-programming/` 没有引入案例代码，正常加载技能不加载或执行这些测试。
  不创建正式 PDCA task/phase，不访问 records；本轮提交不包含用户已有的其他改动，不推送。

## 四项结果

| 项目 | 实际结果 | 结论边界 |
| --- | --- | --- |
| 无提示独立实现 | 两个新上下文分别实现版本缓存，两者均通过统一公共接口测试；各自的 ASan/UBSan、TSan 与 C++ 调用亦通过 | 只有一对样本，不能计算普遍提升或推断加载技能的实现必然更优 |
| 真实内核案例 | x86_64、2 CPU、QEMU TCG；六项 KUnit 全部通过，KASAN、lockdep 与对象/原子上下文诊断启用 | 不覆盖真实 IRQ/DMA、驱动解绑、RT、其他架构或 KCSAN |
| 动态诊断 | 固定异步队列在普通、ASan/UBSan、TSan 下通过 11 组自测、独立接口检查及 C++ 调用 | LSan 因当前 ptrace 环境失败；关闭泄漏扫描后的通过不等于 LSan 通过 |
| 资源与性能 | 四种负载，普通与仪表构建各五次，共 40 个进程、800,000 条消息；资源归零且逻辑峰值不越界 | 当前实现的单机短批次基线，无优化前后对比，不宣称加速 |

## 无方案提示的独立实现

固定输入为 [CASE.md](../../tests/systems-programming/practical/CASE.md) 和
[vstore.h](../../tests/systems-programming/practical/vstore.h)。
任务只给出二进制快照、借用旧版本、多线程、额度、错误和退出契约，没有指定数据结构、
预留算法、锁范围或预期评分答案。两者不读取对方产物、旧评审答案或外网，未改动固定输入。

对照上下文不读取工程 skill 正文；实验上下文读取入口及本题相关的原则、环境和验证资料。
对照仍受宿主通用指令以及可见的技能描述影响，不能称为“完全无指导”。
产物分别冻结于 `W/control` 和 `W/with-skill`，其自述必须与源码、日志和父级检查共同使用。

| 观察项 | 对照实现 | 加载 skill 的实现 |
| --- | --- | --- |
| 索引与锁 | 线性版本链表，一把 mutex | 64 个哈希桶，一把 mutex |
| 内存与锁范围 | 分配、复制、回收在锁内；无借用时原位更新 | 单次头+payload 分配；先预留额度，锁外分配/复制/回收，再复查关闭并提交 |
| 旧视图 | 有借用的旧版本保持不变，最后归还回收 | 同样保护旧版本；退休版本由借用责任保持存活 |
| 满额替换 | 无借用时可复用旧节点和逻辑额度 | 每次发布需要额外构造额度；满额当前缓存不能继续替换，须配置余量 |
| 取舍 | 简单，满额时更新能力较强；大块复制延长临界区 | 临界区避开大块复制，额度覆盖构造和回收窗口；准入更保守 |

实验实现确实主动选择了资源预留、锁外大块操作、提交复查、借用生命周期和整体统计同步，
并以 allocator 暂停验证其他接口可以前进；这些是本样本的可审查设计证据。
其保守准入需要业务接受容量余量。题目没有要求满额、无借用时的替换必须成功，
因此不把这一取舍事后改判为违反原需求；也不据此声称它全面优于对照。
如果未来业务要求该能力，应先明确契约，再验证相应设计，而不是暗改本次题目。

父级 [test_vstore.c](../../tests/systems-programming/practical/test_vstore.c) 分别与两份冻结源码链接：
严格 C11 告警、二进制输入复用、多个借用版本、条数/字节额度、跨线程归还、失败输出清零、
零长度、重复 close、忙 destroy 后归还重试，以及四发布者/四读取者的 32,000 次 publish/acquire 调用，
均通过。并发期间还检查完整 stats 和让出 CPU 前后的视图内容。
不包含私有结构，不要求某种容器，也不解释成功视图的 opaque token。
原先对零长度成功 token 必须非 NULL 的多余断言已在自审中删除；借用责任改由 busy destroy 等公开行为证明。

两边原始自测同时提供分配失败恢复和并发关闭证据；实验侧还覆盖分配前、分配后未提交、
以及 free 前暂停的交错。父级已读取实际源码与最终日志，并复核冻结清单全部匹配。
对照的紧额度自测允许 `-EAGAIN`，不把拒绝次数当成错误或性能结果。

| 固定产物 | SHA-256 |
| --- | --- |
| CASE.md | `5d0389110d840a2119f4c92194697fb3748d17d7196c5768bf0c251d7b4dba64` |
| vstore.h | `2f98ca88dd66cace82bea1eb3a8afdaf3ba478fda2729af8a20b561cac047fa4` |
| control/vstore.c | `65583e804104e071dfac9cd946c3e955e376c1d18c4803b93132371ba1ea11f3` |
| with-skill/vstore.c | `edcc0e05b56cb16e90b7d581342615596984eb26da1ab031123a7b91f3bf22f6` |

源码清单分别为 `W/control/FREEZE.sha256` 和 `W/with-skill/logs/source-freeze.sha256`；
共同验收日志为 `W/logs/parent-control.log`、`parent-with-skill.log`。
两份代码没有因后续评审被悄然修补。

## 内核态案例与源码边界

原始 `/home/black/Documents/linux-7.3` 无可核验的 Git 元数据，Makefile 标记 7.3.0；
上游 commit、是否原版以及“最新主线”身份仍为 unknown。
本轮通过 `cp -a --reflink=auto` 复制到 `W/kernel-source`，只修改该副本的 KUnit 接入与新增测试，
输出使用 `W/kernel-build`；没有装载宿主模块。先前记录的 24 个原树文件摘要全部保持一致，
事实记录在 `W/logs/original-source-recheck.json`。

运行方式见 [内核案例入口](../../tests/systems-programming/practical/kernel/README.md)。
实际构建为目标树 `kunit.py build --arch=x86_64 --jobs=8`，运行使用 QEMU TCG、1024 MiB、
2 CPU、串口控制台和 `kunit.filter_glob=systems-resource`，120 秒外层超时。
生成的 .config 包含 KASAN_GENERIC、PROVE_LOCKING/LOCKDEP、DEBUG_ATOMIC_SLEEP、
DEBUG_OBJECTS_WORK 与 SMP；测试对象的实际编译命令含 `-fsanitize=kernel-address`，
启动日志确认 2 CPU 和 lock dependency validator。

| KUnit 场景 | 实际结果 |
| --- | --- |
| 提交后读取仍存活的 payload | PASS |
| 取消尚未执行的工作，回调不执行 | PASS |
| 对正在运行的回调同步取消并等待 | PASS |
| 等待超时后保持请求与 payload 存活，再释放等待门并收敛 | PASS |
| disable_work_sync 阻止重排，enable_work 后恢复 | PASS |
| complete 先于等待者，两个完成令牌逐次消费 | PASS |

KTAP 总计 `pass:6 fail:0 skip:0 total:6`，QEMU 正常重启退出 0。
日志未见 KASAN、锁循环、work 对象或原子上下文违规报告，但存在 QEMU 启动时的
ACPI `AE_BAD_PARAMETER` 与 SCI handler 错误，不能声称整段启动日志无错误；
该软件测试正常执行，不据此验证 ACPI 或硬件行为。
一 jiffy 的负等待只提供本次调度下的观察，不是对全部调度交错的证明。

保留首次配置失败 `W/logs/kernel-build.log`：
`CONFIG_DEBUG_OBJECTS_WORK=y` 的依赖 `CONFIG_DEBUG_OBJECTS=y` 未开启。
依据本地 `lib/Kconfig.debug` 修正后，构建成功，日志为 `kernel-build-debug.log`。
静态自审同时发现辅助 kthread 不能在完成通知后提前退出、再由清理路径调用 stop；
根据本地 `kernel/kthread.c` 契约改为等待 `kthread_should_stop()` 后退出，再进行实际构建运行。
这不是声称动态检测发现了旧版测试中的缺陷。

目标树 `scripts/checkpatch.pl --no-tree --strict -f` 检查新增 KUnit 源码：
`0 errors, 0 warnings, 0 checks`，日志为 `W/logs/kernel-checkpatch.log`。
测试清理 action 先结束工作和辅助线程，再让 KUnit 回收上下文；不是收到 completion 就直接释放后台对象。

## 用户态动态诊断

固定案例的 `rq.c` SHA-256 为
`d7563fe1fcbe2c96df64ba02c04e28bc712dab6e076967ab2387f9d3635e97c0`，
与上一轮验收实现一致。本轮增加可重放的构建入口和测量，不改队列算法。
运行入口见 [用户态说明](../../tests/systems-programming/practical/userspace/README.md)。

实际在该目录执行：

```sh
make OUTPUT_ROOT=/home/black/skill-work/validation/engineering-consolidation/practical-20261029-r2/userspace check asan tsan bench
```

命令退出 0。普通、ASan/UBSan、TSan 三种构建分别通过：
11 组资源/失败/回调/关闭自测、父级独立公共接口检查、C++11 调用。
C++ 禁用异常和 RTTI，并由 GCC 链接；普通二进制动态依赖只有 libc，没有 C++ 库。
wrapper 断言覆盖分配与线程回收归零，不读取队列私有结构。
新增测量包装器另在 ASan/UBSan 和 TSan 下各运行四生产者、4096 字节、2000 条消息，
均退出 0，分配归零；这两次诊断数据未混入性能基线。

两份版本缓存初次开启 LSan 都失败，实际错误为 ptrace 环境不支持：
`W/control/logs/asan.25`、`W/with-skill/logs/asan.64`。
后续 ASan/UBSan 明确设置 `detect_leaks=0`，通过只指内存访问/未定义行为诊断，
没有重试并伪称 LSan 通过。队列同样使用该显式配置。
所有编译前设置工作区 TMPDIR/TMP/TEMP，GCC 采用 `-save-temps=obj` 与显式输出，
sanitizer 日志固定到工作区且关闭外部符号化；KUnit/QEMU 输出与缓存也显式定位。
没有运行已知必须向 /tmp 写入的测试。

## 资源和性能基线

环境：AMD Ryzen 7 PRO 4750U，8 核 16 线程，x86_64；
宿主 Linux 7.2.11-arch1-1，GCC 16.2.1 20260810，QEMU 11.1.2。
环境事实见 `W/logs/environment.txt`。未固定 CPU 亲和性、频率或系统其他负载；
本任务的内核构建与 QEMU 在最终测量前均已结束。

普通与仪表构建分开，每种 1/4 生产者 × 64/4096 字节负载各运行五个新进程，
每批 20,000 条消息，队列预算为 512 条、512 × payload 字节。
构建 `-O2`，断言与逐条内容验证开启。
吞吐计时覆盖生产者启动屏障至 close 收敛，包含验证与 EAGAIN 重试，
不包含队列创建和最终 destroy。
每条延迟从最后一次成功的 submit 尝试开始到回调入口；
该条先前的容量重试只计入总吞吐时间，不计入这条延迟，不称为端到端或回调完成延迟。

未插桩实现的基线如下。p99 列是“五次各自 p99 的中位数和范围”，不是合并所有样本后的 p99。

| 生产者 / payload | 吞吐 k条/s：中位数［范围］ | p99 ms：中位数［范围］ | VmHWM KiB：中位数［范围］ | 五次最大逻辑峰值：条 / 字节 |
| --- | --- | --- | --- | --- |
| 1 / 64 B | 582.6［511.1–606.8］ | 0.237［0.040–0.557］ | 2416［2404–2432］ | 334 / 21376 |
| 4 / 64 B | 521.1［497.8–553.9］ | 1.188［1.017–1.369］ | 2540［2516–2544］ | 512 / 32768 |
| 1 / 4096 B | 295.2［261.1–308.4］ | 2.957［2.380–3.222］ | 4268［4204–4268］ | 512 / 2097152 |
| 4 / 4096 B | 198.6［181.7–269.7］ | 3.352［2.659–4.502］ | 5132［4900–5992］ | 512 / 2097152 |

仪表版本只重命名队列编译单元的 malloc/free 和锁/cond_wait 调用，不计测试数组、libc 内部分配或线程资源。
下表每次批量均为 20,000 条消息；malloc 次数包括队列本体一次。
显式 lock 等待不包含 cond_wait 的隐含重获锁；持锁区段排除 cond_wait 睡眠，并在 unlock 调用前停止计时。

| 生产者 / payload | 每批模块 malloc 调用 | 显式 lock 平均等待 μs：五次中位数［范围］ | 持锁区段平均 μs：五次中位数［范围］ | destroy 后活跃分配 |
| --- | --- | --- | --- | --- |
| 1 / 64 B | 20001 | 4.329［4.196–4.593］ | 1.598［1.558–1.644］ | 0 |
| 4 / 64 B | 20001 | 14.616［14.424–16.609］ | 1.513［1.499–1.565］ | 0 |
| 1 / 4096 B | 20001 | 5.500［5.433–6.484］ | 1.583［1.558–1.610］ | 0 |
| 4 / 4096 B | 20001 | 15.878［14.923–16.445］ | 1.548［1.531–1.592］ | 0 |

这些锁时间受到时钟读取与原子计数影响；仪表构建本身明显变慢，不能当成未插桩的生产锁时长，
也不能与普通吞吐相除声称产品收益。当前数据只是后续同条件优化的基线。
没有加入对象池、无锁结构或新的性能候选，没有进行版本缓存两份实现的性能比较。

首轮发现 getrusage 的 ru_maxrss 在 exec 后仍可能带入启动器历史高水位，40 次都报告 14028 KiB。
保留 `W/logs/benchmark-initial-rusage.jsonl`，新增 Linux `/proc/self/status` 的 VmHWM 后重跑。
最终仍同时记录 `rusage_maxrss_kib`（本轮为 14212 KiB）用于核查；上表只使用当前地址空间的 VmHWM。
VmHWM 仍包含测试框架、线程栈、allocator 缓存和装载开销，不能解读为模块独占内存或 payload 预算。

最终原始数据：`W/logs/benchmark.jsonl`；汇总：`benchmark-summary.json`；
运行脚本：`W/run_benchmark.py`。脚本仅串行运行进程、保存 JSON 并计算通用统计，
不把 skill/PDCA 的规则写成项目专用 semantic validator。

## 证据摘要与直接复审

| W 下的事实文件 | SHA-256 |
| --- | --- |
| logs/benchmark.jsonl | `aef06d3ede53bbfb30f3be2ff0ca2c4d70e8e7bfa7d7a2ad8a23a89083031416` |
| logs/benchmark-summary.json | `d7cc08bfcd7821d1b3e412025b392125c23aff569ba539f1ac641e40f6dc8de1` |
| logs/kernel-boot.log | `a83d0f57544ef98dcc358b241145a0e12c8ec5148fe039bfe29c3af73fb1bf25` |
| logs/kernel-build-debug.log | `850a728f600c1ef1106222f86641034d3755878e2570acfd21c1d6a5b070d55a` |
| logs/rq-validation.log | `39a496da3992ae77c46c8d2faade69e9765cd65789082201c057c18cd910f8cf` |
| logs/parent-control.log、logs/parent-with-skill.log | 各 `4a5eed41b3aef7cecf85bbfffa166dff82e56149356c291c939d3a220d71cda0` |
| kernel-build/.config | `e57ebe9280a19bbe7c324adf10d665c037c34b0e4191a0f7a528717e17a42fb2` |
| kernel-build/arch/x86/boot/bzImage | `992a38d1d7aa828c0c72421820779bd83f43737c95b7354a97e2600351616579` |

Scope Review：仅新增测试资产与本报告；规则正文无改动，原 Linux 树只读，用户已有五个文件的摘要保持一致。
Consistency Review：区分业务需求、实现选择和测量指标；C++ 沿用 C ABI，无 C++ 库；案例代码与 skill 加载路径分开。
Adversarial Review：复查满额替换取舍、构造/回收窗口、借用与 destroy、辅助线程清理、超时、
opaque token 和 RSS 统计来源；删除无依据的 token 断言，修正测量口径，保留首次失败。
Evidence Review：读取源码与实际日志，重验冻结摘要、目标配置、KASAN 编译参数、KTAP、
普通/动态检测退出状态、原始基准与统计范围。有限测试不推广为全状态空间、硬件或普遍模型能力结论。

本轮不证明“完整包含所有 Linux 开发规范”，也不通过增加案例代码来扩大技能正文。
后续只有真实业务、目标版本变化或新反例表明规则有缺口时，再作最小规则修订。
