# agent-dispatch.1：完整任务与就绪并发

## 基础版本

本增量应用于 `pdca-tree-v3.4.4-cross-project.2-hotfix.1`，精确原包SHA-256为 `8d3a38cd2ec147b493a21843f0ee1521a60c8ac58fc1f8ff12eb84af581aef2a`。protocol_revision仍为3.4.4，修改的权威资产revision升为3.4.5；extension_revisions.agent_dispatch=agent-dispatch.1。版本标识和完整发布摘要共同固定，不冒充宿主发布批准。

## 实施

入口读集新增dispatch-guide和agent-dispatch关联契约；明确宿主派发/已有绑定子Agent两条路径，避免父做Plan、子只做Do及子Agent递归派发自身。根同样完整独立。全流程任务书通过原capability-check与dispatch原生输入摘要关联，原dispatch schema不改。

SCHED新增先提交容量内全部兼容候选再等待、事件到达立即补位、确认仅暂停对应任务、未知创建保留可能占用、索引单写者不形成全局串行等明确义务。容量和授权是硬约束，不强迫所有分支同一时刻启动。

父seed必须先经根的当前ME、完整PDCA和固定局部交付；根不等待后代或整树冻结。草稿不能取得Act/正常归档/确认已消费/可用父输入资格。

跨项目唯一PDCA_ROOT和初始cwd规则不变；每个节点携带固定双根和自己的私有资料区。旧全局hotfix入口会继续读取更新后的entry-check，不要求再添加环境变量或逐项目复制规则。

readiness分开当前ME实际运行、生成的三场景case语义和未来场景not_run；flow-check增加关键顺序在文字/图/案例间的一致性核验。只读研究不升级为代码修改。

## 旧records.tar(5).gz

33份原文保持不变。当前审查缺口是历史事实，不以本补丁补签确认、回填AgentID或替换草稿状态。先核验原宿主未决写者和编号占用；候选可复用但不继承未证明的PASS。合法新根attempt先恢复合格父输入，再按实际容量派发孩子。孩子局部问题不阻断无依赖兄弟。

## 验证边界

新增维护脚本在独立附件，不放进工作流主包。归一化事件重放不是正式记录schema的替代，不认证真实原生工具。临时OS进程探测并发也不是Agent/用户确认试点。真实宿主的新Agent隔离、全流程执行、消息来源、写权及业务语义仍需现场证据；状态NOT_RUN。

原v3.4.4正式/生命周期验证没有新增事件范围，不能将其通过解释为已经验证本扩展。更新入口诊断器同步增加两项显式读集，不省略旧检查。
