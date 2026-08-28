# T3993 对话日志

## Plan
- 分类：bugfix（合并提交信息与版本号偏差）。
- PRD：AC-1 libobk=1.0.0.1；AC-2 提交信息首行含 F-139 单号；AC-3 含版本变化明列；AC-4 对比父均仅 +1。
- test seam：`verify_version.sh` -> 仓库根 `xmake.lua` 版本变量。
- final_confirmation 已记录（P6）。

## Do
- 多次编辑 `xmake.lua` 版本变量；amend 合并提交信息。
- 登记证据 ev-* 系列；convergence 映射 valid:true。

## Check
- 多轮修正：① libobk 应 +1 而非恢复父值；② 所有组件应相对父 +1（修正 rpc/dmsbtex/rdbcomm/tls_keygen 超幅跳版）；③ 提交内容应为单需求（F-139），不罗列 T3985/B-3988 子任务标签。
- 经 `git reset --hard fef11220` 恢复 11 个独立提交，按用户最终方向重新 squash 为单提交 `9d1fcc69`，信息仅概括 F-139 单需求实现，版本全部 +1。
- v4 结论 confirmed。

## Act
- 知识沉淀：`knowledge/versioning/squash-single-requirement-version-bump.md`（合并提交版本号+1 与单需求提交信息规范）。
- disposition：projected（已沉淀可复用知识）。
- journal：2026-08-28.md 已追加任务摘要。
- 本地完成，未推送 origin。
