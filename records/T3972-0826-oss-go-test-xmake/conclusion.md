---
schema: pdca.asset/v1
id: T3972-0826-oss-go-test-xmake
phase: check
source_ids: [xmake-go-script, xmake-test-full, build-default, build-regression-t3972, go-test-direct, convergence-map]
---

## 上下文

仓库统一测试架构（add_tests + xmake test 汇总 + CI test_job）中 aio-oss 是唯一缺席项目，Go 单测无法进入 CI 门禁视野。T3972 以 go test -c 编译 runner 方案完成接入。提交 ba187ae5。

## 假设与结果

- 假设 1：go test -c 编译的测试二进制可作为普通可执行挂入 add_tests 模型 → 成立，与 C 项目零差异（POC + 正式实现双重验证）。
- 假设 2：set_default(false) 足以隔离默认构建 → 成立，build_oss.sh ALL PASS 且产物链路无变化。
- 假设 3：失败用例能通过退出码传播为条目 failed → 成立，注入验证 exit=255 且汇总 0% passed。

## 分析

- **AC-1** ✅ 全量 `xmake test --root -y` 输出含 `aio-oss-go-test/default ... passed 0.062s`，汇总 `100% tests passed, 0 failed out of 44` 计入该条目（xmake-test-full）
- **AC-2** ✅ 注入失败用例后过滤运行报 failed、命令非零退出(exit=255)，移除后恢复 passed（xmake-go-script）
- **AC-3** ✅ 新建 oss/test/xmake_go_test.sh 三步校验 RESULT ALL PASS（xmake-go-script）
- **AC-4** ✅ 默认构建不受影响：xmake build aio-oss 成功、build_oss.sh 回归 ALL PASS（build-default / build-regression-t3972）
- **AC-5** ✅ 直跑通道一致：cd oss && go test -mod=vendor ./cmd 全绿（go-test-direct）

## 适用边界

- 仅覆盖 oss/cmd 单包；oss 未来新增测试包需按包追加 target（PRD 实现决策已声明）
- 过滤语法与输出格式依赖 xmake v3.1 行为，跨大版本升级时 xmake_go_test.sh 的 grep 契约可能需要跟进
- 本任务不修 CI：test_job 现有命令 `xmake --root -y test` 参数顺序错误导致 test 子命令从未真正生效，CI 门禁实际生效依赖该修复（已单独留痕）

## 下一轮建议

- 新任务：修正 .gitlab-ci.yml test_job 命令为 `xmake test --root -y` 并在 MR 流水线观察首轮真实执行结果
- T0259 历史 Pending 任务清理仍待办

## verdict

{"outcome": "confirmed", "reason": "五条 AC 证据齐备（全量汇总含新条目、失败可见性双向验证、默认构建隔离、直跑一致），收敛 valid=True，双轴审查 Blocking=0", "verdict_id": "T3972-0826-oss-go-test-xmake-check", "at": "2026-08-26T11:31:30+08:00"}
