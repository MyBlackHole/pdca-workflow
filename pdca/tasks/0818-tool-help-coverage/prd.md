# 补充工具 help 参数说明与使用案例

## 问题与目标

当前多个用户可见工具的 help 内容不完整或风格不一致，用户无法仅凭 help 判断参数含义、默认值、取值限制及完整调用方式。本任务补齐 help，并用自动化回归防止参数表与说明再次脱节。

## 用户故事

- 作为工具使用者，我希望查看 help 就能知道每个已有参数如何使用、默认值是什么、何时与其他参数配合。
- 作为运维人员，我希望看到不破坏系统状态的实际命令案例。
- 作为开发者，我希望参数变更时 help 回归测试能及时发现遗漏。

## 验收标准

- [ ] AC-1: 运行纳入范围内每个工具的 `--help`，输出覆盖参数注册表中的所有已有长选项和短选项，并为每项提供含义、值类型及默认值或取值约束。
- [ ] AC-2: 运行 `tls-keygen` 的全局及 `create`、`ca`、`sign`、`inspect`、`mtls` 子命令 help，输出覆盖各子命令已有参数及其约束。
- [ ] AC-3: 运行各工具的 help 回归测试，结果包含每个工具的参数覆盖断言、案例断言和失败时的明确工具名称/参数信息。
- [ ] AC-4: 每个纳入范围工具的 help 至少提供一个可复制案例；案例明确前置条件，安全检查类案例不启动服务、不覆盖用户文件。
- [ ] AC-5: 不改变已有参数名称、短选项映射、解析行为、业务逻辑或协议；运行 `git diff --check` 通过。
- [ ] AC-6: 运行 `xmake build` 与 `xmake test`，构建成功且全部既有测试与新增 help 回归测试通过。

## 范围确认

初始范围为 `aio-speedd`、`rdbcomm`、`rdbcommd`、`tls-keygen`（含五个子命令）和 `fsdeamon`。若用户排除或增加工具，应在进入 Do 前更新本节和验收标准。

## 实现与测试决策

- 保留现有参数解析结构，集中整理 help 文本，暂不引入元数据驱动重构。
- 以构建后的工具直接执行 `--help` 和子命令 help 作为黑盒回归接缝。
- 案例不要求在测试中真正执行改变系统状态的动作；测试验证案例文本和前置条件说明。

## Seam 分析

### 声明的测试接缝
- seam: `rpc/tests/tool_integration.cpp` -> `aio-speedd`、`rpc` 用户工具 help 输出
- seam: `rdbcomm/tests/tool_integration.c` -> `rdbcomm`、`rdbcommd` 用户工具 help 输出
- seam: `libs/tests/*` -> `tls-keygen` help 与子命令 help 输出
- seam: `fs-backup/fsdeamon` help regression test -> `fsdeamon` 参数 help 输出
- seam: `xmake.lua` test graph -> `xmake build`、`xmake test`

## 范围外

- 不新增命令行参数，不修改参数名称和业务行为。
- 不为内部测试程序、库 API 或配置文件编写用户 CLI help。
- 不在本任务中重构为全自动参数元数据生成系统。
