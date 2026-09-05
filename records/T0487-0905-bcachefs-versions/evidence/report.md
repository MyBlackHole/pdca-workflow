# bcachefs-tools 1.39.2 之后版本更新分析（T0487）

- 分析对象：`/home/black/Documents/bcachefs-tools`
- 范围：v1.39.2（2026-08-17）→ v1.39.3（2026-08-24，147 个提交）→ v1.39.4（2026-08-30，9 个提交）
- 事实源：`git rev-list v1.39.2..v1.39.3`（147）、`git rev-list v1.39.3..v1.39.4`（9）；重点提交经 `git show` 抽查 diff 佐证
- 复现：`git -C <repo> log --reverse --format="%h|%ad|%s" --date=short v1.39.2..v1.39.3`

---

## 一、版本总览

| 版本 | 提交数 | 时间窗口 | 主线 |
|------|--------|----------|------|
| v1.39.3 | 147 | 08-17～08-24 | mount 用户态重构（degraded/提问/udev/status_fd/recovery 显示）、离线键加固、EC/分配器修 bug、超块写优化、条带碎片化统计、自愈错误 |
| v1.39.4 | 9 | 08-29～08-30 | journal 误报修复、EC 内存泄漏、恢复路径补内容检查、内核 7.3 兼容、initramfs 超时生成器 |

---

## 二、v1.39.3 逐提交清单（147）

格式：`哈希 | 领域 | 改了什么、解决什么问题`

