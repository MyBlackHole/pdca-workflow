# Triage Brief — inih 静态库隐藏 API 符号，移除 inih_static 别名

## 分类

- category: `bugfix`（符号泄漏）
- scenario_type: `development`

## 需求描述

当前项目 7 处 `add_requires("inih 60", {system=false, configs={shared=false}, alias="inih_static"})`。
inih 以静态库链接进各共享库（如 libxbsa64.so）后，inih 的 API 符号（ini_parse/ini_parse_file/ini_parse_stream/ini_parse_string）被导出到共享库动态符号表，造成 API 符号泄漏与潜在冲突。

目标：通过 `add_requires` 配置 `cxflags="-fvisibility=hidden"` 隐藏 inih 符号，同时移除 `inih_static` 别名，全部统一为 `inih` 并 static 连接。

## 验证结果（A/B 对照实验 /tmp/opencode/inih-verify vs inih-ctrl）

- 带 `cxflags="-fvisibility=hidden"`：`libdummy.so` 动态符号表无 `ini_*` 符号 ✓
- 不带该 flag：`libdummy.so` 导出 `ini_parse*` 4 个符号 ✗
- 包缓存验证：`~/.xmake/packages/i/inih/60/6f0a3f82*/manifest.txt` 记录 `cxflags = "-fvisibility=hidden"`，与实际符号隐藏结果一致
- 实测对象：`build/linux/x86_64/release/libxbsa64.so` 当前导出 `ini_parse`/`ini_parse_file`/`ini_parse_stream`/`ini_parse_string`

## 先例

- 本库 `libs/xmake.lua` 中 `timed_net_key` 已用 `set_symbols("hidden")` + `utils.symbols.export_list` 隐藏符号（target 层）。
- 本次为包依赖层（add_requires configs）隐藏第三方库符号。

## 信息缺口

1. 是否仅需 `cxflags`（C 源码）即可，还是需 `cxxflags`？→ inih 含 ini.c（C），INIReader.cpp 可选；`cxflags` 对 C/C++ 均生效，已实验验证
2. 移除别名后是否有命名冲突？→ 全仓 grep 仅 7 处 `inih_static`，无其他 `inih` 依赖，安全
3. 隐藏符号是否影响运行时链接？→ 静态链接进 .so 且符号不出现在动态符号表，仅限内部调用，已验证 dummy 实验可正常 link

## 查重

- PDCA tasks/knowledge 无 inih 符号隐藏重复任务。

## 建议下一步

- P2 grill 确认上表信息缺口 → P3 PRD → P6 终审 → Do 实现（7 处统一修改）
