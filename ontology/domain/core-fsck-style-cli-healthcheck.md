---
schema: pdca.asset/v1
id: ontology:domain/core-fsck-style-cli-healthcheck
type: domain
layer: Knowledge
status: active
summary: fsck 风格 CLI 健康检查入口模式
domain:
- ontology:domain/core
relations:
  specializes:
  - ontology:domain/core
  relates_to:
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 领域知识适用场景
  constraint: 见正文
  testable_signal: 由领域实践与测试验证
---

# fsck 风格 CLI 健康检查入口模式

## 适用场景

把库级一致性校验 API 暴露为命令行健康检查工具：脚本可调、退出码可判、
输出可解析。上游锚点：bcachefs `fsck` 命令（src/commands/fsck.rs:419-447
打开设备→全量 pass→首错即停→eprintf→exit(ret)）。

## 模式要点

1. **lib 核心 + bin 薄壳**：核心逻辑（打开+校验）放库函数（如
   `fsck_image`），bin 只做参数解析与退出码映射——库级单元测试可构造
   失败态直接测核心，bin 集成测试用 `CARGO_BIN_EXE_<name>` 跑真实二进制
   验证进程级退出码与输出。

2. **退出码分层**：0=通过 / 1=校验失败（输出具体错误变体名）/
   2=打开-IO 错误（输出 IO 错误名）。对齐上游 `exit(ret)` 非零退出语义，
   但区分失败类型利于脚本诊断。

3. **仅 no-repair 模式**：引擎无修复路径时，CLI 天然对齐上游
   `-n/--no_repair`（fsck.rs:266-269 `fix_errors=no`）；接受
   `-n/--no-repair`、`-f/--force` 参数表但无需实现修复。

4. **零依赖手写解析**：参数表很小（两个布尔 + 一个路径）时手写解析，
   与库的零依赖约束一致；用法输出到 stderr 且退出非 0，帮助 `-h` 走
   退出 0。

## 关键架构事实（打开即重建）

**open_persistent 打开路径总会执行 rebuild_derived_state**（恢复语义），
预置的索引不一致会被打开流程修复。因此 CLI 面对"损坏文件"的体现是
打开失败（Io 错误名 + exit 2），而不是校验失败；索引不一致校验失败路径
由库级 verify_all 测试覆盖（错误变体名）。验收口径必须区分这两种
"损坏"：不可打开 = CLI 层，索引不一致 = 库层。

## 测试模式

- lib 单测：健康临时文件 Ok；不可读/缺失文件 Err Io。
- 集成测试：健康引擎 exit 0 + stdout "OK"；垃圾/截断文件 exit 2 +
  stderr "cannot open" + 错误名；缺失文件 exit 2；临时文件唯一命名
  （pid+线程名）并清理。