1. `e4c3400aa` | 内核 ioctl 文档 | 澄清子卷路径 ioctl 的相对基准（LIST 相对子卷根），无功能变更，为递归列出修 bug 铺垫
2. `d913f3e77` | Rust 构建依赖 | Cargo.lock libc 0.2.186→0.2.189，为拿命名的 stx_subvol 字段
3. `917e9ed17` | 工具 subvolume list | 递归改锚定子卷根起走，修非根发起的双倍路径与 -R 只回一层问题
4. `f4af39f9f` | 工具 subvolume list | ★ 三路遍历统一告警+跳过+非零退出，不再静默截断或直接 abort（见详解 A1）
5. `650c7fe02` | 内核 btree 打印 | val_to_text() 加截断键检查，修短键打印走飞 segfault
6. `bac41230b` | 内核 EC | 未知 csum_type 的 stripe 禁布局更新，防算错偏移
7. `acac1700f` | 内核 sb 校验打印 | disk_path_to_text 允许 fs==NULL，修离线打印 corrupt 段空解引用
8. `05e841b2a` | 内核 EC 加固 | stripe to_text/validate 先验 csum_type/granularity，防数组越界与大移位（AFL++ 发现）
9. `2ae1611d5` | 内核 extent | 新增 bch2_bkey_ptrs_safe() 给校验前调用者，防错端序+corrupt nr_blocks 越界写
10. `052359792` | 内核 backpointer 打印 | 无 fs 时打印 plain pos，防 sb 校验打印 SEGV
11. `6f1133451` | 内核 dirent 打印 | casefold 双名字越界检查，修 d_name_len=65535 堆越界读（AFL++ 发现）
12. `a6fb0b88d` | 内核分配器 RCU | ★ guard(rcu) 从函数内移到调用方持有处，并修空解引用（见详解 A2）
13. `f41f7f2df` | 内核 reconcile | 未知 csum/compression 回退 inode/fs 选项，防 BUG/越表
14. `b2dc7fdb1` | 内核数据路径 | 未知类型 WARN_ONCE+回退 crc32c/无压缩，不再崩溃
15. `bb56585c3` | 内核 closure | ★ 恢复 closure_sync() fast-path，省空等开销并修零 closure 警告（见详解 A3）
16. `8edea968b` | 工具 mount | ★ source 超 255B 回退 mount(2)，修 ~25 盘以上无法挂载（见详解 A4）
17. `9ed839038` | 内核 VFS casefold | ★ d_flags 改持 d_lock 更新，修并发 lookup 丢失唤醒致永久 D 状态（见详解 A5）
18. `b08466fb3` | 内核快照测试桩 | 新增 snapshot_delete_bail_before_inodes DEBUG 开关，用于 ktest 中断删除两阶段之间
19. `64bf68986` | 内核 errcode | 587 个 errcode 显式稳定编号，为透给 userspace 打基础，数值不变
20. `429e0b5f5` | 内核 EC stripe 复用 | ★ 只校验实际消费块，修设备移除后 stripe 卡 reconcile 无限重试（见详解 A6）
21. `f590a079a` | 内核 EC 恢复 | raid_rec() 传入含 P/Q 全擦除表，修 data+P 双坏误走 XOR 单坏路径致恢复后校验失败
22. `43cea9391` | 内核 VFS mount | 接管 source 参数并按 : 累加，多 source 可拼设备列表，打破 255B 上限
23. `f59f915fa` | 构建 | 删死变量 INITRAMFS_SCRIPT，无功能变更
24. `856a257bd` | 工具 mount | ★ fsconfig(2) 逐设备发一次 source，彻底解决 255B 天花板并保留内核日志（见详解 A4）
25. `3d668599b` | 格式/选项 | 新增 missing_dev_timeout 选项（0=内置默认），暂无消费者
26. `72e897790` | 工具 mount degraded | ★ 等成员（udev 驱动+去重）+ 应答 degraded=ask（见详解 A7）
27. `c5b58a65e` | 工具 mount 交互 | degraded 提问区分 y(只degraded)/f(very)/n 并说明代价
28. `c7645504e` | 工具 mount 重试 | ★ y 仍报缺盘时二问并一次性升级 degraded=very 重试（见详解 A7）
29. `095fa184e` | 工具 mount | -f/无挂载点不再先弹 degraded 提问
30. `550722dd4` | 工具 mount | 挂载后缺盘再扫一次在线新到成员，覆盖 prompt 窗口
31. `2e748a696` | udev | 新增规则热补迟到盘（RUN bcachefs device online）
32. `39ea36c79` | initramfs | hook 打包 udev 规则
33. `cfd4bf7ef` | 工具 mount 交互 | degraded 提示列出缺失成员详情
34. `58bea27b8` | 工具 mount 交互 | degraded 提示加 r(只读degraded)
35. `2bebe48e0` | 工具 mount 交互 | degraded 提示带 label/UUID，多文件系统可区分
36. `0449146f4` | 内核 VFS errcode | ★ bch2_fs_get_tree() 直接返回真 errcode 不再压成 EINVAL（见详解 A8）
37. `d5f44756f` | Rust errcode | ★ 未知码不再 BUG_ON 中止，适配 DKMS 新内核旧工具（见详解 A8）
38. `5eb755cf2` | 工具 mount 错误 | ★ MountError{code,text} 同时带码带文，escalate 按常量匹配（见详解 A8）
39. `c0bb6d21e` | 工具 mount 计数 | 统一用 dev_idx 集合判齐/判缺，修多路径按路径计数误判
40. `0c51160fa` | 工具 mount 提示 | 用 bch2_member_alive() 判活，不再把已 remove 槽位当 missing 报
41. `d7dfd45c3` | 工具 mount 提问 | 升级问题不再复用降级 Answer::parse()，r 不再误触发强制挂载；systemd 路径补 --echo=yes
42. `41f7d8cda` | 工具 mount 提问路由 | 新增 Prompt::detect()，有 agent 走 agent，无 agent 走终端
43. `0aeaf7e1f` | 工具 mount 提示 | fs_name() 移到 prompt 共用，两次提问指同一文件系统
44. `5849a9aed` | userspace workqueue | ★ 队列从单线程改按需增长到 max_active，手写非重入，修 async_exec 死锁（见详解 B1）
45. `8ea61487d` | 文档 | 删除指向不存在目录的 (I1) 引用，无行为变更
46. `58147326c` | async_exec 注释 | Task Sync 的 SAFETY 依据从 pending 位正名为 workqueue 非重入（见详解 B2）
47. `1846ddcf6` | 工具测试 | 新增 workqueue_test.rs 两用例，锁定阻塞不霸占队列与 poll 永不并发（见详解 B2）
48. `8324892fc` | async_exec 文档 | 注释指明测试位置（链接原因放 src/）
49. `7017decbf` | docgen 构建 | 先去 * 再去空格，修 tab 缩进 \item 致 pdflatex 失败
50. `9868bb55d` | 文档 | 补向量时钟相对标量序号的价值说明
51. `7d592294b` | 工具 shim | sched_init/kthread_start_fn 用 SYS_gettid 填 pid，诊断不再全 0
52. `2ec342ff3` | 工具 shim | 主线程 task_struct 补 thread 句柄，dump_stack 主线程从 0 帧恢复到 20 帧
53. `6fecd83ac` | 工具块层探测 | sync_check() 短读不再打印，UUID 扫描不再刷屏
54. `3f99999e9` | mount 注释 | 砍 prompt/degraded/device_scan 到只留 why，无行为变更
55. `38f213507` | mount 日志 | 无人可问的拒绝从四行 WARN 合为一个
56. `36d285daf` | mount 提问路由 | 有终端优先终端，plymouth --ping 判遮挡才走 agent
57. `772fe7d1f` | mount 提问路由 | 管道/文件 stdin 视为脚本直接拒绝
58. `7d7dc2c61` | mount 重构 | 抽 counts_as_missing() 统一缺席/移除/evacuating 判定，无行为变更
59. `bc3d1763c` | key 口令路由 | 口令提问复用 Prompt::detect()，被遮挡终端走 agent，修开机 splash 后 hang
60. `4a73aaf14` | init splitbrain | no_splitbrain_check 上提到分支头，不再构建/打印诊断
61. `a9b4dcfab` | mount splitbrain | ★ 过滤前跑发散预检并详细报告，仅 splitbrain 拒绝（见详解 B3）
62. `8091fcae9` | mount 提问类型 | Question 改泛型 Choice 数组单源，渲染/解析同源
63. `c2c4dda73` | mount 超时 | Question::timeout 改 Option，None 对应 --timeout=0 永等
64. `6098c0714` | mount 提问 | 等待改 poll+新增 Answer::Moot，提问可取消
65. `3302e5fc9` | mount udev 联动 | 降级提问带 DeviceWatch，缺席盘到达即取消提问直接正常挂载
66. `fb59b49a5` | mount splitbrain 交互 | ★ 终端问选哪边历史继续，同意顺带答 degraded（见详解 B3）
67. `9c0382578` | mount udev netlink | ★ 按 /run/udev/control 选 kernel vs udevd 组，修 initramfs 无 udevd 时等满 timeout（见详解 B3）
68. `e244b8104` | sysfs 锁 | ★ sysfs_opt_show() 全程持 sb_lock，修与 add/remove 并发 UAF（见详解 B4）
69. `b73067989` | 压缩内存 | ★ 压缩/解压 workspace 分池，修 zstd 读路径按压缩尺寸拿 buffer 致内存膨胀（见详解 B5）
70. `f267999dd` | 压缩内存 | ★ 写按本次 level 按需分配，池退为保底（见详解 B5）
71. `8f869dcf0` | mount 文案 | 无人可问拒绝首句改为具体原因
72. `7df48d38f` | wait-devices 兼容 | 命令变立即成功 no-op，文档改讲 missing_dev_timeout+降级问
73. `cd3bbab2d` | 设备上线 | ★ bch2_dev_online() 补 pre_dev_usage 初始化，修中断 add 重上线致分配器 wedged（见详解 B6）
74. `32e133ac2` | mount 日志 | “找齐设备”从 warn 降 info
75. `08a253912` | ioctl 权限 | ★ FS_USAGE 等四 ioctl 门限从 started 提前到 accounting_read，recovery 期可查用量（见详解 B7）
76. `ad58b3174` | progress 内核 | progress 从 btree 位置泛化为 count/total 计数器，为 journal replay 铺路
77. `388abe6e2` | recovery 内核 | journal replay 改用通用 progress，每阶段独立节流
78. `577591dd8` | reconcile 内核 | check_reconcile_work 的 data-btree 循环拆独立函数，避免指示器嵌套
79. `cee60f727` | 工具 | thread_with_stdio 中继从 fsck 纯搬移到 thread_with_file.rs 供 mount 复用，无行为变更
80. `6c898b9fc` | 工具 | 中继结束恢复 stdin 的 O_NONBLOCK，不泄漏标志给后续提示
81. `5d69302be` | thread_with_file 内核 | fd 创建拆出，明确先取 task 引用再 fd_install 防 close 竞争
82. `0f7a4f384` | thread_with_file 内核 | 新增无线程的 stdio_redirect，供 mount 建通道用
83. `097b7b509` | 构建 | 删从未定义的 systemd_libexecfiles 依赖，纯清理
84. `1c175584c` | systemd 启动 | ★ 新增 bcachefs-mount-generator 写 TimeoutSec=infinity，防长 recovery 每次 90s 被杀（见详解 C1）
85. `9e66f6d11` | recovery 可观测 | 各 pass progress 移到常驻存储，recovery_status 可读正在跑的 pass 进度
86. `70d40c92d` | progress ABI | units 从 const char* 改枚举+x-macro，可跨到 userspace
87. `02d8130d9` | recovery 可观测 | current_pass 赋值处打时间戳，显示当前 pass 已跑时长
88. `cec49bbe7` | recovery 安全 | ★ mid-run require 的离线 pass 不再直接进 current_passes（见详解 C2）
89. `dad028927` | 超块内核重构 | ★ 引入 CLASS(sb_write) 守卫，类型级防 ephemeral 误持久化（见详解 C3）
90. `2b6cc0268` | recovery 清理 | RUN_RECOVERY_PASS_nopersistent 改名并标注分类不一致 XXX，无行为变更
91. `c7efdb88b` | 超块内核重构 | ★ 15 处 write_sb bool idiom 转 sb_write/sb_dirty/sb_write_flush（见详解 C3）
92. `705cb0b30` | replicas bug 修 | ★ bch2_replicas_gc_reffed 从生下来就没置 write_sb，GC 瘦身只留内存（见详解 C4）
93. `c83820300` | 构建 vendor | bitfield 0.14.0 补 edition=2015，消 cargo 警告
94. `a4bfd48a7` | 兼容构建 | ★ MuQSS 无 current->se，走零 runtime 分支（见详解 C5）
95. `77e938b14` | fsck 日志路由 | 新增 bch2_print_str_user()+stdio_user_only，用户/日志分流
96. `075e09188` | VFS 挂载通道 | ★ 新增非选项 status_fd 参数，fsconfig 返回值即 fd（见详解 C6）
97. `096a3277a` | VFS ioctl | ★ status fd 透传 bch2_fs_ioctl，主供 RECOVERY_STATUS（见详解 C6）
98. `d5d2b7602` | progress 日志 | userspace 真调过 RECOVERY_STATUS 即停 dmesg 10s 重复打印
99. `2216829e3` | 工具挂载 | ★ mount 先要 status_fd 再起分离线程双向中继（见详解 C6）
100. `17a4e0191` | fs_usage 正确性 | hot-remove 后仍列出但 offline 的设备按缺失计入 degraded
101. `2d2e08622` | 工具挂载显示 | 新增 533 行 recovery_display：终端/plymouth/单行三档绘制进度
102. `a87f5262c` | 测试 | 新增 recovery_progress_delay_ms 把小 fs 拉长到可观测以测挂载显示
103. `d1f3680a2` | 缺盘语义内核 | insufficient_devices_to_start 按 replicas 表拆可读 vs 真丢数据两种 errcode
104. `ab8613d6a` | 工具缺盘问答 | degraded 提示从“选条件”改“内核已分类只选 mount/ro/不挂”，并修重扫用旧列表问题
105. `9873c5ffb` | 工具日志 | warn/error 默认输出改 mount.bcachefs: 前缀
106. `de184ebb8` | 超块显示 | 短 member 打印跳过空 Model/Serial
107. `b9f2708b7` | 工具等盘 | “found x of y”延到 2s 真停顿才 warn
108. `5f050ca52` | 工具 | 用户亲手答的不再复读，从 warn 降 info
109. `4bb25c155` | 文档 | 重写 principles-of-operation 挂载章，宣布 wait-devices 过时
110. `51abe6a4a` | VFS 安全加固 | parse_param 顶部统一校验 fs_value_type，防 filename/file 联合体越界 strlen
111. `cc3d02235` | 加密架构 | ★ 32B 密钥经 user_key fsconfig 直交内核，不再走 keyring 中转（见详解 C7）
112. `37216fa73` | 构建体验 | bindgen 缺失 panic 补二进制名+$BINDGEN 指引
113. `56c2061ce` | 工具解锁 | 新增 /run/bcachefs/unlock unix socket，远端可反复试错
114. `6b6300e68` | 加密 bug 修 | ★ 错口令不再回 0+垃圾 key，改 -ENOKEY（见详解 C8）
115. `1d4411f39` | plymouth 重构 | 协议与 active() 检测收拢到一处，无行为变化
116. `86c1c80ae` | plymouth 显示 | 超长 display-message 按字符边界截断，不再丢整行
117. `4160c2cd2` | mount 显示 | splash 增加耗时相关 splines 随机行
118. `0bafa4ce0` | plymouth 协议 | ★ 去掉每次 display-message 后误发的 PROGRESS_UNPAUSE，修进度条钉 0%（见详解 D1）
119. `b450fe4ee` | device evacuate | 输出平滑疏散速率，只统计减少量防负速率误读
120. `fffaaedd7` | 构建文档 | INSTALL.md 补 bindgen 二进制为独立构建依赖
121. `a279533ea` | nix 打包 | 设置 PKGCONFIG_GENERATORDIR，修 flake 装到只读 store 路径失败
122. `22026960f` | mount 显示 | splines 每进程洗牌、PERIOD 15s→6s，扩充词条
123. `f9adf086f` | device evacuate | 加 about 5h30m 两段式 ETA
124. `2040cb618` | 加密 bug | ★ bch2_passphrase_check() 返回值反转（见详解 D2）
125. `d5b4a05c7` | 文档 | journal rewind 上限还有 discard_buffer 储备，近满盘储备趋零属正常
126. `dbcb025be` | alloc 可观测 | discard release 计数改人类可读 GiB 显示
127. `b4769a7db` | 超块可观测 | bch2_write_super() 全程加 timestat，区分 journal 阻塞与慢 sb 写
128. `f5b0895cf` | 超块重构 | __bch2_write_super() 加 device mask 参数，全传 NULL，无行为变化
129. `b5973501e` | 超块 bug | ★ ENOMEM 路径泄漏设备引用，致 unmount 挂起（见详解 D3）
130. `9d35c9063` | 超块性能 | ★ 新增 bch2_write_super_replicas()，可跳慢盘（见详解 D4）
131. `c4e2607c2` | 超块性能 | ★ 两路热超块写改走可跳慢盘路径（见详解 D4）
132. `348ebcbdb` | 数据读安全 | ★ 解压错误不再掩盖校验错误，恢复 checksum 重试（见详解 D5）
133. `944fa7415` | 自愈 fsck | ★ journal_entries_missing 转 FSCK_AUTOFIX（见详解 D6）
134. `1e83f0c67` | 自愈 fsck | ★ 四类错误转自愈：sb_clean 不一致、stripe 计数错等（见详解 D6）
135. `21e5d29a5` | 自愈 fsck | ★ subvol_children_not_set 转自愈（见详解 D6）
136. `1139d94d0` | 数据写调试 | write op 转储打印具体桶索引，与 new_stripes 共键可关联
137. `8ca5d6212` | EC 状态机 | ★ ec_stripe_new 改显式 open/filling/in_flight 三态+富 dump（见详解 D7）
138. `a838b515b` | EC 内存 | ★ 旧 stripe 读到即折叠，halving buffer 占用（见详解 D8）
139. `88209f67b` | EC 日志降噪 | ★ 仅离线设备致失败的 stripe 读静默（见详解 D9）
140. `a088d5bca` | 写路径降噪 | ★ 仅设备移除致降级的写静默（见详解 D9）
141. `375dcc747` | EC 会计 | ★ stripe 空块碎片化双维会计（见详解 D10）
142. `7327ecd3a` | EC 兼容性 | ★ 新增 BCH_COMPAT_stripe_frag_accounting(5) 兼容位（见详解 D10）
143. `14ee91167` | EC 会计 | ★ 按设备聚合条带碎片化（见详解 D10）
144. `44870e781` | Rust 绑定 | codegen 暴露 BCH_SB_COMPAT 供查询 stripe_frag_accounting
145. `4a3417bef` | fs usage 显示 | ★ stripe 行旁加 empty 列（见详解 D10）
146. `e8a9917e1` | 打包 | deb/rpm 补 systemd-mount-generator，修 dh_missing 构建失败
147. `9cc4c7808` | 版本号 | 1.39.3，无功能变更

