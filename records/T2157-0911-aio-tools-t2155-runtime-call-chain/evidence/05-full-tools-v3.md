# 构建与发布 Knowledge Map（知识地图）

> **文档定位**：本文是构建装配子系统的导航—— **「构建动作 → 代码位置 → 产物落点」**：加 target、升版本、查产物、改流水线时看什么、改哪里。
>
> **前置阅读**：《00-index》（路由矩阵）
> **阅读约定**：路径一律相对 `6200/release`；`file:line` 行号易变动，以符号名为准
> **依据**：aio-tools 6200/release 实际代码 + 仓内引用统计（基线：目录 6200/release，commit fe9d4364）
> **版本化**：本文为 6.2.0.0 版代码地图，地图与代码基线强绑定；读前先按 00-index §〇 版本路由选版本，再读对应目录下的 `<tag>.md`
> **最后更新**：2026-09-10

---

## 1. 构建体系总览

- xmake 版本要求：`set_xmakever("2.3.6")`（`xmake.lua:1`）；全局 `set_warnings("all","error")`、`set_languages("c99","cxx11")`、`add_cxflags/mxflags -Wno-error=deprecated-declarations -fno-strict-aliasing`（`xmake.lua:3-6`）；`add_rules("mode.release","mode.debug")`（`:8`）。
- 根 `xmake.lua` 结构：1-53 行全局配置 + 版本号变量 + arch 归一化（i386→x86_64，arm64→aarch64，`lib_dir=lib_<arch>`）；57-68 行 `includes()` 聚合 11 子目录；70-80 行定义 `makeFsbackup`。
- 各级分工：根（版本常量/configvar/arch/下发 includes）→ `libs/xmake.lua`（基础静态库 + tls-keygen + timed_net_key wheel）→ `rpc/xmake.lua`（`rpc` static + `aio-speedd/aio-speed` binary）→ `fs-backup/xmake.lua`（纯聚合）→ `s3tools/xmake.lua`（纯聚合）→ `xbsa/xmake.lua → src/xmake.lua`（两级聚合）→ `bwlimit/xmake.lua`（`includes(lib,tests)`）。
- 代码风格：`.clang-format`（ColumnLimit 80，UseTab Always，内核风格）+ `.clang-tidy`（Checks `-*,readability-identifier*,google-*…`，近乎全量 WarningsAsErrors）——但 CI 未见两门禁，标记无法确认是否强制。
- `compile_commands.json`：xmake 生成，262 条 `{directory, arguments[], file}`，供 clangd 用。

---

## 2. 产物清单（target → 产物 → 落点）

默认 `xmake build` 只建 `set_default(true)` 或未设 false 者；大量 `set_default(false)` 为中间库/测试。

