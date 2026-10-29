# Linux 开发经验提炼与完整目标复核（3.3.0）

日期：2026-10-29。基线：`3a794adce42bb5ba6f44a06dfd64a61c1e94733c`（3.2.0）。对象：[systems-programming](../../skills/systems-programming/SKILL.md)。

## Scope Review

目标是将 Linux 官方规范与用户指定的 `/home/black/Documents/linux-7.3` 实现共同归纳为未来内核态、用户态开发的工程方法。上一轮已全文核对树内 coding-style 的 22 章，逐章观察、资源实现比对与 23 个文件标识见 [7.3 比对报告](2026-10-29-linux-7.3-code-comparison.md)；已修正的规范缺口和贡献政策见 [3.2 审查](2026-10-29-linux-coverage-repair.md)。

本轮围绕容器、等待、文件映射与设备排序补强开发经验，修改七份已有技能文件，新增一份数据结构与接口资料。references 仍只有 principles、workflows、environments、sources 四类，不新增独立工程 skill 或嵌套索引。运行时 skill 不依赖本报告或本机 Linux 路径。

本地 Makefile 仍标识 7.3.0，根无 .git；远端、提交及与官方发布树的差异为 unknown。没有以目录名称认定“最新主线”，没有改动该源码树。本轮从封闭的 25 个路径取得 24 个存在文件的内容标识；语义阅读仅为下表所列相关路径，不等于全文审查 24 份文件。预选的 `Documentation/locking/completion.rst` 不存在，未递归查找替代文件；completion 结论用官方在线文档及明确的头文件/实现核对。

## Consistency Review

### 官方要求、实际路径与两种环境的迁移

