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
4. **Evidence Review**：每个重要结论绑定 subject、authority/AC、observation、counterevidence、reasoning、limitation。

最终 verdict 继续使用 EVIDENCE-01 / VERDICT-01；证据不足保持 unknown/not_run。

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

CI 只保留低维护成本、与 PDCA 语义无关的机械检查，例如 shell syntax 和 `git diff --check`。
CI 成功不表示 Check PASS。

## 现场验收

[host-acceptance.md](host-acceptance.md) 验证真实宿主发现、Agent 身份/恢复、阶段交互、资源与授权语义。
这些项目仍需真实宿主或人工/AI 现场执行，不能由静态脚本替代。

首个现场实验见 [host-smoke.md](host-smoke.md)：先核验原生能力，再由真实用户逐阶段推进一个 root modeling 任务，
最后从其固定 child seed 核验 fresh Agent 的输入隔离。它是人工操作说明，不是执行器或新增 authority；
缺少宿主能力时保留阻断证据，不改写 H1–H18 的 `NOT_RUN`。