| target | 产物类型 | 源码范围 | 落点（install/ 下） | 出处 |
|---|---|---|---|---|
| makeFsbackup | binary（Go embed） | `main.go` + `fsbackup_kernel_4.x` | `bin/makeFsbackup` | `xmake.lua:70-76` |
| tls-keygen | binary | `libs/tls_keygen.c,common.c` | `tls-keygen/<arch>/` | `libs/xmake.lua:6-18` |
| timed_net_key | shared + wheel | `libs/timed_net_key.c` | `wheel/`（after_build 调 `setup.py bdist_wheel`） | `libs/xmake.lua:41-86` |
| tls_cert/timed_key/rdb-config/logger/tools/rpc-net/lmdb/bwlimit/s3tools/s3_tools_public/fs_backup_public/rch/utils/xlog | static（中间） | 各目录 | 仅被 deps 链接，不安装 | 各目录 xmake.lua |
| rpc | static（`false`） | `rpc/*.cpp/c` | 被 aio-speed 系链接 | `rpc/xmake.lua:6-40` |
| aio-speedd | binary | `rpc/main.cpp` + server/session/rpc-net | `rpc/<arch>/aio-speedd` + service/sh | `rpc/xmake.lua:42-87` |
| aio-speed | binary | `rpc/rpc-client.cpp` + client/session | `rpc/<arch>/aio-speed` + rpc 软链接 | `rpc/xmake.lua:88-131` |
| fsdeamon | binary | `fs-backup/fsdeamon/*` | `fs-tools/<arch>/fsdeamon` | `fsdeamon/xmake.lua:6` |
| fs-cli | binary | `fs-backup/fsclient/*.cpp` | `fs-tools/<arch>/fsclient/` | `fsclient/xmake.lua:4` |
| fsbackup_tools | binary | `fs-backup/tools/*.cpp` | `fs-tools/fsbackup_tools` | `tools/xmake.lua:1-4` |
| rdbcomm | binary | `rdbcomm/rdbcomm-main.c` + client/module/msg.c | `rdbcomm/<arch>/rdbcomm` | `rdbcomm/xmake.lua:2-14` |
| rdbcommd | binary | `rdbcomm/rdbcommd-main.c` + server/module/msg.c | `rdbcomm/<arch>/rdbcommd` | `rdbcomm/xmake.lua:15-26` |
| sbt | shared | sbt lib/logic + sbt + quickLZ + lz4 | `obk_ftp/<arch>/libsbt.so*` | `libobk/xmake.lua:2-12` |
| FileTransferAgent | binary | `libobk/*.c` + logic/quickLZ/lz4 | `obk_ftp/<arch>/` | `libobk/xmake.lua:15-25` |
| dmsbtex | shared | `dmsbtex/*.c` | `dm_ftp/<arch>/libdmsbtex.so*` | `dmsbtex/xmake.lua:3-13` |
| dm-ftp | binary | dmsbtex main 系 | `dm_ftp/<arch>/` | `dmsbtex/xmake.lua:16-25` |
| bwlimit_tools | binary | `bwlimit/*.c` | `bwlimit/<arch>/` | `bwlimit/xmake.lua:5-11` |
| s3file | binary | `s3tools/s3file/*.cpp` | `s3tools/<arch>/` + `lib_<arch>/` | `s3file/xmake.lua:5` |
| s3mount | binary | `s3tools/s3mount/*.cpp` | `s3tools/<arch>/` + `lib_<arch>/` | `s3mount/xmake.lua:6` |
| s3-tool | binary | `s3-tool/*.cpp/c` | `s3-tools/<arch>/s3-tool/` + `lib_<arch>/` | `s3-tool/xmake.lua:6-39` |
| afsd | binary | `huanweicloun…/my-fuse/*.cpp` | `s3-tools/<arch>/afs/` + `lib_<arch>/` | `my-fuse/xmake.lua:4` |
| afs-cli | binary | `huanweicloun…/my-fuse/*.cpp` | `s3-tools/<arch>/afs/` + `lib_<arch>/` | `my-fuse/xmake.lua:54` |
| xbsa64 | shared | `xbsa/src/xbsa/*.c` | `xbsa/<arch>/libxbsa64.so*` | `xbsa/src/xbsa/xmake.lua:4-14` |
| rch-tools | binary | `xbsa/src/*.c` | `rch/<arch>/` | `xbsa/src/xmake.lua:3-12` |
| rpc-keygen | binary（`false` 默认不编） | `rpc-keygen/main.c` + `libs/timed_key.c`（`-static`） | 无 prefixdir（build 目录） | `rpc-keygen/xmake.lua:1-10` |

---

## 3. 版本机制

1. 源头：根 `xmake.lua:12-24` 硬编码 12 个版本变量（如 `rpc 3.6.4.19`，`fsbackup_kernel 3.3.1.6`）。
2. 注册：`set_configvar` 逐一注册（`xmake.lua:27-39`）。
3. 渲染：`add_configfiles("version.h.in","version.log.in")` 在 `xmake f/config` 期渲染到 `build/version.h`（C 宏如 `RPC_VERSION`）、`build/version.log`（20 行 `binary "x.y.z"` 映射）。
4. 分发：各交付 target 用 `add_configfiles("version.in", {filename=<target>.version})` 将对应变量渲染为单行 `*.version` 并 `add_installfiles` 随包发布；各子目录 `version.in` 仅一行占位（如 `libs` 的 `${TLS_KEYGEN_VERSION}`，根的 `${FSBACKUP_KERNEL_VERSION}`）。
5. 发布：CI 把 `build/version.log` 同步为 aio-public-module 的 `tools-versions.txt`（`.gitlab-ci.yml:130`）。
6. 特殊：`makeFsbackup.before_build` 写 `fsbackup_kernel_4.x/version.h`（`#define VERSION`，`xmake.lua:78-80`）。

