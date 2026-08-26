# Triage Brief — 0826-oss-go-test-xmake

- **category**: enhancement
- **scenario_type**: development
- **summary**: aio-oss 的 Go 单元测试接入仓库 xmake test 架构，纳入 CI 测试链
- **current behavior**: 仓库已有统一 test 架构（子项目定义测试 target 并 add_tests 汇聚到根 test 目标，CI 执行 xmake --root -y test），多个 C 项目已接入；oss/xmake.lua 仅有 aio-oss binary target，其 Go 单测（go test -mod=vendor ./cmd）只能手动执行
- **desired behavior**: 在 oss/xmake.lua 定义 Go 测试 target 并通过 add_tests 接入根 test 目标；xmake test 时自动运行 go test -mod=vendor ./cmd 并以退出码判定 pass/fail
- **key interfaces**: oss/xmake.lua 测试 target 定义、根构建体系 test 目标汇聚机制、CI test job、Go vendor 模式测试命令
- **acceptance criteria**:
  - 运行 xmake test 时 oss 的 Go 单测被执行且结果计入汇总
  - 人为注入失败用例时 xmake test 对 oss 报 FAIL（非零退出）
  - CI test job 无需改动即覆盖（或说明所需最小改动）
  - 既有 binary target 构建行为不受影响
- **out of scope**: 其他未接入项目的补齐、Go 基准测试/benchmark、跨项目 e2e
- **information gaps**: 无——接入模式可参照既有 C 项目写法与 Go on_build 自定义先例
- **dedup results**: 相关任务为 TLS 集成测试类，无"测试接入构建体系"同概念任务；不重复
- **recommended next steps**: P2 对齐 target 形态后合成 PRD；可与根 test 目标维护者确认 CI 超时预算
