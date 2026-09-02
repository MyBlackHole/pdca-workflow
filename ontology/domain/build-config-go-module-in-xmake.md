---
schema: pdca.asset/v1
id: ontology:domain/build-config-go-module-in-xmake
type: domain
layer: Knowledge
status: active
summary: 多包 Go Module 接入 xmake 构建体系
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
  testable_signal: "运行 grep -q 'go-module' ontology/domain/build-config-go-module-in-xmake.md && python3 scripts/ontology-validate.py --ontology-dir ontology 2>&1 | grep -q 'OK'"
---


# 多包 Go Module 接入 xmake 构建体系

## 结论

xmake 的 Go 工具链（`core/tools/go.lua`）以文件列表方式调用 `go build -o <target> <files>`，
要求所有文件位于同一目录同一 package。**多包 Go module（如 `module oss` + `oss/cmd` 子包 + vendor）
无法用 `add_files("**/*.go")` 直接构建**，报错：
`named files must all be in one directory`。正确做法是自定义 `on_build`，在 module 目录内执行
`go build -mod=vendor -o <绝对路径> .`。

## 可复用模式

```lua
local _version = oss_version  -- 定义阶段捕获全局变量（on_build 沙箱内全局不可见）

target("oss")
    set_kind("binary")
    set_basename("aio-oss")
    set_prefixdir("aio-oss/" .. arch, {bindir = ""})
    on_build(function (target)
        local module_dir = path.join(os.projectdir(), "oss")
        local out = path.join(os.projectdir(), target:targetfile())
        os.mkdir(path.directory(out))
        local argv = {"build", "-mod=vendor"}
        if is_mode("debug") then
            table.insert(argv, "2", "-gcflags=-N")
        end
        table.insert(argv, "-ldflags")
        table.insert(argv, "-X oss/cmd.version=" .. _version)
        table.insert(argv, "-o")
        table.insert(argv, out)
        table.insert(argv, ".")
        os.vrunv("go", argv, {curdir = module_dir})
    end)
    version_name = "aio-oss.version"
    add_configfiles("version.in", {filename = version_name})
    add_installfiles("$(builddir)/" .. version_name)
end)
```

## 关键陷阱

| 陷阱 | 现象 | 对策 |
|------|------|------|
| `target:targetfile()` 返回**相对 projectdir** 路径 | `os.vrunv` 在 `{curdir = module_dir}` 下执行时，相对路径输出被写入 module 子目录（如 `oss/build/...`） | 必须 `path.join(os.projectdir(), target:targetfile())` 转绝对路径 |
| 全局变量在 `on_build` 沙箱内不可见 | `os.vrunv` 报 `attempt to concatenate a nil value (global 'oss_version')` | 在 `target()` 定义前用 `local _v = oss_version` 捕获 |
| 产物名设置 API | `set_targetname()` 不存在 | 使用 `set_basename("aio-oss")` |
| 版本注入目标变量 | 需替换源码硬编码 | Go 侧定义 `var version = "1.0.0"`，`-ldflags "-X pkg.version=<v>"` 注入（支持未导出变量） |
| 版本文件位置 | `add_configfiles` 生成的版本文件位于 `$(builddir)`（**build/ 根**），非 targetdir | 引用/清理时用 `$(builddir)/<name>`，勿用 `target:targetdir()` |
| debug 优化标记 | 自定义 on_build 不继承 xmake 原生 go 工具的 `-gcflags=-N` | 手动 `is_mode("debug")` 时插入 |

## 版本体系接入（对齐 xbsa 先例 commit 25d5742d）

1. 根 xmake.lua：`oss_version = "1.0.0.0"` + `set_configvar("OSS_VERSION", oss_version)` + `includes("oss")`
2. version.h.in 加 `#define OSS_VERSION "${OSS_VERSION}"`
3. version.log.in 加 `aio-oss "${OSS_VERSION}"`
4. 目标内 `add_configfiles("version.in", ...)` 生成 `.version` 文件并 `add_installfiles`

## 危险警示

**不要在自定义 target 中定义 `on_clean` 使用 `os.rm` 删除产物**：`xmake clean <target>`
会清除配置，此时 `target:targetfile()` 可能返回空值，`path.join(projectdir, "")` 会得到
projectdir 本身，`os.rm` 将递归删除整个工作区目录。已验证可导致 git worktree 整个丢失。
如需清理，交给 xmake 默认行为或使用绝对路径 + 判空守卫。

## 适用范围

- 验证环境：linux x86_64，Go 1.26.5，xmake 3.1.0。
- arch 变量已抽象（x86_64/aarch64），交叉编译未实测。
- 保留 module 独立构建能力：`cd oss && go build -mod=vendor .` 仍可用。