**升级版本套路**：根 xmake 改变量 → `version.h.in` / `version.log.in` 各加一行（如新增组件）→ 各 target 的 `version.in` 占位 → `xmake f` 验证 `build/version.log`。

---

## 4. 内核模块构建（与 xmake 解耦）

- `fs-backup/kernel/` 仅含 `device/dev_ioctl.h`（用户态-内核接口），无 Makefile/Kbuild，不独立构建。
- 真正模块源码在顶层 `fsbackup_kernel_4.x/`（`fs_backup.c` + conf|device|imp|log|network|sys|utils/ + Makefile），Kbuild 写法 `obj-m := fsbackup.o`，`$(MAKE) -C $(KDIR) M=$(PWD) modules`，KDIR 缺省 `/lib/modules/$(uname -r)/build`（`Makefile:1-17`）。
- xmake 仅在 `makeFsbackup.before_build` 注入版本（`xmake.lua:78-80`）；`makeFsbackup` 本身是 Go 程序（`main.go`）：`//go:embed fsbackup_kernel_4.x` 打包内核源码 → 运行时解包到 tmpdir → 执行 `make && cp fsbackup.ko /opt/aio/airflow/tools/fs-tools/$(uname -m)/kernel/$(uname -r)/ && insmod` → `modinfo --field=version` 回显（`main.go:16,104-119`）；先 `lsmod|grep fsbackup`，存在则 `rmmod`（`main.go:73`）。
- 无法确认：该 `.ko` 是否进 `xmake install` 包（install 树无 kernel 子目录，`main.go` 写死 `/opt` 路径），缺打包脚本证据。
- 目录现存 `fsbackup.ko/.o/.mod.c` 系本地 make 残留（构建污染，见 01 §7）。

---

## 5. 装配与发布

- `install/` 结构 = 按产品线 + arch 分仓：`bin/`、`rpc/<arch>/`、`rdbcomm/<arch>/`、`fs-tools/<arch>/`、`s3tools/<arch>/`、`s3-tools/<arch>/{s3-tool,afs}/`、`obk_ftp/`、`dm_ftp/`、`bwlimit/`、`rch/`、`xbsa/`、`tls-keygen/`、`wheel/`；每 binary 旁带 `*.version`，shared 带 `.so[.1[.x.y.z]]`，s3 系附 `lib_<arch>/*.so + OBS.ini`，rpc/fsdeamon 附 service/sh。
- 输出位置机制：`set_prefixdir("<产品>/"..arch, {bindir="", libdir=lib_dir})` + `add_installfiles`（含第三方 so 搬运，`s3mount/xmake.lua:29,40,51`）。
- CI 流水线（`.gitlab-ci.yml:27-31`，stages = check_message → test → get_version → sync_version，仅 push/MR 触发）：
  - test_job（MR only）：`xmake config -m debug && xmake && xmake test`（`:65-82`）。
  - get_version（push only）：`xmake f` 并断言 `build/version.log` 存在（`:84-100`）。
  - sync_version：`build/version.log` 拷为 aio-public-module `tools-versions.txt` 并经 sync/version 分支提 MR（`:102-161`）。
  - commit 题需 `【[s,f,m,B,F,T]-数字】`（allow_failure，`:48-63`）。
- `third_party/`：fuse/、gmssl/、huaweicloud-sdk-c-obs/、nlohmann/（header-only）、sqlite3/；前三者为 `include/ + lib_<arch>` 预编译 so（`s3-tool/xmake.lua:23-33`）；sqlite3 仅 fsdeamon 用且不 install（注释掉，`fsdeamon/xmake.lua:29-34`）。

---

## 6. 新模块如何接入构建（三件套，归纳自现有 target）

