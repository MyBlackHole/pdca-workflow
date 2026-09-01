# T0488 潜问题调研清单（项目 139，排除 third_party/openssl，T0463 已修复项仅引用）

> 范围：fs-backup/fsdeamon/*.cpp, rpc/*.cpp, libs/rdb-config*, rdb-cfg/*, dmsbtex/*, libobk/* 全量热点扫描；按 code-review-checklist 6 维度抽样，至少 4 维度各有实例；每条含 文件:行号、严重度、类别、证据。

## 严重度摘要

| 严重度 | 数量 | 编号 |
|--------|------|------|
| CRITICAL | 2 | C-01, C-02 |
| HIGH | 4 | H-01 ~ H-04 |
| MEDIUM | 8 | M-01 ~ M-08 |
| LOW | 3 | L-01 ~ L-03 |
| 合计 | 17 | 覆盖 6 维度 |

维度覆盖：正确性(5) / 安全性(4) / 性能(2) / 可维护性(2) / 错误处理(3) / 测试(1)

---

## CRITICAL

### C-01 安全性-命令注入：rpc 服务端无鉴权执行任意 shell（高危攻击面）
- **文件:** `rpc/rpc-server.cpp:854-1063`（`execute_cmd`）、`rpc/rpc-server.cpp:2600-2627`（`nc_extend`→`popen`）、`rpc/rpc-client.cpp:965-2766`（客户端 `snprintf(host->command)` 直送）
- **类别:** 安全性
- **证据:**
  ```cpp
  // rpc/rpc-server.cpp:878-885
  msg_cmd_ntoh(cmd_host, cmd_net);
  cmd_len = MIN(cmd_host->cmd_len, MSG_BUFF_LEN - 1);
  command[cmd_len] = 0x00;
  fptr_pipe = my_popen(command, "r", &chpid); // -> execl(SH, "sh","-c",command)

  // rpc/rpc-server.cpp:2626-2627
  snprintf(command, sizeof(command), "%s", host->data);
  fptr = popen(command, "w"); // nc_expand 亦同
  ```
  `timed_key_verify` 仅在 `MT_KEY_VERIFY` 分支校验（`rpc-server.cpp:520`），而 `MT_EXECUTE_SHELL_SCRIPT` / `MT_EXECUTE_NC_EXTEND` 分支 **不检查** `timed_key` / `auth_enabled`，且 `execute_cmd` 受 `SH -c` 解释，`--nc "lz4 -d | sh"` 等管道可直达。任何能完成 TCP+握手（明文模式 `mtls_enabled=0` 即无证书）的对端即可 `aio-speed -h ip -p 6611 -c "任意命令"`。
- **影响:** 需配合网络隔离；否则等价远程代码执行。
- **建议:** 在 `StartRPCServiceWoker` 的 `MT_EXECUTE_SHELL_SCRIPT`/`MT_EXECUTE_NC_EXTEND` 入口前置 `auth_enabled` 校验；或将白名单命令与 `allow_list` 绑定，拒绝含 `;|&$()` 的输入；审计日志已落但未阻断。

### C-02 正确性-数据丢失风险：Snapshot 同步等待与 io_event_index/timetamp_ns 竞态 + 最长 300s 无超时上限
- **文件:** `fs-backup/fsdeamon/backup_helper.cpp:537-585`（`DoSnapshot` 主等待环）、`fs-backup/fsdeamon/backup_helper.cpp:919-1008`（解析线程 `DoParserLogDispatch` 仅 `SyncDownState` 快照同步）
- **类别:** 正确性
- **证据:**
  ```cpp
  // backup_helper.cpp:546-585
  if (stat.io_event_index <= m_sync_stat->io_event_index ||
      stat.timetamp_ns <= m_sync_stat->timetamp_ns) break;
  sleep(3); count++; if(count%100!=0) continue; // 300s 才触发 LogSwitch 重试
  // m_err 与 m_sync_stat 无锁跨线程读写（Downloader 改 io_event_index，Parser 改 start_time）
  ```
  `m_sync_stat` 为 `mmap` 共享结构，`DownloadLogDispatch`/`DoParserLogDispatch`/`DoSnapshot` 三线程并发读写 `m_sync_stat->io_event_index/timetamp_ns/start_time/hook_status`，**无 `m_down_mutex` 覆盖** 的直接读（`SyncDownState` 仅在 Parser 环一次拷贝）。DoSnapshot 的退出条件 `<=` 在 `timetamp_ns` 回绕或 Parser 滞后时可能 **提前退出**，导致 `OnCopy` 拷贝未完全 replay 的 LMDB，产出缺事件的“成功”快照。
- **影响:** 增量链断裂需全量；已缺事件的快照会写入 `snapshot.db` 无法自动回滚。
- **建议:** 为 DoSnapshot 增加超时上限（如 5-10min 超时转 `msg="kernel sync timeout"`）；将 `m_sync_stat` 读加 `m_down_mutex`/`std::atomic`；或以 `log_file_index` 为主判定（单调递增更可靠）。

---

## HIGH

### H-01 安全性-缓冲区截断未置终止：`build_dir_path` strncpy 不保证末字节 `\0`
- **文件:** `fs-backup/fsdeamon/fs_kernel_sync.cpp:13-20,143-144,173-174,203-204,232-234,261-262`
- **类别:** 安全性/正确性
- **证据:**
  ```cpp
  // fs_kernel_sync.cpp:16-17
  strncpy(dir_path->app_name, app_name, APP_NAME_LEN - 1);
  strncpy(dir_path->path, path, MONITOR_PATH_MAX_LEN - 1);
  // 调用点 ioctl_buff[4096]={0} 初始为零，但 dir_path 与 stat_tmp 复用同一 4096（fs_kernel_sync.cpp:139-141）
  // FsKernel_GetStat 等 6 处均同模式；若传入恰好 APP_NAME_LEN-1/ PATH_MAX_LEN-1 长且无 \0，依赖残留 0，不健壮
  // fs-backup/tools/main_ioctl.cpp:44-45 同问题
  ```
  当 `ioctl_buff` 非全新零（如复用或栈残留）且输入被截断时，内核将收到 **非终止** 路径，导致 `hook` 层 `strcmp` 越界或匹配错误 monitor。正确写法应为 `strncpy(..., n); dir_path->path[n]='\0';` 或直接 `snprintf`。
- **建议:** 统一替换为 `snprintf(dir_path->path, sizeof(dir_path->path), "%s", path)` 或补 `dir_path->path[MONITOR_PATH_MAX_LEN-1]='\0'`。

### H-02 正确性-固定长拷贝越界：`rpc/rpc.cpp` 等 `strcpy(host->data, remote_file)` 未限长
- **文件:** `rpc/rpc.cpp:228,238,768,778`；`rpc/rpc.cpp:1073,1260,1320`；`rpc/rpc-command.cpp:91,425,561`；`rpc/rpc-client.cpp:1474,2766` 等（全文约 22 处 `strcpy`/`sprintf`）
- **类别:** 正确性/安全性
- **证据:**
  ```cpp
  // rpc/rpc.cpp:238,768
  strcpy(host->data, info__->remote_file); // host 指向 MSG_BUFF_LEN(约1M) 末尾变长区，依赖上游长度合法
  // trans_handle::remote_file[512], info__->remote_file[1024] -> strcpy 512 可能截断但 data 侧无边界
  // rpc/rpc.cpp:1073 strcpy(host->file_name, remote_file); // host->file_name 未在协议头声明 maxlen
  ```
  `msg_download_block_t.data` 为柔性尾数组，协议以 `host->data_len = strlen(host->data)` 为界，但 `strcpy` 前无 `PATH_MAX` 校验，恶意/异常超长路径可写越 `MSG_BUFF_LEN`。同类 `rpc/rpc-client.cpp:2766 strcpy(cmd_host->command, command)` 亦依赖 `snprintf` 已截断（`rpc-client.cpp:965`），但此处直接 `strcpy`。
- **建议:** 全量替换为 `snprintf(host->data, MSG_BUFF_LEN - sizeof(*host), "%s", remote_file)` 并以返回值校验截断；对 `remote_file` 前置 `strlen>PATH_MAX` 拒绝。

### H-03 正确性-解析越界：`parse_file_to_set` 的 `line[j++]` 无边界
- **文件:** `rpc/rpc.cpp:1581-1631`
- **类别:** 正确性
- **证据:**
  ```cpp
  // rpc/rpc.cpp:1588-1613
  char line[PATH_MAX] = {0}; int j=0;
  for(i=0; buf[i]; i++){
    if(buf[i]!=';' && buf[i]!='\n' && buf[i]!='\r'){
      line[j]=buf[i]; j++; // 无 j < PATH_MAX-1 保护
    } else if(buf[i]==';'){ files_list.insert(line); memset(line,0,...); j=0; }
  }
  // 另：仅在 ';' 时插入，'\n' 分隔的行被丢弃；尾部 "x;" 与 "x\n" 行为不一致
  ```
  单个分号段超 `PATH_MAX` 将堆栈越界；`--exclude-from` 等文件若被误填超长行可稳定复现。
- **建议:** 增加 `if (j >= (int)sizeof(line)-1) { ErrorLog; memset(line,0,...); j=0; continue; }`；统一将 `\n`/`\r` 也视为分隔符。

### H-04 并发-锁粒度错误：`FsSource` 多处状态未加锁或不一致加锁
- **文件:** `fs-backup/fsdeamon/fs_source.cpp:118-177`（`FSDeamonDestory` 全程持锁但内部 waitpid 阻塞持锁）、`fs-backup/fsdeamon/fs_source.cpp:315-403`（`AddBackupHelper`/`DelBackupHelper`/`AddExcludeDir`/`DelExcludeDir` **无** `m_mutex`，而 `ChangeTrackup`/`ChangeExclude` 外层已持锁再调用 → 嵌套不一致；`CheckAndRestartBackupHelperProcesses` 遍历 `m_MapBakHelperProcess` **无锁**）
- **类别:** 正确性/并发
- **证据:**
  ```cpp
  // fs_source.cpp:406-439 CheckAndRestart 未加锁遍历
  void FsSource::CheckAndRestartBackupHelperProcesses(){
    for(auto &iter: m_MapBakHelperProcess){ // 无 lock
      if(proc.client->Ping()!=0){ kill(); waitpid(); launchBackupHelper(); }
    }
  }
  // fs_source.cpp:315 AddBackupHelper 修改 m_MapBakHelperProcess/m_bits/m_trackups 并 SaveConf，未加锁
  // fs_source.cpp:834 AddTrackup 已持锁再调 ChangeTrackup -> Del/AddBackupHelper(无锁) 仍在临界区，但 DelBackupHelper 内 waitpid 阻塞会放大临界区
  // fs_source.cpp:124 FSDeamonDestory 持锁 waitpid 所有 helper，阻塞期间其他 RPC 线程无法 List/Check
  ```
  `CheckAndRestart` 与 `AddTrackup/DelTrackup` 并发时 `m_MapBakHelperProcess` 迭代器失效可致 coredump；`FSDeamonDestory` 持锁 `waitpid` 导致长阻塞。
- **建议:** 为 `KernelSyncRun/AddBackupHelper/DelBackupHelper/AddExcludeDir/DelExcludeDir/CheckAndRestart` 统一加 `m_mutex`（或读写锁）；`FSDeamonDestory` 先 `swap` 出 map 再无锁 `kill/waitpid`/`FsKernel_Del*`。

---

## MEDIUM

### M-01 错误处理-静默失败：`DoSnapshot` 错误语义与诊断合并
- **文件:** `fs-backup/fsdeamon/backup_helper.cpp:537-644`、`fs-backup/fsdeamon/backup_helper.cpp:810-905`（`DownloadLogDispatch` 的 `m_err++` 无可见性）
- **类别:** 错误处理
- **证据:** DoSnapshot 在 `FsKernel_SyncStatOne/LogSwitch` 失败时仅 `msg="kernel sync failed"`，未回填 `req.host/port/err_no/detail`，与已修复的 `fs_kernel_sync.cpp` 诊断链路不对齐；`DownloadLogDispatch` 的 `m_err` 为普通 `int` 非 `atomic`，跨线程累加无序。
- **建议:** 复用已修复的 `detail[512]` 回填到 `json_response["detail"]`；`m_err` 改 `std::atomic<int>`。

### M-02 错误处理-资源泄漏：`backup_helper.cpp:1062-1298` Unix 套接字线程与 fd 泄漏点
- **文件:** `fs-backup/fsdeamon/backup_helper.cpp:1070-1198`（`ClientHandlerThread`）、`fs-backup/fsdeamon/backup_helper.cpp:1200-1284`（`RunAsServer` 的 `accept` 循环）
- **类别:** 错误处理/资源
- **证据:**
  ```cpp
  // 1077-1088 读长度失败仅 close+delete，但未对 req_len ntohl 后的超大值做 write 回包前已 delete
  // 1121-1124 写 response 的 write 未检查短写（应循环 write）；RunAsServer accept 后 create_thread 失败仅 close+delete，但 server_fd 未设非阻塞，SIGTERM 无法优雅退出
  // 1298 后 RunAsServer 的 while(1) accept 无退出条件，unlink 仅启动时一次
  ```
- **建议:** 对 `write` 循环直到全量；RunAsServer 增加 `atomic<bool> stop` 与 `shutdown(server_fd, SHUT_RDWR)` 退出路径。

### M-03 正确性-TOCTOU + 原子性：`FsSource::SaveConf` 先写 tmp 再 rename 但无 fsync
- **文件:** `fs-backup/fsdeamon/fs_source.cpp:253-272`
- **类别:** 正确性
- **证据:**
  ```cpp
  std::ofstream ofile(context_file_tmp);
  ofile << data.dump(4) << std::endl; ofile.close();
  rename(context_file_tmp.c_str(), m_conf_path.c_str()); // 无 fsync(dir)
  ```
  掉电可能丢失 `m_bits/m_trackups` 映射，重启后 `ReadConf` 的 `size !=` 校验失败（`fs_source.cpp:245`）直接拒绝加载，导致服务无法启动。
- **建议:** `ofile.flush(); fsync(fileno); fsync(dirfd)` 后再 rename；或保留旧文件备份。

### M-04 安全性-路径注入/遍历：`--remote/--local` 等参数未规范化
- **文件:** `rpc/rpc-client.cpp:1394-1410`（仅去尾 `/`）、`rpc/rpc.cpp:1765-1798`（`rpc_conn_cli_*` 直接 `buf_put_cstring(remote_path)`）、`fs-backup/fsdeamon/fs_source.cpp:669-831`（`CheckPathValid` 仅判空与白名单，未 `realpath`/`..` 归一）
- **类别:** 安全性
- **证据:** `CheckPathValid` 实现为空或简易前缀检查（见 `fs_source.cpp:684` 调用），`../` 可穿透 `data_path` 拼接（`fs_source.cpp:280-285 data_path+buff` 以不可控 `bit` 命名虽有限，但 `remote_path` 直达内核 `monitor[]` 仍可构造 ` /etc/shadow` 类路径触发内核越权监控）。
- **建议:** 对 `remote_path` 执行 `realpath` 或至少拒绝含 `..` / `//` / `\0` 的输入，并校验其为已配置 `monitor` 前缀或白名单。

### M-05 性能-N+1 与串行回退：`CheckSource`/`List` 等 MergeMultiResponse 串行 RPC
- **文件:** `fs-backup/fsdeamon/fs_source.cpp:454-493`（`List`）、`fs-backup/fsdeamon/fs_source.cpp:862-916`（`CheckSource`）、`fs-backup/fsdeamon/fs_service.cpp:178-501`（`FsService` 转发）
- **类别:** 性能
- **证据:**
  ```cpp
  // fs_source.cpp:1246-1262 MergeMultiResponse
  for(const auto &path: paths){ json resp = fetch_fn(path); json_response[path]=resp; }
  // fetch_fn 内 BackupHelperClient::GetStat -> 每次新建 AF_UNIX connect + JSON parse，trackup=64 时 64 次串行
  ```
  64 目录时 List 需 64 次 Unix socket 往返，延迟线性增长；失败一条即 `all_success=false` 但仍继续串行。
- **建议:** 改为 `std::async`/线程池并发收集，或在 BackupHelper 侧增加批量 `mget_stat` 接口。

### M-06 性能-过度拷贝：`GetDirTreeFile()` 值返回导致全量拷贝
- **文件:** `rpc/rpc-client.cpp:177-179`（`std::set<std::string> GetDirTreeFile() { return m_dir_tree_files; }`）、`rpc/rpc.cpp:1923,2072` 等 `scp_info_t` 频繁 `new/delete`
- **类别:** 性能/可维护性
- **证据:** 每次 `GetDirTreeFile()` 拷贝整棵目录树集合（可能万级）；`ScpDownloadFilesThread` 等热路径 `new scp_info_t/new scp_files_t` 未用对象池。
- **建议:** 改为 `const std::set<...>&` 或 `std::shared_ptr<const Set>`；或提供 `Swap` 语义。

### M-07 可维护性-重复协议分支：`rdb-cfg/cli.c:91-117` 与 `libs/rdb-config.c:224-474` 的键表双重维护风险
- **文件:** `rdb-cfg/cli.c:42-120`、`libs/rdb-config.c:224-605`
- **类别:** 可维护性
- **证据:** `g_cfg_keys` 为 SSOT，但 `cli.c:cmd_gen` 对 `type==BOOL` 硬编码回退文案 `0=关闭,1=开启`，与 `g_cfg_keys[].allowed_values` 的 TLS 双枚举文案分散；新增 `cfg_key_id` 时 `cli.c` 的 `seen_sec` 去重仅 256*64 固定栈，若 `CFG_KEY_COUNT` 超限截断无告警。
- **建议:** 将 BOOL 文案也收口至 `g_cfg_keys[].allowed_values`；`seen_sec` 改动态 `std::set` 或 `CONFIG_KV_MAX` 约束校验。

### M-08 安全性-敏感参数明文残留：`--key`/`--cert_dir` 日志与 `getopt` 明文
- **文件:** `rpc/rpc-client.cpp:1572`（`memset(optarg,'*',...)` 仅覆盖当前 `optarg` 缓冲，非 `argv` 原串）、`rpc/rpc-server.cpp:542-550`（`ErrorLog("key verification failed for key: %s", msg_req->key)` 明文打日志）、`libs/tls_cert.c:86-96`（`tls_cert_log_setup_error` 明文打印完整路径）
- **类别:** 安全性
- **证据:** 服务端错误日志会完整打印 `key` 明文（`rpc-server.cpp:544`）；客户端 `memset` 未覆盖 `argv[i]` 原始内存，`ps aux` 仍可见 `--key xxx`。
- **建议:** 移除 `key` 明文日志，改为 `key_len` 或 `sha256(key)`；启动后 `memset(argv[i],0,...)` 并 `prctl(PR_SET_MM_ARG_*)` 或改用环境变量/文件。

---

## LOW

### L-01 可维护性-魔术数与硬编码阈值
- **文件:** `fs-backup/fsdeamon/backup_helper.cpp:83,765,880,1029`（`MMAP_SIZE` 未在头中注释、`SYNC_COUNT 10`、`sleep(3/5/10)` 硬编码）、`rpc/rpc-server.cpp:1221`（`sprintf(buff, "open file:[%s] failure.")` 依赖 `resp_host->data` 隐式大小）
- **证据:** 轮询间隔与重试阈值散落，调整需跨 5 文件；`sprintf` 同类已在 hotspots 有 4 处残留（`rpc-server.cpp:889,982,986`）。
- **建议:** 收口为 `constexpr int kSyncReportInterval=10; kPollInterval=3s;` 并以 `snprintf` 替代 `sprintf`。

### L-02 测试-覆盖缺口：`fsbackup_kernel` 与 `Download/Parser` 线程无可重复单测
- **文件:** `test/`、`fs-backup/fsdeamon/tests/`、`libs/tests/`（现有多为 happy path）、`fs-backup/public/tests/fs_meta_comprehensive_test.cpp:76-830`（`system("rm -rf /tmp/...")` 直接环境依赖）
- **类别:** 测试
- **证据:** `DoSnapshot` 的 300s 等待、`CheckAndRestart` 的并发竞态、`parse_file_to_set` 的越界均无回归用例；`system("rm -rf")` 在 CI 非隔离环境可误删。
- **建议:** 为 `parse_file_to_set` 增加边界单测（超长行/无分号尾行/混合换行）；为 `DoSnapshot` 增加 mock `m_sync_stat` 超时用例；为 `FsSource` 增加并发 Add/List 模糊测试。

### L-03 错误处理-不一致的超时语义
- **文件:** `rpc/rpc-io.cpp:208,246,373,403`（`read_is_ready/write_is_ready` 超时仅 `WarningLog` 后继续循环）、`rpc/rpc.cpp:246-251`（`read_is_ready` 失败直接 `-1`）、`fs-backup/fsdeamon/backup_helper.cpp:798-810`（`GetStat` 失败仅 `m_err++` 后 `sleep(10)` 盲重试）
- **类别:** 错误处理
- **证据:** 同一 `read_is_ready` 在 `rpc_download_block` 中视为致命（`goto return__`），在 `DownloadLogDispatch` 中仅 `sleep` 重试，语义不一致导致排障困难。
- **建议:** 统一超时错误码（`ETIMEDOUT`）并在 `json_response` 中回显 `timeout_ms/read_timeout`。

---

## 已修复项引用（T0463，不重复深入）

- `rpc/rpc.cpp:1549-1566`、`rpc/rpc-io.cpp:154-220`：已将 `connect_server_session` 的 `!=0` 误判修复为 `<0`，并细分 `socket/connect/bind/handshake(mtls)` 四类错误，携带 `errno/mtls/cert_dir/port` 诊断到 `buf` 与 `ErrorLog`。
- `fs-backup/fsdeamon/fs_kernel_sync.cpp:45-88,118-177`：已为 `FsKernel_Add/DelTrackup` 等补 `conn->host:port + ioctl_buff` 关联日志。
- `fs-backup/fsdeamon/fs_source.cpp:669-758,790-830`：已为 `ChangeTrackup/ChangeExclude` 回显 `source_host/port + detail`，`AddSource` 增加 `open_service` 预检。
- 结论：T0463 阻塞已闭环；本清单不再对该误判展开，仅在其基础上评估残留的截断/越界/并发等二阶问题（H-01/H-04 等）。

---

## 修复优先级建议

1. **P0（下次发版前）**: C-01 命令注入鉴权、H-04 并发锁、H-02/H-01 越界截断
2. **P1（近期）**: C-02 快照竞态/超时、H-03 解析越界、M-08 密钥脱敏
3. **P2（迭代）**: M-03 fsync、M-04 路径规范化、M-05 并发化、L-01~L-03 清理与补测

## 抽样方法与工具

- `grep -rn "strcpy|sprintf|strcat" --include="*.c/*.cpp"` 全量扫描（22 处未限长拷贝，3 处 `sprintf`）
- `grep -rn "strncpy.*- 1"` 14 处，核对 `dev_ioctl.h:APP_NAME_LEN=128, PATH_MAX_LEN=512` 末字节保障
- `grep -rn "m_mutex|lock_guard|waitpid|fork|kill"` 并发与生命周期审计
- `grep -rn "parse_file_to_set|j++|line\[j"` 边界审计
- 人工精读：`fs_source.cpp:669-860`、`backup_helper.cpp:537-644,767-909,1062-1284`、`rpc-server.cpp:854-1020,2600-2627`、`rpc.cpp:1581-1631,193-287`、`libs/rdb-config.c:224-605`、`rdb-cfg/cli.c:42-120`

