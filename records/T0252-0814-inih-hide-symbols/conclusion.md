---
schema: pdca.asset/v1
id: T0252-0814-inih-hide-symbols
phase: check
source_ids: [e-ac1-count, e-ac2-build, e-ac3-nmd, e-ac4-readelf, e-ac5-linkcmd, e-ac6-install, e-ac7-version, e-ac8-rootcause, convergence-map]
---

## 上下文

任务目标：inih 作为第三方静态库被 7 个 target 链接。其中共享库（libxbsa64.so）静态链接
inih 后，把 inih 的 C API（ini_parse 等）导出到动态符号表，造成 API 符号泄漏，可能与其他
动态库中的同名符号冲突。方案：通过 `add_requires` 配置隐藏 inih 的 API 符号，同时移除
`inih_static` 别名，全部 7 处统一为 `inih` 引用 + 静态连接。

## 假设与结果

| 假设 | 结果 |
|------|------|
| 仅用 `cxflags="-fvisibility=hidden"` 即可隐藏 inih API 符号 | ✗ 不成立：inih 头文件 ini.h 中 `INI_API` 宏（gcc 下为 `__attribute__((visibility("default")))`）显式声明 default 可见性，覆盖 `-fvisibility=hidden`；`readelf` 确认符号仍为 GLOBAL DEFAULT |
| 加 `-DINI_API=` 将宏覆盖为空串后隐藏生效 | ✓ 验证成立：`-DINI_API=` 使声明不再带 default 属性，符号落入 hidden 默认；`readelf` 确认 GLOBAL HIDDEN |
| 隐藏后静态链接的二进制仍可正常解析 inih 符号 | ✓ 验证成立：fs-cli/s3-tool `--version` 正常输出；check 二进制调用 ini_parse 正常返回 |
| 移除 inih_static 别名不影响构建 | ✓ 7 处统一后 `xmake build` 全量构建成功 |

## 分析

- 全部 4 项验收标准 PASS，均有独立 evidence 支撑。
- 关键发现（PRD 偏差）：PRD 原方案只写了 `-fvisibility=hidden`，Do 阶段 A/B 实验证明
  不充分——`INI_API` 宏显式 `visibility("default")` 会覆盖编译器默认。必须在 cxflags
  中追加 `-DINI_API=` 覆盖宏，两者缺一不可。
- 对照实验（双包目录 hash）：`6f0a3f82`（仅 fvisibility）符号 GLOBAL DEFAULT（泄漏），
  `6d047740`（+DINI_API=）符号 GLOBAL HIDDEN（正确）；libxbsa64.so 链接命令已确认引用
  新包 `6d047740`。
- 全局扫描 build 下所有 .so，无其他共享库再导出 ini_* 符号；libxbsa64.so `nm -u` 无未
  定义 inih 引用，静态链接完整。

## 失败原因

无（verdict: confirmed）。

## 适用边界

- 本次验证环境：linux x86_64，xmake 3.1.0。
- `-DINI_API=` 覆盖宏作用于所有包含 ini.h 的编译单元，将 inih API 全部标记为 hidden。
  本项目 inih 均为静态链接 + 内部使用，隐藏不产生外部可见性需求，行为安全。
- debug 模式：`debug = is_mode("debug")` 会改变包构建 config hash，inih 重新编译，
  cxflags 仍生效，符号隐藏对 debug 同样适用（未单独实测，风险低）。
- Windows 平台不在本项目目标范围；`-DINI_API=` 与 DLL import/export 场景不兼容，
  若未来需 Windows 支持需另行设计。

## 下一轮建议

- 无阻塞项。可沉淀为可复用知识：第三方 C 库头文件中含显式 `visibility("default")`
  宏（如 INI_API）时，仅 `-fvisibility=hidden` 无效，需同时用 `-D<MACRO>=` 覆盖宏；
  此模式可在 xmake-repo 内 inih/xmake.lua 的 on_install 中加注释提示。