1. 选位置建目录 + 写 `target("<名>")`：binary 用 `set_kind("binary")`；公共复用库用 `set_kind("static") + set_default(false)`；对外 so 用 `set_kind("shared") + set_version(<ver>, {soname=true})`（參 sbt/dmsbtex/xbsa64）。
2. 三件套必抄：
   - `set_prefixdir("<产品>/"..arch, {bindir="", libdir=lib_dir})` 定 install 仓；
   - `version_name = "<t>.version"` + `add_configfiles("version.in", {filename=version_name})` + `add_installfiles("$(builddir)/"..version_name)` 发版本（`version.in` 放 `${XXX_VERSION}`，根 xmake 加变量 + `set_configvar` + `version.h.in` / `version.log.in` 各加一行）；
   - `add_deps("logger","tools",…)` 复用基础库，`add_packages("inih_static")` 按需。
3. 预编译依赖抄 s3 系：`local l = os.projectdir().."/third_party/<sdk>/lib_"..arch` + `add_includedirs/add_linkdirs/add_installfiles(l.."/*", {prefixdir=lib_dir}) + add_links(…)`。
4. 链路上加 `includes("<新目录>")`（根或父 xmake）；测试另建 `tests/xmake.lua` 并在父中 `includes("tests")`；特殊安装动作抄 `after_install`（软链接，`rpc/xmake.lua:76-85`）/ `after_build`（wheel，`timed_net_key`）。

---

## 7. 分支差异

- 本分册基于 6.2.0.0（`6200/release`，`fe9d4364`）。他分支的版本变量与 target 矩阵若有差异，差异补记于此，当前为空（待实证）。

## 8. 全量工具独立装配链

根 `xmake.lua:57-68` 聚合所有子目录；每个下列入口都必须单独从 target 路由到产物，不因仓内无调用方而从构建地图删除：

| 工具 | target/入口 | 核心 → 产物或副作用 | 状态 |
|---|---|---|---|
| `fs-cli` | `fs-backup/fsclient/xmake.lua:4` | method handler → 8901 请求/6611 数据传输 | 运行时客户端 |
| `fsdeamon` | `fs-backup/fsdeamon/xmake.lua:6` | FS 分发 → BackupHelper/kernel/meta | 运行时服务 |
| `fsbackup_tools` | `fs-backup/tools/xmake.lua:1` | 子命令 → ioctl/meta/done 解析 | 独立运维工具 |
| `fsbackup.ko` | `fsbackup_kernel_4.x/Makefile:1-17` | hook/driver → 监控日志与字符设备 | 内核模块 |
| `makeFsbackup` | `xmake.lua:70-80` + `main.go:73-119` | embed/make/cp/insmod → 内核安装 | 装配工具 |
| `s3-tool` | `s3-tool/xmake.lua:6` | CLI → S3 upload/download/list → 对象存储 | 对外交付入口 |
| `s3file` | `s3tools/s3file/xmake.lua` | 文件操作 → S3 对象 | 对外交付入口 |
| `s3mount` | `s3tools/s3mount/xmake.lua` | 快照挂载 → FUSE 文件系统 | 对外交付入口 |
| `afsd` | `my-fuse/xmake.lua:4` | FUSE 服务 → S3 文件系统 | 对外交付入口 |
| `afs-cli` | `my-fuse/xmake.lua:54` | CLI → S3 文件系统 | 对外交付入口 |
| `xbsa64` | `xbsa/src/xbsa/xmake.lua` | XBSA API → shared library | 外部消费者入口 |
| `rch-tools` | `xbsa/src/rch/xmake.lua` | 解析工具 → 外部备份结果 | 外部消费者入口 |
| `sbt` | `libobk/xmake.lua:2-12` | SBT API → OBK shared library | 外部消费者入口 |
| `FileTransferAgent` | `libobk/xmake.lua:15-25` | 服务 → OBK 传输，端口 12000 | 外部消费者入口 |
| `dmsbtex` | `dmsbtex/xmake.lua:3-13` | DMSBT API → 达梦 shared library | 外部消费者入口 |
| `dm-ftp` | `dmsbtex/xmake.lua:16-25` | 服务 → 达梦传输，端口 1255 | 外部消费者入口 |
| `bwlimit_tools` | `bwlimit/xmake.lua:5` | CLI → `bwlimit` shared-memory 服务 | 运维/测试入口 |
| `tls-keygen` | `libs/xmake.lua:6` | keygen main → TLS certificate/key 文件 | 运维工具 |

“仓内无调用方”只表示 runtime-consumer 状态为 `external` 或 `operator`，不表示 target、安装产物或独立调用链不存在。
