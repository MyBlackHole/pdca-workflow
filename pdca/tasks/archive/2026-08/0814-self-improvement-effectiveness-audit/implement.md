# T0260 执行拆解

本任务保持单一 research PDCA 周期，Do 阶段顺序执行以下工作包：

1. **真实记录总体**：枚举 cutover 后非 fixture 的任务、record、clarifications、transition receipts、conclusion、journal 与失败证据；记录纳入/排除规则。
2. **独立损失参照集**：不读取 flow occurrence 的问题判断，先从真实任务事实提取返工、额外交互、门禁失败/恢复和可用遥测。
3. **记录发现能力**：盘点 occurrence，和独立参照集交叉匹配，报告捕获、漏报、重复/噪声、定位信息与可行动性。
4. **投影与治理链路**：检查 backlog 覆盖/新鲜度，以及 decision、candidate、Improvement Task、post-change observation、effectiveness verdict 的真实产物和引用链。
5. **当前可执行性**：运行现有确定性测试或 fixture，只回答机制当前是否仍可执行，不外推真实 AI 效率。
6. **候选与判定**：按证据门槛筛选和排序候选，填写替代解释、baseline、指标与观察计划；分别判定记录发现能力和完整改进闭环。
7. **证据登记与 Check 输入**：生成机器可复查统计和研究报告，经 `register-evidence` 登记后才推进 Check。

不拆成子 task：上述工作包共用同一总体、参照集和交叉匹配矩阵，拆开会导致各子任务不能独立收敛，并增加证据口径漂移风险。
