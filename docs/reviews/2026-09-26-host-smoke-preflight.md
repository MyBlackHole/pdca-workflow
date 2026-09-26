# 最小宿主实验准备与前置阻断记录

日期：2026-09-26。维护基线：`4a9f6b3e0c8a73e8d55a6d599061582815a5401a`（PR #15 合并后）。
AI-assisted: yes。

**本轮交付是实验准备，不是已通过的宿主验收。** 未创建正式 task/Agent/phase/run，
未把本次“开始下一步”改写成实验中的逐阶段用户授权；H1–H18 保持原字节的 NOT_RUN。

## 目标与实际范围

用户要求进入真实宿主最小闭环。先核验当前接入环境，再准备
[操作员实验](../../tests/host-smoke.md)：一个 root modeling 四阶段，加一个已固定 child seed 的创建/输入核验。
正式运行因前置能力不足未开始；没有改用父 Agent 内联模拟。

实际差异仅四份文件：实验说明、tests README 导航、本报告、脱敏本地探测日志。
未修改 Skill、ontology authority、安装器、CI、记录格式或已有任务；未新增 semantic validator、
manifest、adapter、调度器或自动阶段驱动，也未为验收安装额外服务或读取认证材料。

## 已执行的事实采集

[本地探测原始输出](evidence/2026-09-26-host-preflight.txt) 保留命令、stdout/stderr 和退出码。
命令仅查询可执行文件、Git 版本及公开仓库连接情况；没有枚举凭证或输出环境变量。

| 观察 | 证据及解释 |
|---|---|
| Git、shell、Node、npm 可找到 | 本地 command -v 成功；这些不是独立可交互 Agent |
| codex、opencode、claude 不在当前 PATH | 三个 command -v 均退出 1；仅限定本会话环境，不判断用户真实宿主 |
| 本地 Git 无法访问 GitHub | ls-remote 退出 128，错误为无法解析 github.com；先前完整克隆也失败，未得到完整本地检出 |
| GitHub 连接器可读取仓库 | 实际读到 main、PR #15 合并回执、现行 authority 和 tests 清单；连接器不是宿主 Agent 执行器 |
| 没有当前可调用的原生宿主回执 | 可用工具与插件目录检索未提供已连接的 new/communicate/continue 入口；目录中的未连接服务不算已有执行能力 |

本地工具缺失与 DNS 失败不是用户宿主“不兼容”的证据。它们只说明本次环境不能据此启动正式验收。
没有真实创建实参、用户到子实例的消息、恢复回执、原生加载记录或实际资源写权证据；
按 [CAP-01](../../ontology/concept/capability-protocol.md) 停在前置检查，正式宿主结果为 not_run。

## 四遍维护审查

本节是同一 AI 对本次文档差异的维护自审，**不是 H17 已执行，也不是独立第二视角**。

**Scope Review。** 原始目标的“真实运行”尚未完成，已明确列为缺口。可交付范围收敛为可逐步操作的实验，
没有用更多 authority 或脚本替代实际运行，也没有变更 H1–H18 的状态。

**Consistency Review。** 对照基线的 TASK-01、CONFIRM-01、CONTEXT-01、CAP-01 与 flow-check：
root bootstrap 尚无 revision 时不伪造冻结；child 必须来自实际已固定模型；任务创建与阶段启动分开；
恢复核查原绑定/输入/事件/未决操作；child 初始子图、允许调查范围和写域分开。
实验沿用既有记录，不另建 ContextManifest 或 ReviewContract。

**Adversarial Review。** 检查并封堵文档被误用为一键授权脚本、同 ID 冒充恢复、无 canary 输出冒充隔离、
把整份验收剧本传给 child、部分路径成功覆盖整项 H 的表达。保留失败/未知停止点；
原生加载证据不足时必须 unknown，不请求 Agent 自述隐藏上下文来补证。

**Evidence Review。** 本地探测支持“当前执行环境存在能力缺口”，不支持任何真实宿主兼容性结论。
GitHub 读取支持维护基线和现行规则定位，不支持 Agent 执行已发生。实验步骤是待运行说明，
未预填用户确认、会话 ID、模型版本或 PASS；能力探测同样必须由用户明确批准。

## 字节与机械检查

修改的原始 `tests/README.md` 以 Git blob SHA
`34df23696bc2ee21e9399121b71d10980f6e8fff` 核对通过。
在只含已读取原文件的本地临时差异工作树中，四份交付的 `git diff --cached --check` 通过。
该临时工作树不是上游完整克隆；没有声称全库检查、宿主安装或产品测试已经运行。

本轮不修改 `tests/host-acceptance.md`，其基线 blob 为
`fb5bd5d75a054677e496c859035cce603c5b2352`。
CI 如成功也仅表示既有机械检查成功；没有模型遵循率、隔离认证或现场验收的含义。

## 停止点与下一次实际操作

进入实验第 1 节需要一个真正可交互且可采集原生回执的宿主；名称/版本、配置、输入、身份和写权
在现场取得。满足能力要求后，由用户逐步执行 A–H，不把本报告或 PR 合并当成那些阶段的批准。
本次独立第二视角、真实四阶段、child 初始化、长会话/崩溃恢复、资源并发均未运行。
