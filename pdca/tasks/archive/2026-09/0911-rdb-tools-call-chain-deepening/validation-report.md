# T2180 Do 验证报告

验证日期：2026-09-11。事实基线：`/home/black/Public/aio/aio-tools/6200/release`，commit `fe9d4364748b9918b5613d01e048be68dbdf1e0a`。

## 交付范围

本次只更新 `rdb-tools-design` 的现有 `SKILL.md`、`references/00-index.md` 与 01–05 五份 `6.2.0.0.md`。没有创建 23 个独立工具页，没有修改 aio-tools 产品源码、构建脚本或运行行为。

调用链按真实入口、参数/请求构造、分发、核心实现、跨进程/内核/SDK 边界、对端消费和结果返回展开；状态区分 `current`、`external`、`operator`、`build-only`、`isolated`、`deprecated`。

## 自动与人工复核结果

| 检查 | 结果 | 覆盖 AC |
|---|---|---|
| `quick_validate.py /home/black/Public/aio/rdb-skills/skills/rdb-tools-design` | PASS，`Skill is valid!` | AC-7 |
| 23 工具索引连续性 | PASS，索引行 1–23，无缺项 | AC-1、AC-5 |
| 源码公开操作清单对照 | PASS：fs-cli method 21；fsbackup_tools command 5；afs-cli method 18；rpc `MT_*` request 19；persistent opcode 19；XBSA ABI 16；SBT2 API 11；DMSBT ABI 13 | AC-1、AC-4、AC-7 |
| Markdown 文件与 heading 引用 | PASS，7 个 Markdown、53 个内部链接均可解析 | AC-5、AC-7 |
| 新增调用链 `path:symbol` | PASS，138 个去重锚点的路径存在且符号可在对应源码定位 | AC-2、AC-7 |
| 复杂链层数 | PASS：01 有 11 条、02 有 8 条、03 有 4 条、04 有 12 条至少五节点链；最大分别 21/19/15/25 节点 | AC-3 |
| 关键协议两端 | PASS：20 个 fs-cli `FS_*` 分支（含 3 个本地/6611 例外）、19 个 `MT_*`、11 个 rdbcomm opcode、10 个 ioctl 常量/三份头文件、6 个 AFS 未闭合 method 均逐字核对 | AC-4 |
| 占位扫描 | PASS，`TODO/TBD/FIXME/示例占位` 零命中 | AC-7 |
| aio-tools 产品树 | PASS，`git status --short` 与 `git diff --stat` 均为空；HEAD 未变化 | AC-8 |
| task 收敛字段 | PASS，`meta.convergence` 保持 PRD 三项原值，`meta.ontology_fragment="ontology"`，`meta.phase="do"` | Do 门禁 |

## 关键实证结论

- `fs-cli -> fsdeamon -> BackupHelper -> rpc 6611 -> fsbackup.ko` 的控制面、helper unix socket、ioctl 生产/消费端和 JSON 返回均已闭合；`FS_RESTORE` 是本地恢复，两个 `FS_FSDEV_*` method 改走 6611。
- `aio-speed -> aio-speedd` 同时保留短会话 19 个 `MT_*` 与持久连接 19 个 `NEW_CONN_TMP_*`；`NEW_CONN_TMP_NO=0` 明确为哨兵。`MT_GET_TIME` 的实际生产端是 `libs/rpc-net.c:rpc_get_time`，由 `timed_net_key.c` 调用。
- `rdbcomm -> rdbcommd` 的 INIT、文件读写、命令与模块操作全部闭合到服务端 handler 和 STATUS/HANDLE/DATA/NODATA 返回。
- S3/FUSE 章节枚举 s3-tool、s3file、s3mount、afsd、afs-cli 的公开命令/callback；6.2.0.0 的 afsd 只有 FUSE 入口，没有 8892 TCP listener，因此 afs-cli 的 6 个网络 method 明确标记未闭合。
- XBSA、OceanBase SBT 与达梦 DMSBT 从公开 ABI 分别追到文件实现或 FileTransferAgent/dm-ftp 对端；源码 stub/incomplete 分支与仓外真实消费者边界均已标明。

## 未解决但不阻断 Do 的环境问题

- afs-cli 的 `list-file/lock-snapshot/unlock-snapshot/full-cache/snapshot-cache-stat/local-cache-stat` 在本基线找不到 TCP 接收端，需要其它部署仓、历史版本或实际安装包证据。
- 外部 S3、XBSA、OceanBase、达梦调用者以及目标端口/TLS/权限只能由部署联调确认；静态源码不证明真实备份恢复成功。
- `fsbackup.ko` 在目标内核的符号兼容性和装载结果未做运行验证；本票为文档知识投射且不修改产品代码。

## 阶段边界

任务保持 Do；未创建 `conclusion.md`，未获取 verdict，未执行 Do→Check。
