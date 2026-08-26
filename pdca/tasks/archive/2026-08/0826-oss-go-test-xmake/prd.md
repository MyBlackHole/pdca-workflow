# aio-oss Go 单测接入 xmake test 架构

## 问题陈述

仓库已有统一测试架构：子项目定义 binary target 并 `add_tests("default", {realtime_output = true})`，`xmake test` 汇聚运行并按退出码判定，CI test_job 执行。aio-oss 是唯一未接入的项目——其 Go 单测（`go test -mod=vendor ./cmd`，11 个用例，含 T3970 新增开关用例）只能手动执行，CI 无法感知其回归。

需求：将 Go 单测纳入 xmake test 架构，使其进入统一测试汇总与（未来的）CI 门禁。

## 方案概述

经 POC 验证（本地全量 44 条 passed 含新条目；失败注入可见）：采用 **`go test -c` 编译测试二进制 + 标准 add_tests** 方案——与 C 项目模型零差异。

`oss/xmake.lua` 追加：

```lua
target("aio-oss-go-test")
    set_default(false)
    set_kind("binary")
    on_build(function (target)
        local oss_dir = path.join(os.projectdir(), "oss")
        local out = path.join(os.projectdir(), target:targetfile())
        os.mkdir(path.directory(out))
        os.vrunv("go", {"test", "-c", "-mod=vendor", "-o", out, "./cmd"}, {curdir = oss_dir})
    end)
    add_tests("default", {realtime_output = true})
```

关键点：
- `set_default(false)`：不参与默认构建（`xmake -y` 不编译测试二进制）
- `go test -c` 编译 cmd 包测试为独立可执行文件，退出码即通过/失败语义，天然匹配 xmake test 判定
- 过滤语法：`xmake test --root -y "aio-oss-go-test/default"`

配套产出：新建验收脚本 `oss/test/xmake_go_test.sh`（构建 target → 过滤运行 → 校验 passed 与退出码）。

## 用户故事

1. 作为开发者，运行 `xmake test` 一次看到全部项目（含 aio-oss Go 用例）的通过情况与统一汇总。
2. 作为开发者，单独过滤运行 Go 测试条目快速回归 oss 改动。
3. 作为 CI 维护者，未来 test_job 无需为 Go 项目增加任何特判。

## 实现决策

| 决策点 | 结论 | 理由 |
|--------|------|------|
| 接入形态 | go test -c 编译 runner + add_tests | 与既有 C 测试模型完全一致，无 xmake 特判 |
| 测试范围 | 仅 ./cmd 包（当前唯一含测试包） | 多包演进时按包追加 target，避免过度设计 |
| 默认构建影响 | set_default(false) 隔离 | 测试产物不进发布链路 |
| CI 语法问题 | 本任务不动 .gitlab-ci.yml（用户裁决） | 另行登记：现有 `xmake --root -y test` 参数顺序错误（test 被当作 target 名），正确应为 `xmake test --root -y` |
| 验收脚本 | 新建 oss/test/xmake_go_test.sh（用户裁决） | 与构建回归解耦 |

## 测试决策

以 xmake test 实际运行为主验证（正向 + 失败注入）；build_oss.sh 回归确保默认构建不受影响；go test 直跑通道保留验证一致性。

## 范围外

- .gitlab-ci.yml 任何改动（含已知参数顺序错误修复）
- 其他未接入项目的补齐
- go benchmark / 多包测试 target 演进
- 测试覆盖率统计接入

## Seam 分析

### 声明的测试接缝

- seam: oss/test/xmake_go_test.sh -> oss/xmake.lua
- seam: oss/test/build_oss.sh -> oss/xmake.lua

## 备注

- 发现项留痕：CI test_job 命令 `xmake --root -y test` 参数顺序错误（本机 v3.1.0 下 test 被当作 build target 名，exit=255），需单独任务修正后 CI 测试链才真正生效。
- POC 数据：全量 44 条 passed（含 aio-oss-go-test/default 0.067s）；注入失败用例后该条目 failed 且汇总 0% passed。

## 验收标准

- [ ] AC-1: 运行 `xmake test --root -y` 全量测试，输出含 `aio-oss-go-test/default ... passed` 且汇总计数包含该条目
- [ ] AC-2: 注入临时失败用例后运行 `xmake test --root -y "aio-oss-go-test/default"`，该条目报 failed 且命令非零退出；移除注入后恢复 passed（失败可见性）
- [ ] AC-3: 新建 `oss/test/xmake_go_test.sh` 执行结果 RESULT ALL PASS
- [ ] AC-4: 默认构建行为不变：`xmake build aio-oss` 成功且 build_oss.sh 回归 ALL PASS（测试 target 不参与默认构建）
- [ ] AC-5: 直跑通道一致：`cd oss && go test -mod=vendor ./cmd` 全绿
