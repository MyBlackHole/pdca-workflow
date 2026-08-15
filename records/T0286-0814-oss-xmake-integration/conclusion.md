---
schema: pdca.asset/v1
id: T0251-0814-oss-xmake-integration
phase: check
source_ids: [e-build-test, e-version, e-help, e-install, e-version-h, e-version-log, e-debug, e-standalone, e-script, e-commit, convergence-map]
---

## 上下文

任务目标：将 oss（Aliyun OSS Emulator，Go 多包 module + vendor）纳入根 xmake 统一构建，
产出 aio-oss 二进制并纳入版本管理体系。产物安装到 aio-oss/<arch>/，版本号 1.0.0.0 经
-ldflags -X 注入替代硬编码。

实现方式：oss/xmake.lua 自定义 on_build（因多包 module 无法用 add_files 文件列表构建），
在 oss/ 目录内执行 `go build -mod=vendor` 并注入版本；根 xmake.lua 增加 oss_version + 
set_configvar + includes("oss")；version.h.in/log.in 加 OSS_VERSION 条目；oss/cmd/main.go
硬编码版本改为变量；新增 oss/test/build_oss.sh 验收脚本。

## 假设与结果

| 假设 | 结果 |
|------|------|
| 多包 go module 无法用 add_files 构建，需自定义 on_build | ✓ 验证成立：文件列表构建报 "named files must all be in one directory"，改为 on_build 后成功 |
| target:targetfile() 返回相对路径，curdir=oss 下需转绝对 | ✓ 验证成立：未转绝对时二进制被写入 oss/ 子目录 |
| set_basename("aio-oss") 控制产物名 | ✓ 产物 build/.../aio-oss 正确 |
| -ldflags "-X oss/cmd.version=<ver>" 注入版本 | ✓ --version 显示 1.0.0.0（非硬编码 1.0.0） |
| add_configfiles 生成的版本文件位于 $(builddir)（build/ 根） | ✓ 验证成立：实际路径 build/aio-oss.version |

## 分析

- 全部 8 项验收标准 PASS，均有独立 evidence 支撑。
- 版本体系对齐 xbsa 先例（commit 25d5742d）：oss_version 变量 → set_configvar →
  version.h.in/log.in → 目标生成 .version 文件 → 安装。
- 保留了 oss 独立 go module/vendor 结构，`cd oss && go build` 独立构建回归通过，
  兼容原有开发方式。
- debug 模式下额外注入 -gcflags=-N（对齐 xmake 原生 go 工具行为）。

## 失败原因

无（verdict: confirmed）。

## 适用边界

- 本次验证环境：linux x86_64，Go 1.26.5，xmake 3.1.0。
- aarch64 架构理论上可用（arch 变量已抽象），但未实测验证，若有交叉编译需求需另行验证。
- 构建依赖本机 Go 工具链（>=1.21.6）及 xmake 环境；CI 需预装 Go。
- 版本注入仅覆盖 cli 的 --version 输出，OSS HTTP API 响应（如 x-oss-bucket-version 等）
  仍是业务模拟值，不在本任务注入范围。

## 下一轮建议

- 无阻塞项。可选：将 oss/test/build_oss.sh 纳入 CI 或 runmd 文档。