---

## 三、v1.39.3 重点提交详解

### A1 `f4af39f9f` 递归子卷列出：静默截断 vs 直接 abort
根因：三路遍历对不可打开子目录处理不一致（文本路丢错继续，--json/--tree 直接上抛）。触发：非特权列出含他人目录的树（实测 187 只印 146 却 exit 0）。影响：备份脚本误以为全量。修后 stdout 纯结果、stderr 告警去重、非零退出可区分部分列出。

### A2 `a6fb0b88d` RCU：返回即释放的 mask
根因：guard(rcu) 写在 bch2_target_to_mask() 内部，返回时已释放而返回值指向 RCU 对象；并发 label 变更即 UAF，另有拔盘后空解引用。修后调用方持锁读取，PROVE_RCU 遗忘持锁会告警。

### A3 `bb56585c3` closure_sync fast-path
根因：调试注释掉 remaining>1 检查后半年全量走慢路径。影响：每次空等多一次 sleeper 写+原子操作；零初始化 closure 误减触发 guard 警告。单行恢复，两端皆修。

### A4 `8edea968b`/`856a257bd`/`43cea9391` mount fsconfig 255B 天花板
根因：fsconfig(2) 经 strndup_user(_,256)，超 255B 直接 EINVAL 且无内核日志；切 fs_context 后 ~25 短路径盘即超限（65 盘 633B，feedc0de 报告）。先回退 mount(2) 保挂载，再由内核累加 source + userspace 逐设备发送彻底解决，仅单路径超长才回退。

