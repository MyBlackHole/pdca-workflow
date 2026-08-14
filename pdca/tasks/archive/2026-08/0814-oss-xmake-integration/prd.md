# oss 接入 xmake 构建体系 — 规格文档

## 问题陈述

- **现状**: `oss/`（Aliyun OSS Emulator）是独立 Go 多包 module（`module oss` + vendor），当前需 `cd oss && go build` 手动构建，脱离根 `xmake` 统一构建体系与版本管理体系；cli 版本号硬编码 "1.0.0"。
- **目标**: `xmake` 根目录统一构建产出 `aio-oss` 二进制并安装到 `aio-oss/<arch>/`，纳入版本管理体系（根 xmake.lua 版本变量 + version.h.in/log.in + .version 文件），版本号经 `-ldflags -X` 注入替代硬编码。
- **差距**: 根 xmake.lua 未 `includes("oss")`；无 OSS_VERSION 定义；构建产物无安装路径；版本硬编码在源码。

## 解决方案

用户无需手动 `cd oss && go build`，在仓库根目录执行 `xmake` 即可构建 oss；`xmake install` 将 `aio-oss` 二进制及 `aio-oss.version` 安装到 `aio-oss/<arch>/`；版本号由构建体系统一管理并注入二进制。

## Seam 分析

### 测试接缝
- 本任务为构建系统接入，无业务逻辑变更。可测边界是**构建产物行为**：二进制存在、`--version`/`--help` 输出、版本文件内容、版本注入生效。
- 验证方式：shell 验收脚本驱动 `xmake` 构建后断言产物。不引入 Go 单元测试（不改业务逻辑）。
- 外部依赖隔离：依赖本机 Go 工具链（>=1.21.6）；vendor 已内嵌，无需网络。

### 声明的测试接缝
```markdown
- seam: oss/test/build_oss.sh -> oss/xmake.lua
```

### 验收可测性
- 每个验收项有明确 pass/fail 信号（见验收标准）。
- 边界：debug/release 模式均需构建成功；未安装 Go 时 `xmake` 对 oss 目标应报清晰错误。
- 分层：构建端到端验证（构建→运行--version/--help→检查版本文件）。

## 用户故事

1. 作为构建工程师，我想要在根目录一条 `xmake` 构建 oss，以便统一构建与 CI 集成。
2. 作为版本维护者，我想要 oss 版本号由构建体系管理并注入二进制，以便版本可追溯。
3. 作为部署人员，我想要 `xmake install` 将 aio-oss 安装到约定目录，以便与其他工具部署布局一致。

## 实现决策

- **构建方式**: 不采用 `add_files("*.go")`（多包 module 会触发 go build "named files must all be in one directory" 错误），采用 `on_build` 自定义构建，在 `oss/` 目录内执行 `go build -mod=vendor -o <绝对路径> .`。可行性已验证（P0）。
- **路径陷阱**: `target:targetfile()` 返回相对 projectdir 路径；`os.vrunv` 在 `{curdir = oss_dir}` 下执行，必须用 `path.join(os.projectdir(), target:targetfile())` 转绝对输出，否则二进制被写入 oss/ 子目录。
- **模块划分**:
  - `oss/xmake.lua`（新建）: 定义 `target("oss")`，`set_targetname("aio-oss")`，`set_prefixdir("aio-oss/" .. arch, {bindir = ""})`；自定义 `on_build`/`after_build`/`on_clean`。
  - `oss/version.in`（新建）: `${OSS_VERSION}`，经 `add_configfiles` 生成 `aio-oss.version` 并 `add_installfiles`。
  - 根 `xmake.lua`: 新增 `oss_version = "1.0.0.0"`、`set_configvar("OSS_VERSION", oss_version)`、`includes("oss")`（置于其他 includes 之后）。
  - `version.h.in`: 新增 `#define OSS_VERSION "${OSS_VERSION}"`。
  - `version.log.in`: 新增 `aio-oss "${OSS_VERSION}"`。
  - `oss/cmd/main.go`: 将 `Version: "1.0.0"` 改为引用包级变量 `var version = "1.0.0"`（保留默认值），供 `-ldflags -X oss/cmd.version=<OSS_VERSION>` 注入。
- **版本注入**: `-ldflags "-X oss/cmd.version=" .. oss_version`；oss_version 为根 xmake.lua 全局变量，被 includes 的子脚本直接访问（同 arch 模式）。
- **debug 模式**: 自定义构建不继承 xmake 原生 go 工具的 `-gcflags=-N`，`on_build` 内用 `is_mode("debug")` 显式追加。
- **保留结构**: 保留 `oss/go.mod`/`go.sum`/`vendor/`，`cd oss && go build` 独立构建能力不破坏。

## 测试决策

- 被测模块: `oss/xmake.lua`（构建配置）、`oss/cmd/main.go`（版本注入）、根 `xmake.lua`/`version.h.in`/`version.log.in`。
- 测试方式: `oss/test/build_oss.sh` 验收脚本——构建成功断言 + `--version` 断言注入版本 + `--help` 断言 + 版本文件内容断言 + 独立 `go build` 回归断言。
- 现有测试先例: 无 Go 测试先例；C 项目为手写 `test/` 目录（如 libobk/test/test.c），本次采用构建验收脚本。

## 验收标准

- [ ] AC-1: 根目录 `xmake` 全量构建成功无报错，产出 `build/<平台>/<架构>/<模式>/aio-oss` 二进制。
- [ ] AC-2: `build/.../aio-oss --version` 输出 `1.0.0.0`（经 -ldflags 注入，非硬编码 1.0.0）。
- [ ] AC-3: `build/.../aio-oss --help` 正常展示 `server` 子命令。
- [ ] AC-4: `xmake install` 后 `aio-oss/<arch>/` 下存在 `aio-oss` 与 `aio-oss.version`，版本文件内容为 `1.0.0.0`。
- [ ] AC-5: 生成的 `version.h` 含 `#define OSS_VERSION "1.0.0.0"`，`version.log` 含 `aio-oss "1.0.0.0"`。
- [ ] AC-6: debug 模式 `xmake f -m debug && xmake` 构建成功。
- [ ] AC-7: 回归：`cd oss && go build -mod=vendor .` 仍可独立构建（结构未破坏）。
- [ ] AC-8: `oss/test/build_oss.sh` 脚本运行全部断言通过。

## 范围外

- 不修改 oss 业务逻辑（server/bucket/object 等 handler）。
- 不改动 `.gitlab-ci.yml` CI 配置。
- 不做 oss 功能级测试（S3 API 行为）。
- 不迁移 vendor 或升级 Go 依赖。

## 备注

- 构建依赖本机 Go 工具链（>=1.21.6，与 oss/go.mod 一致），CI 需预装 Go。
- `-X` 注入未导出变量 `oss/cmd.version` 是 Go 官方支持的机制。
- 先例: commit 25d5742d 【B-1985】xbsa 融入 xmake 构建体系与版本处理体系。