| 解决的问题与官方依据 | 本地实际路径及观察 | 归纳与采用限制 |
| --- | --- | --- |
| 容器选择与安全遍历：[list](https://docs.kernel.org/core-api/list.html) | `Documentation/core-api/list.rst:320–363,753–775`、`include/linux/list.h:909–929,975–989`；safe 缓存下一项，锁释放及并发删除另有约束 | 按访问模式比较连续存储、链表和索引；safe 不是并发或生命周期保证。用户态用项目 C 抽象重新证明 |
| 索引与对象引用：[XArray](https://docs.kernel.org/core-api/xarray.html) | `Documentation/core-api/xarray.rst:185–247`；`lib/xarray.c:1600–1638` 的 xa_load 在返回前结束内部读侧保护 | 索引内部保护不替调用者取得对象使用权。查找、取引用与删除形成完整协议；ID/fd/槽位复用另有身份问题 |
| completion 与等待：[Completions](https://docs.kernel.org/scheduler/completion.html)、[Driver basics](https://docs.kernel.org/driver-api/basics.html) | `include/linux/completion.h:60–102`、`kernel/sched/completion.c:1–85,155–176,330–363`；`include/linux/wait.h:96–127,300–363` | 超时不是生产者取消；重新初始化不是收敛上一轮参与者；done 不是所有等待者已退出的证明。用户态条件等待也围绕同步谓词、停止与存活协议 |
| per-CPU 与迁移：[this_cpu](https://docs.kernel.org/core-api/this_cpu_ops.html) | `Documentation/core-api/this_cpu_ops.rst:124–157,281–318` 区分指针、单次操作及远端访问 | 旧 CPU 地址未必立即失效，但不能继续按当前 CPU 独占使用。迁移约束、互斥及复合状态不能互相替代 |
| timer/work 重新生产：[Driver basics](https://docs.kernel.org/driver-api/basics.html) | `kernel/time/timer.c:1630–1721`；delete_sync 的禁止重启前提与 shutdown_sync 的最终禁入语义不同 | 按目标版本和回调上下文停止全部生产来源，再等待与回收；用户态 timer/线程机制按实际接口采用 |
| poll 登记、read 与非阻塞：[VFS](https://docs.kernel.org/filesystems/vfs.html) | `include/linux/poll.h:34–69` 的 qproc；`fs/select.c:158–177,219–237` 的回调可使用 GFP_KERNEL；`drivers/uio/uio.c:543–634` 先登记再检查并处理 O_NONBLOCK | 登记后按同步协议读 readiness，不丢就绪变化；登记过程可能分配/睡眠。用户态事件循环继续按自身 epoll/poll 及 fd 契约处理 |
| fd、file、VMA 与设备：[VFS](https://docs.kernel.org/filesystems/vfs.html)、[mmap(2)](https://man7.org/linux/man-pages/man2/mmap.2.html) | `Documentation/filesystems/vfs.rst:1080–1110,1160–1185`；`drivers/uio/uio.c:672–759,820–895` 的映射、fault 与设备有效性检查 | close(fd)、flush、最终 release 和解绑分开；正常 vm_file 引用可维持 file，不能见 close 就判 UAF。初始/后续 VMA 计数、页和设备存活分别核对；采用目标 mmap_prepare/mmap 入口 |
| 错误编码与缓冲：[Kernel API](https://docs.kernel.org/core-api/kernel-api.html)、[snprintf(3)](https://man7.org/linux/man-pages/man3/snprintf.3.html) | `include/linux/err.h:20–96`、`include/linux/string.h:70–111`、`lib/string.c:96–173` | NULL、错误指针、可选缺省逐 API 区分；strscpy 保留有符号错误，snprintf 所需长度不当实际写入量。用户态核对 libc/项目 API，二进制采用显式长度 |
| CPU、DMA 与 MMIO 顺序：[DMA guide](https://docs.kernel.org/core-api/dma-api-howto.html)、[Device I/O](https://docs.kernel.org/driver-api/device-io.html) | `Documentation/core-api/dma-api-howto.rst:347–394,423–466`、`Documentation/driver-api/device-io.rst:58–106`；`drivers/net/ethernet/intel/igb/igb_main.c:4294–4324,6348–6386` 分开 CPU 地址、DMA handle、dma_wmb 与门铃 | coherent 不包办顺序；posted write 到达、设备停止和软件互斥是不同保证。匹配 coherent free 或 streaming unmap，释放前收敛真实访问；不靠纯软件案例证明硬件行为 |

直接追踪 select 调用链后，修正了草稿中“poll_wait 本身不睡眠”的过度概括。该说法未作为最终规则保留。规范目的、目标实现和反例共同约束结论，不能因为名字含 safe/coherent/complete 就扩大保证。

### 唯一规则维护位置

- [数据结构与接口](../../skills/systems-programming/references/principles/data-and-interfaces.md)：结构选择、容器/身份、表示/缓冲和回调边界；详细预算/存活/锁外提交继续引用原有 [内存与锁](../../skills/systems-programming/references/principles/memory-and-locks.md)。
- [内核环境](../../skills/systems-programming/references/environments/kernelspace.md)：错误结果、等待/per-CPU/停止、poll/mmap、DMA 的环境/API 限制。
- [用户态](../../skills/systems-programming/references/environments/userspace.md)：mmap 返回值、所有权和 fd/映射分离；未复制内核私有 API。
- [改动验证](../../skills/systems-programming/references/workflows/validation.md)：相关交错、正常用法对照及真实 VFS/设备证据的适用性。详细测试设计仍归测试策略。
- [官方映射](../../skills/systems-programming/references/sources/official-docs.md)：主题、唯一位置与触发读取责任。既有 60 个来源 URL 全部保留，新增九个；数量不作为规范通过率。

19 份技能资料的长段落精确重复检查没有命中；它仅说明文字相等情况。直接审读的职责边界及独立审查未发现需要合并的重复详细规则。

## Adversarial Review

### 只读场景的基线与复测

修订前，独立 fresh-context 基线已能凭一般知识正确回答九题，并指出技能缺少明确规则。没有把这些正确答案改记为失败，也不能据此宣称本轮产生了可测的模型能力提升。

修订后由 `linux_coverage_retest` 在 fresh context 中重新读取允许的技能资料；未传入预期答案、基线结论或作者说明。实际读取 11 个明确技能文件，未读取外部源码或运行产品测试。

| 场景 | 观察到的复测判断 |
| --- | --- |
| safe 遍历与锁外回调 | safe 不防其他执行者删除；回调上下文和函数表也需要有效期 |
| completion 超时/复用 | 等待返回不证明异步生产者结束；上一轮参与者未收敛不能复用 |
| poll/O_NONBLOCK/mmap | 登记可能分配/睡眠；没有进度时遵守非阻塞契约；正常 file/VMA 引用作为避免 UAF 误报的对照 |
| XArray 查找和旧 ID | 内部 RCU 不等于返回后引用；身份/代际必须随实际请求传播，不能只给新对象加字段 |
| devm/错误指针与字符串 | 未知具体函数时不能断言 NULL 检查必错；区分编码、符号、所需长度与实际数据 |
| timer/work 相互 rearm | 先覆盖生产来源及回调上下文，不能仅同步删除后释放 |
| per-CPU 多步操作 | 地址可能仍有效，但 CPU 归属/独占依据已变；固定迁移不等于互斥 |
| coherent DMA 与 doorbell | 分开设备可见性、排序、总线到达与硬件完成 |
| 向用户态迁移与低风险对照 | 采用 C/pthread 等许可接口，不引入 C++ 库；README 小改不触发内核全量流程 |

`linux_coverage_repair_review` 以只读第二视角审查本轮差异、新资料及相关源码路径；最终对完整用户目标复核 19 份资料后，未发现必须继续追加的核心规则缺口或明确诱导错误设计。其结论包括共同原则、任务方法和环境限制分工明确，具体子系统/硬件/版本仍需触题核对。该审查没有重演行为场景，也没有认证尚未收到的实现案例。

### 真实实现验收

隔离项目：`/home/black/skill-work/validation/engineering-consolidation/linux-experience-forward-20261029-r1`。固定 `rq.h` 和 README 公共契约，由 fresh-context 实现 Agent 读取技能后实现 C/pthread 单消费者消息队列；父 Agent 独立拥有 `test_parent.c`，实现者不得修改它。实现不进入 PDCA 产品或 Linux 树。

实际方案使用一把 mutex 保护队列及统计，分配前预留条数/负载预算，锁外单块分配、复制、回调与释放，锁内重新检查准入后提交；消息实际释放后才退账。关闭阻止准入并等待包含构造/在途阶段的 live 归零；最终独占 destroy 再 join 线程。没有为这一契约引入共享引用框架、无锁结构、池或 C++ 库。

父 Agent 已直接审读 `rq.c`、公开头/契约、Makefile、测试及系统边界故障注入代码。所有权及停止证明保留“destroy 前其他公开 API 已退出”的前提，不能推广为支持任意使用已销毁句柄。

实现者实际执行 `make check >build/logs/normal-check.log 2>&1`，退出 0。父级已读取该日志及测试源，观察到：

```text
PASS all 11 C scenarios; tracked allocations=0, unjoined threads=0
PASS C++ caller: C ABI, binary copy, close, stats
```

11 项涵盖创建/分配失败回滚、溢出和零长度、FIFO 与输入复制、在途条数/字节上限、回调重入、自身关闭、分配前/后暂停与并发关闭、实际 free 前预算不提前退还、四生产者排空/关闭竞争及 destroy 排空。故障注入包装真实 malloc/free/pthread 边界，不直接操作队列私有字段；未注入时调用真实系统实现。资源记账覆盖显式取得的模块分配与线程，不等于全进程内存诊断。

实现者的 strace 附加审计因沙箱 ptrace 限制退出 1，未取得有效 trace；后续沙箱外申请由父级收尾中止，没有成功执行结果。ASan/UBSan/LSan/TSan 未运行，不将该审计或 sanitizer 计为通过。工具输出路径预检、工作区 TMPDIR/TMP/TEMP、-save-temps=obj、显式输出及禁止 core 的设置另见隔离项目 `EVIDENCE.md`，不把参数预检说成完整写入路径审计。

父级独立检查实际编译并运行：

```text
gcc -std=c11 -O2 -g -Wall -Wextra -Werror -Wpedantic -pthread -save-temps=obj rq.c test_parent.c -o parent-check/test_parent
timeout 30s ./parent-check/test_parent
parent public-API checks: passed
```

两条命令均退出 0；运行时明确将 TMPDIR/TMP/TEMP 设为项目 `parent-check/tmp`，完整命令见工作区 `parent-check/EVIDENCE.md`。独立断言覆盖在途预算、回调重入、自身 close、双线程 close、四生产者/关闭交错、逐 ID 成功与交付对应、重复停止和最终归零。父级另执行 readelf，C++ 调用产物仅有 `libc.so.6` 一项 NEEDED。

`rq.c` SHA-256：`d7563fe1fcbe2c96df64ba02c04e28bc712dab6e076967ab2387f9d3635e97c0`；父级 `test_parent.c`：`0533bcb140e5aea178277c9bf1295b960fc746987daeb5f586c49b3bcfe7254b`。该案例是有明确行为契约的前向使用验收，不是无技能/有技能的因果实验，也不支持性能改进声明。

## Evidence Review

- 技能 quick_validate 实际返回 `Skill is valid!`。
- 技能与本报告的 176 个本地 Markdown 链接/锚点核对无错误；工程索引及两份前轮报告作为明确目标读取。
- 八份技能文件与本报告共九份，精确名称与本轮允许列表一致，工作区与暂存内容一致；暂存 diff 空白检查退出 0。报告首次纳入时发现的末尾空行已修正，检查包含两份新增文件，未仅凭普通 diff 宣称覆盖。
- 受保护的 `AGENTS.md`、`README.md`、`INSTALL.md`、`skills/README.md`、`skills/catalog.json` 与本轮开始时 SHA-256 一致；不收集其暂存内容。
- 24 个本轮源码文件在最终核对时 SHA-256 均未变化；源码阅读和只读场景属于静态证据，真实 C 队列编译/运行另列其命令与限制，没有将几种证据互相替代。

## 完整用户目标复核

| 用户要求 | 最终落点与证据 |
| --- | --- |
| 在指定位置提供统一 skill，名称 systems-programming | `skills/systems-programming/SKILL.md`；版本 3.3.0，单一按任务读取入口 |
| 汇入本包软件工程方法，移除旧入口 | [迁移索引](../engineering/INDEX.md) 对应安全、调试、测试/TDD、审查、构建、注释、项目及提交约定；本轮精确检查已知 11 个旧 SKILL.md 均不存在，未递归盘点或卸载宿主插件 |
| C 为主，C 风格 C++ 不使用 C++ 库，兼顾 Rust | 入口和两种环境资料保持语言边界；C++ 调用实际以 g++ 编译、gcc 链接，动态依赖未出现 C++ 库；不将 C++ 推广为内核实现语言 |
| 未来开发主动设计内存与锁 | 入口主动资源设计及内存/锁的唯一详细规则；只读设计场景与真实队列实现均包含完整预算、存活、锁外复核和退出 |
| 官方编码规范与指定本地实现比对 | 前轮 22 章全文与逐章表，本轮专项声明/实现/调用者链；区分规范、实际条件、局部历史写法和两种环境的迁移 |
| references 清晰、避免规则重复 | 四类保持不变；详细规则有唯一 owner，入口/环境/方法按条件引用；精确重复检查及直接语义审读 |
| 自我审查并验证 AI 使用效果 | 修订前正确基线如实保留，九题复测、正常用法对照、只读独立完整目标审查，以及真实实现与父级独立测试；不将其写成因果或普遍能力保证 |
| 提交 PDCA、保留用户修改及禁用 /tmp 测试产物 | 本轮仅选择八份技能文件与本报告；保护五份既有文件的内容；测试和诊断目录固定在工作区，不自动启动 PDCA 生命周期或推送 |

最终复核支持其作为未来内核态/用户态开发的工程入口。这里的完整性是本次统一规范、可执行设计决策和专项读取责任的完整闭环；不将所有 Linux 子系统、架构、硬件和未来版本的文档复制进 skill。触及具体接口时仍须按目标树、声明、调用者与配置取得证据；这项责任已写入技能。

没有修改或构建目标 Linux，没有取得硬件 DMA、真实驱动 VFS、内核配置矩阵、掉电恢复或性能基准结果。用户态队列案例只能证明该受控契约在实际场景中的表现，不能据此认证所有未来代码或声称已经测得加速。

## 本轮源码内容标识

这些哈希固定已取得的整文件内容，不表示全文语义审查；实际阅读范围以比对表为准。来源认证仍为 unknown。

| 相对源码根的路径 | SHA-256 |
| --- | --- |
| `Makefile` | `2eb7b5d5c2ac15a28136607e086f82ebd13f0d3753acc89e463fed49109bc794` |
| `Documentation/core-api/list.rst` | `a63136d038454d599c81b8fb119be25fba78b3d2af9eded43d7bec6a56e02d61` |
| `Documentation/core-api/xarray.rst` | `c8b903861e456d2414c68328c8ed7add726798aa12849681305ff43c131a2ba0` |
| `Documentation/core-api/dma-api-howto.rst` | `92070ca3b5e150580c26d39be990b109053951a767fb3fd1d695aece478bbff2` |
| `Documentation/driver-api/device-io.rst` | `852aa412631b7f2e1e6c16c992c5c31569f8c20ea7dd8d465d5faa992571d50a` |
| `Documentation/filesystems/vfs.rst` | `89136bc040715b64f71fb7a00b2071c3a376785d944c0bbc30b42023d9dca8e3` |
| `Documentation/core-api/this_cpu_ops.rst` | `0472e7527b41a4f8e0670c6bf6a86fccbef699841c2adde18a1a87b6a2147ef3` |
| `include/linux/list.h` | `1b44c1ce3ba165b1ea722de9b1353324c1795d76757b8038ca6b4b8cb85c97c9` |
| `include/linux/completion.h` | `db5aac6634fbb92542486d273d93861dfd29061043d461ae494cfa2b2e9f4e4b` |
| `kernel/sched/completion.c` | `79f10c4e41095aa647591de8edec1ed037fff51737d2b1082e8b88ebbdedcfbe` |
| `include/linux/wait.h` | `f9f53a02fd25a1a1fefdc41310285975d5c1fdce1a1b62282cc05e737ae96417` |
| `include/linux/poll.h` | `2e9d66ec3a6ae91ae35d1e2065e90f42116e48081c68456da56594656b6022eb` |
| `fs/select.c` | `eaaf171b3549ca4df9a270b3cf2b09e295439ffb15dee77250d14f3a52ee5a95` |
| `drivers/uio/uio.c` | `830c65f332d1a994a86401b104b75506b1fb752ef3e66a76e89fc6a382838c71` |
| `include/linux/err.h` | `e7fab3f021ae4d0c5f7e34497eca5cd3473cca904cb59a853b015720a74b04e9` |
| `include/linux/string.h` | `4dbc380b35f81d4e3992abae48fbb23b4f392fd28f633d0d96114be166d5dfd5` |
| `lib/string_helpers.c` | `674e41d0f69f197783bc6970fd887a52e2cd92ff7956ac6b2d0bb700c2969535` |
| `lib/string.c` | `708fd782a7c09e0b04b2eafa87007004ffb81283e0ac37941f59738a9288f497` |
| `include/linux/percpu.h` | `13c146fd57546e47ab465849cd671ba930ffab739b4e2568fed6ddc3247a67e9` |
| `kernel/time/timer.c` | `6695f63fe4a4f58e1d7297ee106b68434aa842598dc055aae1a5572f98ce3fe8` |
| `include/linux/timer.h` | `8841dfffe707b32e3a2f8f34b4a4797754a299ba23f8d60c4c7b56e8995f6376` |
| `lib/xarray.c` | `b2d275008a1f24090b9c6a3019faad73ac21c326e080c4488e89f13bd575da61` |
| `include/linux/xarray.h` | `be3707d0f78bbf6ddf64ac16885f0ed4c6ccd083cc3d8197e92f3a9ad2c03dd4` |
| `drivers/net/ethernet/intel/igb/igb_main.c` | `b8833f12c4cd1d4059170a36621c938bb826a14a9faa50f432a778b7e833b7ea` |
