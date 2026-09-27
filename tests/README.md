# AI 审查与现场验收

PDCA 不维护项目专用语义验证脚本。

过去的 Python tests 把“Skill 数量、authority、阶段边界、ontology 加载规则”等 PDCA 语义重新编码成 assert，
会形成第二套规则系统：修改一条规则时需要同时修改 ontology、Skill 和 validator。
当前改为由 AI 在 Check 阶段直接读取唯一权威并验证真实对象与证据。

## AI Check

每次正式 Check 按 [flow-check](../ontology/process/flow-check.md) 完成四遍审查：

1. **Scope Review**：Plan 与真实 diff/产物对照，发现遗漏和范围膨胀；
2. **Consistency Review**：Skill、authority、Plan、model/mapping、records 与实现交叉核对；
3. **Adversarial Review**：主动寻找能够推翻当前结论的反例、绕过路径和 stale evidence；
4. **Evidence Review**：对 decisive claim 按 EVIDENCE-01 绑定当前 subject 的 observation/counterevidence；需要预定义 oracle 时读 CASE-01，需要真实执行时由 TEST-01 保存 observation。

最终 Check 只由 VERDICT-01 聚合 acceptance_results / subject_conformance；task_execution、delivery_usable、scene_coverage 分别来自生命周期、Act 与真实 scene records。证据不足保持 unknown/not_run。

## 工具边界

允许通用工具提供事实，例如：

- `git diff/status/show/log`；
- 文本搜索和文件读取；
- JSON/YAML 等通用格式解析器；
- `sh -n`、编译器语法检查；
- TARGET_ROOT 自己已有的单元、集成、系统测试和静态分析。

禁止新增 `validate_pdca.py`、`check_authority.py`、`test_runtime_surface.py` 一类解释 PDCA 语义的程序。
工具不能决定阶段授权、authority 优先级、ontology 是否可自动采用或最终业务符合性。

## CI

CI 只保留低维护成本、与 PDCA 语义无关的机械检查，例如 shell syntax、`git diff --check`
以及 Skill bundle 发布/安装元数据的一致性（`VERSION`、catalog version、catalog 所列 Skill 的 metadata.version、
安装器 clone 前必须使用的入口 bootstrap mirror 与 canonical Skill 路径）。
这些检查只验证同一发布/安装元数据是否一致，不验证 Skill 数量阈值、authority、阶段边界或其他 PDCA 语义。
CI 成功不表示 Check PASS。

OpenCode compatibility smoke 的安装、CLI Skill discovery 与基础 server diagnostics 用于宿主兼容性。
它先真实执行生产 `install.sh` 验证默认 clone/链接，再把隔离 HOME 中的临时安装根通过本地 Git bundle
精确切换到当前 workflow checkout HEAD；后续 OpenCode 检查必须断言并读取该 HEAD，不能把安装器重新 clone 的
远端 `main` 当作当前 PR/push 的 Skill 证据。

public free-model recovery / child-context / continuation / transcript probe 只在其语义输入
（runtime Skills、bounded-counter host-smoke ontology）或 smoke workflow 自身变化时运行。
仅修改 `install.sh` 仍验证真实安装与发现，但不重复执行与该改动无关的模型语义探针；
手工 `workflow_dispatch` 保守运行全套。OpenCode smoke 的期望运行入口直接读取
`skills/catalog.json`，不再维护独立九项名单；同时仍把 catalog 之外意外暴露的 `pdca` / `pdca-*` Skill 视为 discovery 失败。

## 现场验收

[host-acceptance.md](host-acceptance.md) 验证真实宿主发现、Agent 身份/恢复、阶段交互、资源与授权语义。
这些项目仍需真实宿主或人工/AI 现场执行，不能由静态脚本替代。

首个现场实验见 [host-smoke.md](host-smoke.md)：先核验原生能力，再由真实用户逐阶段推进一个 root modeling 任务，
最后从其固定 child seed 核验 fresh Agent 的输入隔离。它是人工操作说明，不是执行器或新增 authority；
缺少宿主能力时保留阻断证据，不改写 H1–H18 的 `NOT_RUN`。

OpenCode v1.18.32 如需先补 `communicate` 的真人来源/路由证据，使用
[opencode-interactive-provenance.md](opencode-interactive-provenance.md) 做一次无业务写入的交互 TUI challenge 探针。
该探针必须由真人在 TUI 中提交，不能由 CI、`opencode run`、REST/SDK 或父 Agent 模拟。
