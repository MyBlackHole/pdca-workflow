# 在当前项目使用 PDCA

`cross-project.2 + entry-hotfix.1` 的日常入口只需要一个可选环境变量 `PDCA_ROOT`。目标固定为**本次工作入口的真实当前目录**；未设置或空值时，PDCA 根也取该目录。保留纯 Markdown、三场景、完整 PDCA、新 Agent 与既有确认机制，不增加 adapter 或执行器。

## Agent 的下一步：必须交接到流程入口

固定双根后，不要停在这份使用说明。**读取 `PDCA_ROOT/bootstrap/entry-check.md` 并按其读集继续进入 `PDCA_ROOT/ontology/README.md`、权威与阶段入口**，然后核实派发能力与当前确认。外部项目不会因为读到本文就自动加载 PDCA 仓库的 AGENTS.md。

规则和模板按 PDCA_ROOT 定位；Markdown 链接按所属文件定位；新 records 布局按 PDCA_ROOT 定位；源码与命令按 TARGET_ROOT 定位。不要先 cd 到 PDCA_ROOT 来解决相对路径，再将它误当成开发根。入口观察要显示真实双根、已读版本及具体阻断层级，见[读取交接](bootstrap/entry-check.md)。

## 日常用法

在目标项目目录启动具有本入口加载规则的 Agent：

```bash
cd /home/black/projects/backupstream
export PDCA_ROOT=/home/black/projects/pdca-tree
# 在这个环境中启动你的 Agent，然后给出业务目标。
```

不再要求配置 TARGET_ROOT、PROJECT_ID 或 WORKSPACE_ID。也可以在 shell 的个人环境设置中持久配置绝对 PDCA_ROOT；本包不修改用户环境配置。已启动的编辑器/服务能否取得变量由宿主决定，不能把“另一个终端已export”当成本会话已收到。

开发 PDCA 项目自身：

```bash
cd /home/black/projects/pdca-tree
unset PDCA_ROOT
# 在这里启动 Agent；资料放 ./records，开发留在当前项目。
```

等价定位规则（内部推导，不是四个用户参数）：

```text
ENTRY_CWD    := 本次工作开始时读取并固定的真实 cwd
TARGET_ROOT  := ENTRY_CWD
PDCA_ROOT    := resolve(非空环境变量 PDCA_ROOT，相对 ENTRY_CWD)
               或 ENTRY_CWD（未设置/空值）
模式         := 相同根为 shared，不同且不嵌套的根为 split
资料目录     := PDCA_ROOT/records
```

示例：入口为 `/work/app`，PDCA_ROOT=`/work/pdca` → 目标 `/work/app`，资料 `/work/pdca/records`。入口为 `/work/pdca`，变量未设 → 目标 `/work/pdca`，资料 `/work/pdca/records`。

“未设置时取当前”**不是把任意普通项目初始化成 PDCA 项目**。有效根必须包含本包的 `USE-PDCA.md`、`ontology/README.md`、`protocol-release.md` 与所采用契约；缺失、不可读或版本不匹配时阻断 PDCA 接入，不自动 mkdir、复制规则或改用其他路径。非空但拼错的变量也不回退。

## 让 Agent 自动找到入口：一次配置，日常只设变量

环境变量负责定位，不会自行让任意 Agent 读取 Markdown。将[通用入口规则](bootstrap/global-entry.md)的正文放入宿主原生支持、**实际会加载**的个人/全局指令或已安装技能中一次；它不绑定产品，也不复制全部流程。本条实际加载后，**非空 PDCA_ROOT 即启用条件**，之后日常只需上述 cd/export 和业务目标，不必反复说“使用 PDCA”。用户明确拒绝本次使用时不启用。更新 PDCA 仓库后，过去复制的旧全局正文不会自动变化，本次也需替换为新的全局入口。

宿主没有全局入口能力时，给 Agent 这一句即可：