### A5 `9ed839038` casefold d_lock 丢失唤醒
根因：无锁读改写 d_flags 与 d_alloc_parallel 并发置 LOOKUP_WAITERS 竞争，旧值回存擦掉等待位致永久 D 状态挂起（两次现网复现，不可杀至重启）。修后统一持 d_lock 并加 lockdep 断言。

### A6 `429e0b5f5` EC stripe 复用卡死
根因：复用 stripe 时全量校验含刚置废的块，必败回 LRU 且越空越早被再选（11+2 stripe 两坏块无活数据即永久滞留 reconcile，空间不回收+日志刷屏）。修后仅“坏皆在丢弃集”不再判失败，仍全量读/全量参与重构。

### A7 `72e897790`/`c7645504e` degraded 挂载
等成员（udev 驱动+去重，修零设备空集立即成功）+ 应答 degraded=ask；y 仍缺盘时二问并一次性升级 degraded=very 重试。无终端/超时一律拒绝，不静默降级。

### A8 `0449146f4`/`d5f44756f`/`5eb755cf2` errcode 链
先稳定编号（587 项，值不变），再内核透传真 errcode（不再压 EINVAL）、工具带码带文按常量匹配、未知码不中止。degraded/splitbrain 判断从不可靠变可靠。

### B1 `5849a9aed` workqueue max_active
单线程队列遇“task 等 task”即死锁；改按需增长到 max_active 并手写非重入（防 btree 更新双执行致二次 free 堆损坏）。fsck 全绿验证。

