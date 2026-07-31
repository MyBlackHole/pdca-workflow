# T0108 执行证据：静态流程与任务图审查

## 检查命令

```text
find . -name AGENTS.md -print
rg -n 'AGENTS|final_confirmation|parent|children|disposition|manifest|archive' README.md flows skills scripts templates knowledge/pdca-flow
find pdca/tasks -name task.json -print0 | xargs -0 jq empty
find pdca/tasks -name task.json -print0 | xargs -0 jq -r '[.id, .meta.phase, (.parent // ""), ((.children // [])|join(","))] | @tsv'
```

## 观察结果

1. 根目录及仓库内没有 `AGENTS.md`；README 和 `scripts/init-external.sh` 都引用该入口约定。
2. T0108 当前为 `meta.phase=do`，`children=[T0109,T0110,T0111,T0112,T0113]`；五个子任务均为 `meta.phase=plan`，双向引用一致。
3. 所有当前 `task.json` 均可解析；`pdca/tasks/archive/2026-07/` 存在历史任务目录。
4. `advance-phase` 的 plan→do 校验只寻找 `source=final_confirmation`，没有检查响应值或方案摘要 digest。
5. `flow-act` 定义 disposition 后迁移目录，但未把 receipt、恢复验证和父子引用校验列为迁移退出条件。

## 证据边界

这是仓库内静态审查证据，不代表尚未执行的 T0109–T0113 子任务已完成，也不代表外部业务仓库实现已被审查。
