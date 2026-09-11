# 真实记录修复回归 · 3.4.6

权威沿用CONTRACT/TEST/CASE/REVIEW/REWORK/VERDICT/ONTOLOGY，不新建Agent或批准机制。本文件固定维护案例范围；实际输入、命令、输出与逐测试结果在独立validation附件。代码不进入本体运行依赖。

## 固定来源与判断边界

原项目包SHA-256：`d71fd23aec4658dd0f0190507d9fd3f44a551c5ad93e8982a34276042e5da71b`。
原records包SHA-256：`8705f1ce8592ce23905bd73e80550ab7c7cbc1fe628f212ec45187064a0ac74b`。

真实输入是两份原包的字节，不是手写“已经发现缺陷”的答案。合成字段/关系控制另标synthetic_fixture，不冒充真实任务；原文摘录比较与合成测试分别计数。准确拒绝错误记录说明维护检查奏效，不说明原业务通过。

| ID | 检查对象与动作 | 必须拒绝/保留未知 | 合法控制 |
|---|---|---|---|
| RR01 | 校验原包、文件清单和补丁基准 | 非该基准、丢文件、源树内容漂移 | 不同tar时间但相同文件内容可作相同内容基准，原包摘要仍分开 |
| RR02 | 资产必填、枚举、关系端点与分类 | 缺authority、非法semantic_kind、悬空/反向关系、继承环 | 类/实例合法、弱关系互引和逆向同一部分事实 |
| RR03 | 从资产核对INDEX与当前发布/字段投影 | 索引漏节点/版本/摘要滞后，即使其文件哈希匹配也拒绝 | 全部逐项一致；历史固定输入不重写 |
| RR04 | 严格frontmatter和正式类型准入 | 缺闭合、重复键、未知schema不得充当正式成功 | 普通附录可保留，但不计正式通过 |
| RR05 | 从独立要求展开case/assertion | 17例计划扩成20例PASS、缺断言清单、同步缩水候选 | 两个case三个具名assertion合法，分别计数 |
| RR06 | 全身份和case语义/摘要核对 | 同ID新语义配旧run、改required、换scene | 同名不同suite可分别合法绑定 |
| RR07 | 观测task/attempt/artifact/checker绑定 | 借用别次观察、Act后新产物沿用旧PASS | 同版本的当前真实观察；fixture只证明绑定关系 |
| RR08 | actual对原始输出与独立oracle | 无raw、把expected复制到actual、raw反驳PASS | actual可与expected同文，但有匹配原始观察 |
| RR09 | 比较真实两份work_pool_metrics_t摘录 | 26与45条成员却称完全一致 | 注释/空白变化不误报；成员顺序/数组长度变化须检出 |
| RR10 | 比较方法与证据范围 | 未支持宏/嵌套语法、无ABI数值，不宣称布局/行为通过 | 符号维度保留标记不求值；明确只比较可支持声明；布局另用真实目标工具 |
| RR11 | 可见输入和保留清单逐成员核验 | 漏artifact/观测/raw、成员摘要不符、另一个run | 非空固定成员，额外具名保留对象允许 |
| RR12 | 错误检查器与oracle能力边界 | always-pass/always-fail、未知oracle、测试器error当killed | 正确检查器接受正例、拒绝负例；mutation单列 |
| RR13 | 需求/方法/实现双向范围 | 删除旧不变量、只看头文件却声称行为全覆盖 | 固定旧要求覆盖不缩水；任意语义仍需独立审查 |
| RR14 | 维护/运行/发布结果分层 | 字段通过、目录、手填completed升级为宿主通过 | finite profile可pass，但overall PDCA incomplete、production false |
| RR15 | 原records与历史fixtures保护 | 倒填身份、确认、时间，覆盖首次失败 | 原字节不动，追加当前integrity-event及新尝试准备 |
| RR16 | 文件工具输入与输出边界 | 逃出授权根、符号链接、输出覆盖输入、错误基准应用补丁 | 只读核验；补丁只应用到新目标目录 |

## 运行与汇总

独立附件的 `verify_all.py` 负责重新解包固定输入、运行自测和原文比较、保存命令/退出码/输出。unit的正负对照不是业务case运行；用预期拒绝判断检查器表现，不把负例返回1算作原业务成功。未知宿主和自然语言语义保持未验收。

## 仍需真实宿主的接续

三场景、完整自主节点Agent、真实Plan/Check确认、资源与未知副作用结清、固定源码的布局/行为测试、独立语义审查均不由本套件认证。先完成一个实体三场景及根加两叶试点；按照既有CAP/CONFIRM/RESOURCE/SCENE记录实际结果，不复制fixture的合成身份。