### B2 `58147326c`/`1846ddcf6` async_exec 契约正名+测试
pending 位只负责 wake 去重，真正互斥是 workqueue 非重入；新增双测试锁定，跨语言契约可回归。

### B3 `a9b4dcfab`/`fb59b49a5`/`9c0382578` splitbrain 与 netlink
旧流程丢发散 sb 后误问降级，答 yes 即静默选一边丢数据；修后分层问“选哪边历史”，证据放 detail，破坏性重写不提供。等盘 monitor 错订 udevd 组致 initramfs 永不响；改按 /run/udev/control 选源。

### B4 `e244b8104` sysfs sb_lock UAF
opt show 裸读 disk_sb，与 add/remove 并发即 UAF；全程持锁，低风险。

### B5 `b73067989`/`f267999dd` 压缩 workspace
读按压缩尺寸拿 buffer（zstd 8G→12G，ChrisHowie 报告）；写按最坏 level 拿（lz4 16 倍、zstd 一律 22 级）。分池+按需分配，池退保底。

### B6 `cd3bbab2d` 中断的设备添加致分配器 wedged
bch2_dev_online() 漏 pre_dev_usage 初始化，free 绕回 2^64，健康盘闲置、journal_full 连锁全堵。修后幂等。

### B7 `08a253912` usage ioctl 门限提前
四 ioctl 从 started 改 accounting_read_done()，recovery 长窗口可查用量；读自持 mark_lock，早调只得零表。