> 使用 PDCA：先取本会话的真实当前目录；读取非空环境变量 PDCA_ROOT 下的 USE-PDCA.md，变量未设置或空时读取当前目录下的 USE-PDCA.md；目标始终是此次入口目录。读完使用说明后，继续读取 PDCA_ROOT/bootstrap/entry-check.md 并进入正式流程，先报告真实路径、已读版本和阻断点。

只有环境变量、但没有全局入口也没有这条指令时，不能声称流程已经自动加载。无法取得真实环境/cwd或两个目录访问能力时，按现有CAP阻断；不得猜测路径、伪造读入结果或将资料写回业务目标兜底。

## 定位一次，整项工作固定

首次启动捕获入口目录和**仅PDCA_ROOT**的原值、来源及规范化结果；不要保存整个环境及其中的密钥。相对PDCA_ROOT只对入口目录解析一次；推荐持久设置绝对路径。不执行eval、不猜测字符串中的`~`/`$HOME`。后续cd、读规则、子进程或新Agent不能改变目标。父派发/恢复使用既有固定context，新任务才重新解析环境。

Git仓库根作为独立身份记录，不自动把目标提升到git toplevel。进入子目录即选择该子目录作为开发范围；需要整仓库时先cd到根目录。若PDCA目录与目标一大一小相互嵌套，则阻断并调整为相同根或独立根，防止扫描与写域混用。

project/workspace标识由已有精确身份绑定复用，或按[PX-ID](ontology/contracts/project-workspace.md#px-id)生成本地确定性标识，不要求用户命名。分支名不作为workspace身份；不同worktree仍单独绑定，共享Git元数据仍按资源规则处理。

## 资料与开发边界

```text
PDCA_ROOT/
  ontology/ templates/                 # 流程规则
  records/projects/<project>/          # workspace绑定与引用索引
  records/works/<work>/                # 工作树、跨节点资料
  records/<task>/
    task.md project-context.md
    tests/ artifacts/                 # 验收、设计、日志、报告、补丁、固定证据
TARGET_ROOT/
  <实际源码、产品测试、批准的构建及产品文档>
```

两个根相同时，以上只是同一仓库的两类写域，不再新建第二棵PDCA目录。`records/`不能作为业务源码写域，也不能把它纳入会递归包含本次输出的源码快照。自维护时可明确批准修改ontology/templates等产品文件，但不能因此修改当前已固定的规则/基线副本、旧确认或历史记录；先保留本次采用版本，变更成为下一版本产物。

两个根不同时，普通业务任务对PDCA共享规则只读，不在目标生成.pdca或复制规则。新设计/报告/日志/流程测试规范在PDCA；源码、产品测试代码及明确要求修改的产品README/API文档在目标。保留已有dirty/untracked文件，不自动reset/clean/stash、提交或切分支。

[绑定模板](templates/project-workspace.md)和[任务上下文](templates/project-task-context.md)由Agent/宿主根据实际观察填入，不是用户额外配置项。所有动作明确cwd及输出路径；正确目录不等于已批准开发、自动获得新Agent或完整PDCA完成。详细规则见[双根契约](ontology/contracts/project-workspace.md)，边界用例见[示例](examples/cross-project/README.md)和[回归](tests/cross-project/suite.md)。

跨项目不能运行时，按[故障定位](examples/cross-project/troubleshooting.md)分别检查入口是否加载、实际进程环境、文件路径、各工具权限与真实流程能力；不要仅凭“配置了变量”宣称已接入。

## 目录接入之后：独立任务与同时在途

通过目录检查后还必须按[dispatch-guide](bootstrap/dispatch-guide.md)调用实际原生派发能力。每个节点场景由自己的新Agent负责完整PDCA；宿主先提交容量内全部兼容就绪任务再等待，不将一个任务待确认扩大为全局暂停。已有派发绑定不重复spawn。沿用唯一PDCA_ROOT设置，资料仍在PDCA，开发仍在固定目标；本更新不需要新的环境变量或adapter。
