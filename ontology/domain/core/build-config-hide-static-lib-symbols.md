---
schema: pdca.asset/v1
id: ontology:domain/build-config-hide-static-lib-symbols
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/build-config-hide-static-lib-symbols/1.0.0
summary: 第三方 C 静态库隐藏 API 符号：覆盖 visibility 宏
domain:
- ontology:domain/build-config
relations:
  specializes:
  - ontology:domain/build-config
  relates_to:
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 领域知识适用场景
  constraint: 见正文
  testable_signal: "运行 grep -q 'hide-static' ontology/domain/build-config-hide-static-lib-symbols.md && python3 scripts/ontology-validate.py --ontology-dir ontology 2>&1 | grep -q 'OK'"
---


# 第三方 C 静态库隐藏 API 符号：覆盖 visibility 宏

## 问题

xmake 项目用 `add_requires` 引入第三方 C 静态库（例：inih）后，共享库 target
（如 libxbsa64.so）静态链接该库时，库的 C API 符号会被导出到动态符号表，造成
API 符号泄漏，可能与其他动态库的同名符号冲突。

## 常见错误做法（无效）

```lua
add_requires("inih 60", {system = false, configs = {shared = false,
    cxflags = "-fvisibility=hidden"}, debug = is_mode("debug")})
```

**无效原因**：`-fvisibility=hidden` 只影响"未显式声明可见性"的符号。若库头文件
含显式可见性宏（如 inih 的 `ini.h`）：

```c
#elif __GNUC__ && !__MINGW32__
#define INI_API __attribute__((visibility("default")))
```

函数声明带 `INI_API` 前缀时显式声明 `visibility("default")`，**凌驾于**编译器
`-fvisibility=hidden`，符号仍为 `GLOBAL DEFAULT`。

## 有效做法

在 cxflags 中同时传递 `-D<MACRO>=` 覆盖宏（置空），使声明回落默认可见性：

```lua
add_requires("inih 60", {system = false, configs = {shared = false,
    cxflags = "-fvisibility=hidden -DINI_API="}, debug = is_mode("debug")})
```

验证（A/B 对照，`readelf` 而非仅 `nm -D`）：

```
仅 -fvisibility=hidden  : ini_parse -> GLOBAL DEFAULT  （泄漏）
加 -DINI_API=           : ini_parse -> GLOBAL HIDDEN    （正确）
```

## 适用边界

- 适用于"静态链接 + 库仅供本 target 内部使用"的场景。
- `-D<MACRO>=` 作用于所有 `#include` 该头文件的编译单元；若库 API 需对外可见
  （公共头 + 动态链接 + 其他模块依赖），不可用。
- Windows DLL import/export（`__declspec(dllexport/import)`）场景不兼容，
  需另行设计。
- debug 模式（`debug = is_mode("debug")`）改变 config hash 触发包重编，
  cxflags 仍生效。

## 实验陷阱提示

- xmake 包目录 `~/.xmake/packages/i/inih/60/<hash>/` 按 config hash 区分。
  实验删除包目录会导致旧产物残留、"假成功"假象。
- 验证需三重交叉：`readelf -s <lib>.a 中的 .o` 看符号绑定（HIDDEN/DEFAULT）、
  `nm -D <lib>.so` 看动态符号表、`xmake build -v` 看链接命令实际引用的包 hash。