### C1 `1c175584c` systemd generator 防 90s 误杀
.mount 单元 DefaultTimeoutStartSec=90s，超长 recovery 每次开机同点被杀无限循环。generator 按 fstab 写 TimeoutSec=infinity drop-in，x-systemd.mount-timeout 仍优先。

### C2 `cec49bbe7` recovery pass 上下文逃逸
mid-run require 的离线 pass 直接进 current_passes，在线 fsck 可写活数据。修后只调度到下次挂载。

### C3 `dad028927`/`c7efdb88b` sb_write 守卫
9 文件手写 bool write_sb 易忘写/早返漏写/ephemeral 误持久；类型化守卫统一 15 处，唯一行为变更是 mi_field_upgrades 改每脏盘即写。

### C4 `705cb0b30` replicas GC 从不写超块
出生即死代码（write_sb 永 false），GC 瘦身只留内存，盘上仍称有而已无的 journal，can_read 永拒；只读/安静挂载可爆出。

### C5 `a4bfd48a7` MuQSS 构建修
无 current->se，走零 runtime 分支，仅统计列。

### C6 `075e09188`/`096a3277a`/`2216829e3` status_fd 挂载通道
fsconfig(CREATE) 阻塞整个 recovery 却最黑盒；新增非选项 status_fd（fd 号即返回值，stock 内核可用）+ RECOVERY_STATUS ioctl（128bit pass 掩码）+ userspace 分离线程双向中继 + 三档进度绘制 + 已读即停 dmesg。

