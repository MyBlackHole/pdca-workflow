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

## 本地可执行检查

先把 Python 临时目录解析到工作区的现有 `tests/`，若它落在 `/tmp` 就停止：

```sh
set -eu
test_tmp_dir="$(realpath -e "$(git rev-parse --show-toplevel)/tests")"
case "$test_tmp_dir" in
    /tmp|/tmp/*) printf 'Refusing test temp directory under /tmp: %s\n' "$test_tmp_dir" >&2; exit 1 ;;
esac
TMPDIR="$test_tmp_dir" python3 -m unittest discover -s tests -v
```

该命令运行安装器黑盒文件系统测试，以及集中 records 搜索边界测试。安装器测试在隔离 HOME 中调用真实 `install.sh`，并将固定远端地址通过临时 Git 配置重写到本地 fixture；覆盖成功克隆与入口链接、既有集中根拒绝、普通发现目录复用与无关内容保留、路径/名称冲突、Git 缺失、无效 checkout 和失败后的保留/回滚行为。
测试还模拟克隆期间入口冲突、链接调用前出现的同名目录、后续链接失败和 TERM 中断后的回滚，以及发现目录身份替换；确认回滚删除先前由安装器创建的链接、保留并发冲突和被替换的同目标链接。它也拒绝 checkout 中指向外部有效文件的 Skill 目录符号链接，避免不在竞态目录内嵌套写入或跟随不可信路径。
`test_records_search_guard.py` 在 `tests/` 下的合成 fixture 中确认根 `.ignore` 会从 ripgrep 文件枚举和内容搜索中排除根级 `records/`，并保留普通嵌套 `docs/records/`。它不读取真实记录，也不替代 OpenCode Mini 的 H2 现场验收。
`test_opencode_permissions.py` 只核对 `opencode.json` 的 V1 兼容 `permission` 对象是否为两版 CLI 的发现、shell/subagent 工具及 `records/` 相对/绝对递归读写路径配置 `ask`；它检查静态配置，不证明 Mini 的运行时授权行为。
这些断言只检查安装器文件系统效果、ripgrep 忽略规则与宿主配置结构，不检查 PDCA 语义、Skill 规则或 host 交互。

另运行 `sh -n install.sh` 与 `git diff --check`。它们和本地单元测试都不能替代下面的现场验收。

## CI

CI 只保留低维护成本、与 PDCA 语义无关的机械检查，例如 shell syntax、`git diff --check`
以及 Skill bundle 发布/安装元数据的一致性（`VERSION`、catalog version、catalog 所列 Skill 的 metadata.version、
安装器 clone 前必须使用的入口 bootstrap mirror 与 canonical Skill 路径）。
CI 同时运行上述安装器黑盒文件系统测试与合成 records 搜索边界测试；它们不验证 Skill 数量阈值、authority、阶段边界、真实 OpenCode 工具轨迹或其他 PDCA 语义。
这些检查只验证同一发布/安装元数据是否一致或安装器可观察的副作用，不决定 PDCA 规则。
CI 成功不表示 Check PASS。

OpenCode compatibility smoke 的安装、CLI Skill discovery 与基础 server diagnostics 用于宿主兼容性。
它先真实执行生产 `install.sh` 验证默认 clone/链接，再把隔离 HOME 中的临时安装根通过本地 Git bundle
精确切换到当前 workflow checkout HEAD；后续 OpenCode 检查必须断言并读取该 HEAD，不能把安装器重新 clone 的
远端 `main` 当作当前 PR/push 的 Skill 证据。

Public free-model recovery / child-context / continuation / transcript probe 只在其语义输入
（runtime Skills、OpenCode 项目级 instructions/config、PDCA entry load map 与绑定/恢复/场景契约、bounded-counter host-smoke ontology）或 smoke workflow 自身变化时运行。
仅修改 `install.sh` 仍验证真实安装与发现，但不重复执行与该改动无关的模型语义探针；
手工 `workflow_dispatch` 保守运行全套。OpenCode smoke 的期望运行入口直接读取
`skills/catalog.json`，不再维护独立九项名单；同时仍把 catalog 之外意外暴露的 `pdca` / `pdca-*` Skill 视为 discovery 失败。
其中 headless server 与 public free-model 探针为 `continue-on-error` 诊断。Actions Summary 会列出每步的原始 outcome 和 workflow conclusion；job 成功不能单独证明这些探针通过，需结合上传的 JSONL、stderr、解析摘要和尝试日志判断。

## 现场验收

[host-acceptance.md](host-acceptance.md) 验证真实宿主发现、Agent 身份/恢复、阶段交互、资源与授权语义。
这些项目仍需真实宿主或人工/AI 现场执行，不能由静态脚本替代。

首个现场实验见 [host-smoke.md](host-smoke.md)：先核验原生能力，再由真实用户逐阶段推进一个 root modeling 任务，
最后从其固定 child seed 核验 fresh Agent 的输入隔离。它是人工操作说明，不是执行器或新增 authority；
缺少宿主能力时保留阻断证据，不改写 H1–H18 的 `NOT_RUN`。

OpenCode 交互 TUI 如需先补 `communicate` 的真人来源/路由证据，使用
[opencode-interactive-provenance.md](opencode-interactive-provenance.md) 做一次无业务写入的交互 TUI challenge 探针。
该探针按版本区分 v1.18.32 与 v2.0.32 的提交/导出路径，其他版本要先核对对应源码。Challenge 必须由真人在 TUI 中提交；CI、`opencode run`、REST/SDK 或父 Agent/tmux 注入只能做路由模拟，不能证明真人来源。

通过 tmux 启动 OpenCode Mini 做维护级合成探针时，也把临时路径限定在工作区现有 `tests/` 下；OpenCode 默认会把 `tmp` 指向 `/tmp/opencode`。在仓库根运行 `test_tmp_dir="$(realpath -e "$(git rev-parse --show-toplevel)/tests")"`，再执行 `TMPDIR="$test_tmp_dir" BUN_TMPDIR="$test_tmp_dir" opencode debug paths`，确认输出的 `tmp` 为 `$test_tmp_dir/opencode`；然后在 tmux shell 中以同一组环境变量启动 Mini。若宿主版本不尊重这些变量，或确认仍会向 `/tmp` 写测试、临时、日志、构建或缓存文件，不要运行该探针；保留为未运行。
