# Triage Brief — oss 接入 xmake 构建体系

## 分类

- category: `enhancement`
- scenario_type: `development`

## 需求描述

将 `oss/`（Aliyun OSS Emulator，Go 多包 module + vendor）纳入根 xmake 构建体系，实现 `xmake` 统一构建产出 oss 可执行文件，并纳入版本管理体系（对齐 xbsa 先例）。

## 验证结果

- `oss` 目录确认为完整 Go module（oss/go.mod，module oss，go 1.21.6，带 vendor/modules.txt），主程序 oss/main.go → import oss/cmd，当前版本硬编码 "1.0.0"。
- 根 xmake.lua 的 `makeFsbackup` 用 `add_files("main.go")` 构建单文件 Go；oss 无法用文件列表方式（多包），需在 module 目录内 `go build -mod=vendor -o <abs路径> .`。
- 可行性实验（/tmp/opencode/oss-experiment）已通过：自定义 `on_build` + `os.vrunv` + 绝对路径输出，`xmake` 构建成功产出 `build/linux/x86_64/release/oss` 和 `oss.version`，`./oss --version` 正常。
- 关键坑：`target:targetfile()` 返回相对 projectdir 路径，在 `{curdir = oss_dir}` 下必须用 `path.join(os.projectdir(), target:targetfile())` 转绝对输出，否则二进制被写到 oss/ 子目录。

## 先例

- commit 25d5742d 【B-1985】xbsa 融入 xmake 构建体系与版本处理体系：根 xmake.lua 加 `xbsa_version` + `set_configvar` + `includes("xbsa")`；version.h.in/log.in 添加 XBSA_VERSION；各 target 生成 .version 文件并安装到独立 prefixdir。

## 信息缺口

1. 版本号起点（建议 1.0.0.0）
2. 安装 prefixdir（建议对齐 bin/ 或独立 oss/<arch>/）
3. 是否 -ldflags -X 注入构建版本（覆盖硬编码 1.0.0）
4. 是否保留 oss/ 独立 go module/vendor 结构

## 查重

- PDCA tasks/knowledge 无 oss xmake 集成重复任务。

## 建议下一步

- P2 grill 逐轮确认上表信息缺口 → P3 PRD → P6 终审 → Do 实现