### C7 `cc3d02235` 加密密钥直传
32B 先放 keyring 再按名要回属多余；改 user_key=64hex fsconfig 直交，双出口 memzero，错 key 不残留。

### C8 `6b6300e68` 错口令不再算成功
回退提示后恒 ret=0，错口令给垃圾派生 key，症状后移为 checksum 错；改 -ENOKEY 并清零释放。

### D1 `0bafa4ce0` plymouth 误发 UNPAUSE
每次 display-message 后误发 PROGRESS_UNPAUSE，进度条钉 0% 并污染 boot-duration 缓存。

### D2 `2040cb618` passphrase 检查反转
sb_key 已原地解密，正确口令使 is_encrypted==false，原直接返回谓词即反转；mount/unlock 双重反转抵消而隐藏，show-super 正确口令反报错。两处同改。

### D3 `b5973501e` 超块写 ENOMEM 泄漏设备引用
for_each_online_member 跨循环持有 io_ref，中途 return 泄漏，设备永不释放致 unmount 挂起。单行 kfree/put。

### D4 `9d35c9063`/`c4e2607c2` 超块写跳慢盘
journal 漫游致 replicas 新表项不断触发全舰队超块写，被最慢盘卡住。新增 device mask + BCH_SB_SKIP_META_PCT=10：仅 btree 计量、仅转盘可丢、全 SSD 不丢、总量零则全写；65 盘例从 65 盘屏障降为 27 盘。

### D5 `348ebcbdb` 解压错不掩盖校验错
损坏压缩 extent 先校验错后解压大概率也错，原优先报 decompression；掩盖后无 checksum 重试（3 次）直变硬读错，还永久标记坏 extent。修后仅校验好时解压错才有意义。

### D6 `944fa7415`/`1e83f0c67`/`21e5d29a5` 自愈错误
journal_entries_missing（GH#1203 卡一周，继续是唯一出路）、sb_clean 不一致（丢弃回权威 journal）、stripe 计数错（按 gc 数重组）、subvol_children_not_set（同键补索引）转 FSCK_AUTOFIX，减少 mount 人工卡死。

### D7 `8ca5d6212` ec_stripe_new 显式三态
pending bool 改 open/filling/in_flight，富 dump（state/pin/used/age），内存等待可避死锁。

### D8 `a838b515b` 旧 stripe 读到即折叠
复用同时持新旧等大 buffer 从 head_get 到 create；改读到即 fold，halving ec_stripe_buf_limit 占用。

### D9 `88209f67b`/`a088d5bca` 离线/移除误报降噪
成功降级读/写不再刷屏（保 burst 预算给真错），失败或他因仍报。

### D10 `375dcc747`/`7327ecd3a`/`14ee91167`/`4a3417bef` 条带碎片化统计
空 stripe 块为可复用容量但 fragmented 按整桶计无法区分；加双维会计 + compat 位(5)门控 + fs usage empty 列，纯 informational。

---

## 四、v1.39.3 主题归纳（解决了哪几类问题）

