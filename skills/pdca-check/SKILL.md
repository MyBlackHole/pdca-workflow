---
name: pdca-check
description: 用户明确启动现有 PDCA 任务的 Check 时使用。不修改业务对象或自动返工。
metadata:
  version: 5.0.0-rc.2
---

# Check：AI 直接审查，不用脚本重写 PDCA 规则

## 先定位，不以加载当授权

核对本文件经符号链接解析后的真实路径，定位集中 Git 工作副本 **PDCA_ROOT**。
既有任务绑定优先于 cwd 或环境变量；与入口所在根冲突时停止，不在 TARGET_ROOT 创建另一套规则或 records。

先读[共同恢复入口](../../ontology/contracts/entry-recovery.md)，再读当前绑定项目 context、
自己的 task/原 Agent、最后完整事件和当前请求。当前会话不是该任务执行者时，只路由真实用户操作回原 Agent；
**不可路由就阻断**。**切换 Skill 不换 Agent**。

开始前核对 task/attempt/phase/run/subject 的原始用户回应、最新 Do 产物、固定 Plan/AC/oracle、
撤权状态、资源和实际对象版本。旧 PASS 不能用于新字节。

## AI Review

读取[Check 方法](../../ontology/process/flow-check.md)和当前 scene 方法，按四遍完成：

1. **Scope Review**：Plan 与真实 diff/产物逐项对照，找遗漏和范围膨胀。
2. **Consistency Review**：直接交叉阅读 Skill、authority、Plan、model/mapping、records 和实现，找语义冲突。
3. **Adversarial Review**：假设 Do 结论错误，主动寻找绕过路径、边界条件、stale evidence 和反例。
4. **Evidence Review**：每个重要结论绑定 subject、authority/AC、observation、counterevidence、reasoning、limitation。

找不到反例不自动 PASS；证据不足就是 unknown/not_run。

## 工具只提供事实

允许使用 git、搜索/读取、格式解析器、shell/compiler syntax check，以及 TARGET_ROOT 已有构建/测试/静态分析工具。
它们提供事实证据，不解释 PDCA。

**禁止新增项目专用 semantic validator 来重新编码 PDCA 规则。**
不要用 Python/Shell assert “Skill 数量”“authority 值”“阶段边界”“ontology 加载策略”等；
这些直接由 AI 阅读当前权威判断。若规则本身冲突，报告 UNKNOWN/BLOCKING，而不是修改 validator 让它通过。

## 第二视角

高影响或存在确认偏差时，可以让独立 AI 做一次只读 review pass。
只给 minimum sufficient context，不创建新 PDCA，不轮询、不让 reviewer 修改对象。
其 findings 只是待核验 claim；主 Check 必须继续验证证据与反证。
正式独立 verification 仍需用户显式创建 pdca-verify。

## 报告

Finding 可标为 BLOCKING / NON_BLOCKING / UNKNOWN；最终 verdict 仍使用
[EVIDENCE-01](../../ontology/concept/pdca-evidence.md) 与
[VERDICT-01](../../ontology/concept/pdca-verdict.md) 的既有语义。

保存证据和结论，提出 Act 或新 Do 选项后停止。用户认可不使 fail 变 PASS，Check 不自动返工或进入 Act。