1. 多设备挂载全链（约半数）：255B 天花板→等盘→degraded 分级问→二次升级→热补→计数去重→udev/initramfs 打包
2. 离线/AFL 加固批：打印与校验跑在未校验键上，统一先界后读
3. 并发与死锁：RCU UAF、丢失唤醒、closure fast-path、workqueue 多工作者
4. 数据正确性：EC 复用卡死、P/Q 漏报、未知类型不崩、解压/校验错优先级
5. 挂载可观测：status_fd 通道 + recovery 进度 + 三档绘制 + systemd 防杀
6. 超块持久化：sb_write 类型化守卫 + replicas GC 落盘 + 跳慢盘 + 自愈错误
7. 加密：密钥直传、错口令 -ENOKEY、passphrase 反转修复、unlock socket
8. EC 可观测：三态、富 dump、旧 stripe 折叠、碎片化统计、日志降噪
9. 构建打包：MuQSS、bitfield、bindgen、nix、deb/rpm generator

---

## 五、v1.39.4 逐提交清单（9）

1. `caeed4b3d` | journal | ★ flush_seq stuck 超时从 2x 改 5x 设备延迟，修慢盘误报 stuck（见详解 E1）
2. `19e26cc55` | 内核兼容 | kernel 7.3：bi_bvec_done 改名 bi_offset（Malte Schröder）
3. `94e87324c` | 内核兼容 | kernel 7.3：->create 去 excl 参数（Malte Schröder）
4. `c13428e1a` | alloc 诊断 | ★ “bucket going empty”消息反了，修后并补旧键打印（见详解 E2）
5. `a62ac65c1` | EC 内存泄漏 | ★ stripe_new_alloc 错误路径漏 kfree(new_s)（见详解 E3）
6. `8a13c58ce` | recovery 修补 | ★ 内容 btree 丢数据时补排内容检查，防悬空引用延迟爆发（见详解 E4）
7. `30197b8e8` | alloc 诊断 | bucket 非空转换打印旧键+调用方，修只印终态无法定位
8. `5b177434f` | initramfs | ★ mount 超时 generator 装进 initrd，修 bcachefs 根 90s 被杀循环（见详解 E5，Chris Howie 报告）
9. `d997ad76e` | 版本号 | v1.39.4，无功能变更

---

## 六、v1.39.4 重点提交详解

### E1 `caeed4b3d` journal flush_seq 误报 stuck
根因：与 res_get 共用 max(2x 最坏写延迟, 10s)，但 flushing commit 是 preflush×N + journal 写 + 等待串行，最坏单盘延迟只是下限而非总量。现网慢盘阵列刷屏 stuck。改 5x 并删“两处一致”注释。

### E2 `c13428e1a` 反转的 bucket 消息
检查谓词是 empty→nonempty（无分配即变用），消息却写反；连 errcode 名都反了（为兼容报告保留）。一次现网排查因此看错一半分配器（reddit 报告）。E4 同人报告，同属“诊断误导”类修复；`30197b8e8` 配套补旧键与调用方。

### E3 `a62ac65c1` ec_stripe_new 泄漏
buf_init/stripe_idx_alloc 错误路径释 handle、释双 buffer，漏 kfree(new_s)；同函数另两路都释。审计旧 stripe 钉住窗口时发现。单行修复。

### E4 `8a13c58ce` 恢复补内容检查（本版最重要）
bch2_btree_lost_data() 只给 alloc 系与 snapshots 排修复 pass；extents/inodes/dirents/xattrs/reflink/subvolumes 等全部走 default，只修树形不重验引用，留下悬空引用延迟爆发（现网：SATA 线致 dirents 丢，三周后 lookup 踩到指向不存在 inode 的 dirent 才首次调度 check_dirents）。修后 60 行补全内容检查调度；check_alloc_info 故意不加（check_allocations 已无条件跑）。

### E5 `5b177434f` initramfs 装超时生成器
v1.39.3 的 generator 只装进真根；bcachefs 作根时挂载跑在 initramfs 的 systemd 下仍是 90s 默认，超长恢复被杀则下次开机重来。改 symlink 随 hook 进 initrd（argv[0] 分发，hook 已拷二进制）。

---

## 七、 Convenience：机检复现命令

```bash
git -C /home/black/Documents/bcachefs-tools rev-list --count v1.39.2..v1.39.3  # 147
git -C /home/black/Documents/bcachefs-tools rev-list --count v1.39.3..v1.39.4  # 9
git -C /home/black/Documents/bcachefs-tools log --reverse --format="%h|%ad|%s" --date=short v1.39.2..v1.39.3
git -C /home/black/Documents/bcachefs-tools log --reverse --format="%h|%ad|%s" --date=short v1.39.3..v1.39.4
```
