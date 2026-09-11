> 历史记录：以下是v3.0迁移/验证，不适用于v3.1新字节。当前版本见[v3.1说明](v3.1-MIGRATION.md)与[v3.1验证](v3.1-VALIDATION.md)。

# v3静态检查与参考模型验证报告

日期：2026-09-12。对象：本次PDCA Tree Markdown-native 3.0文件树。

## 结论与限制

实际执行了严格YAML、身份/关系/类实例/图、模板、链接、案例字段与引用检查；另在交付目录外运行独立Python参考模型，对树/调度/结果聚合/返工路径做正反例验证，并核对36条范围案例与9个错误变体。下表只报告这次真正执行的检查。

**没有运行真实多Agent工作流，没有创建真实隔离子Agent，没有生成/使用真实用户确认，没有验证宿主独立消息路由、并发写权、断电恢复或模型指令遵循。68个宿主行为案例均NOT RUN。** 参考模型检查不等于Markdown运行测试，更不等于任意真实实现通过测试。

## 清点

| 项目 | 实测 |
|---|---|
| 文件总数 | 661 |
| Markdown文件 | 660 |
| 本体节点 | 577 |
| 保留上版节点ID | 569 |
| 新增节点 | 8 |
| 关系引用 | 1967 |
| 本地Markdown链接文件目标 | 643 |
| 唯一权威规则 | 20 |
| v3运行模板 | 18 |
| 范围示例完整案例 | 36 |
| 错误实现变体 | 9 |
| 未运行宿主案例 | 68 |
| 静态检查项 | 38 |
| 参考模型规则检查项 | 44 |

无Python/Shell运行文件或平台adapter。保留知识资产schema=pdca.asset/v2，修改规范revision=3.0.0；运行实例/模板为v3。字段完整与草稿合法不代表它可直接进入Do。

## 静态检查实际结果

| 检查 | 结果 |
|---|---|
| 所有Markdown首段YAML严格解析且拒绝重复键 | PASS |
| 节点ID唯一 | PASS |
| 原有569个节点ID完整保留 | PASS |
| 资产模式/受控关系/类实例方向/活动引用 | PASS |
| 继承图无环 | PASS |
| 显式依赖图无环 | PASS |
| 规范化严格部分图无环 | PASS |
| 20个唯一权威规则均指向active normative节点 | PASS |
| 根设计强制树/每节点任务/新Agent/无父审批 | PASS |
| 四条合法转换映射无回退边 | PASS |
| 活动规范与模板无已撤销任务/状态语句 | PASS |
| 本体无失效脚本路径依赖 | PASS |
| 交付无自带运行代码 | PASS |
| Markdown本地链接文件目标存在 | PASS |
| 模板test-suite使用v3并保持草稿 | PASS |
| 模板test-case使用v3并保持草稿 | PASS |
| 模板conformance-review使用v3并保持草稿 | PASS |
| 模板task使用v3并保持草稿 | PASS |
| 模板work-tree使用v3并保持草稿 | PASS |
| 模板work-node使用v3并保持草稿 | PASS |
| 模板baseline使用v3并保持草稿 | PASS |
| 模板response使用v3并保持草稿 | PASS |
| 模板scenario-coverage使用v3并保持草稿 | PASS |
| 模板evidence使用v3并保持草稿 | PASS |
| 模板conclusion使用v3并保持草稿 | PASS |
| 模板delivery使用v3并保持草稿 | PASS |
| 模板dispatch使用v3并保持草稿 | PASS |
| 模板transition使用v3并保持草稿 | PASS |
| 模板rework使用v3并保持草稿 | PASS |
| 模板test-run使用v3并保持草稿 | PASS |
| 模板review-package使用v3并保持草稿 | PASS |
| 模板request使用v3并保持草稿 | PASS |
| 36条案例身份唯一且套件完整 | PASS |
| 每例详细字段/期望/oracle非空 | PASS |
| 全部案例标记教学非实际任务 | PASS |
| 每条约束正反覆盖显式非空 | PASS |
| 每约束覆盖引用真实case | PASS |
| 68个宿主行为案例完整唯一 | PASS |

本地链接检查只验证Markdown正文中相对目标文件存在，不重新验证外部URL、历史源码路径或所有片段锚点；YAML frontmatter单独严格解析，不把其中代码式`a[b](198)`误当文件链接。图验证针对所声明轻量模式，不是OWL形式化推理。没有进行全库领域事实的外部核验。

## 参考模型规则正反例实际结果

这是对本次明确的规则建立的独立小模型：树结构、就绪、slot唯一、祖先失效、同版本全必需聚合、有限返工路径、审查双结果。fixture不提供真实授权；模拟就绪不等于真实并发调度。

| 检查 | 结果 | 观测/注入错误 |
|---|---|---|
| 七节点唯一根组成树被接受 | PASS |  |
| 树反例拒绝-第二父 | PASS | ['parent-count', 'parent-mismatch'] |
| 树反例拒绝-缺失孩子 | PASS | ['missing'] |
| 树反例拒绝-重复节点 | PASS | ['duplicate', 'parent-count'] |
| 树反例拒绝-双根 | PASS | ['parent-mismatch', 'root'] |
| 树反例拒绝-组成环 | PASS | ['cycle', 'parent-count', 'parent-mismatch'] |
| 树反例拒绝-孤立节点 | PASS | ['parent-count', 'parent-mismatch', 'unreachable'] |
| 树反例拒绝-父子不一致 | PASS | ['parent-mismatch'] |
| 树反例拒绝-重复孩子 | PASS | ['duplicate-child', 'parent-count'] |
| 初始仅四叶就绪 | PASS |  |
| A孩子完成不等待B分支 | PASS |  |
| 孩子归档失败不解锁父 | PASS |  |
| 全部直接孩子可用才允许根 | PASS |  |
| 资源预约阻止冲突节点 | PASS |  |
| 首次覆盖21个唯一节点场景任务 | PASS |  |
| 省略组合节点导致覆盖不完整 | PASS |  |
| 同时运行两个attempt被拒绝 | PASS |  |
| 不同节点独立slot允许 | PASS |  |
| B1修改传播到B/R但不波及无关兄弟 | PASS |  |
| 同版本全必需案例允许套件通过 | PASS |  |
| fail不能冒充全套通过 | PASS |  |
| error不能冒充全套通过 | PASS |  |
| blocked不能冒充全套通过 | PASS |  |
| not_run不能冒充全套通过 | PASS |  |
| 空套件拒绝 | PASS |  |
| 遗漏一例拒绝 | PASS |  |
| 重复一例不能充数量 | PASS |  |
| 旧版本PASS拼接拒绝 | PASS |  |
| 未解释flaky阻止通过 | PASS |  |
| 必需约束无覆盖拒绝 | PASS |  |
| 错误变体survived拒绝 | PASS |  |
| 变体构建invalid不能算killed | PASS |  |
| Do预算内同任务修复 | PASS |  |
| Do预算耗尽新attempt | PASS |  |
| check后实现返工新attempt | PASS |  |
| act后实现返工新attempt | PASS |  |
| archive后实现返工新attempt | PASS |  |
| oracle变更不洗白旧失败 | PASS |  |
| 审查任务成功不代表被审对象通过 | PASS |  |
| 全部对象符合且无未知才可发布 | PASS |  |
| unknown阻止完整发布 | PASS |  |
| 参考模型9错误变体均被指定case识别 | PASS |  |
| 对照始终拒绝变体不能通过正例 | PASS |  |
| 重复YAML键反例拒绝 | PASS |  |

## 36条范围案例：返回值参考求值

按node.md的严格类型、数值域、区间和优先级构建纯数值参考函数；expected来自预先固定的独立案例表。以下验证返回allow/code，不验证真实业务函数的外部I/O、真实内存/构建、性能或持久化。cases中的NOT_RUN保留，指真实目标任务尚未执行。

| Case | 输入(N,offset,length) | expected | actual | 结果 |
|---|---|---|---|---|
| RANGE-P01 | `{"N": 16, "offset": 0, "length": 1}` | `{"allow": true, "code": "OK"}` | `{"allow": true, "code": "OK"}` | PASS |
| RANGE-P02 | `{"N": 16, "offset": 0, "length": 16}` | `{"allow": true, "code": "OK"}` | `{"allow": true, "code": "OK"}` | PASS |
| RANGE-P03 | `{"N": 16, "offset": 15, "length": 1}` | `{"allow": true, "code": "OK"}` | `{"allow": true, "code": "OK"}` | PASS |
| RANGE-P04 | `{"N": 16, "offset": 4, "length": 4}` | `{"allow": true, "code": "OK"}` | `{"allow": true, "code": "OK"}` | PASS |
| RANGE-P05 | `{"N": 16, "offset": 4, "length": 12}` | `{"allow": true, "code": "OK"}` | `{"allow": true, "code": "OK"}` | PASS |
| RANGE-P06 | `{"N": 1, "offset": 0, "length": 1}` | `{"allow": true, "code": "OK"}` | `{"allow": true, "code": "OK"}` | PASS |
| RANGE-P07 | `{"N": 18446744073709551615, "offset": 18446744073709551614, "length": 1}` | `{"allow": true, "code": "OK"}` | `{"allow": true, "code": "OK"}` | PASS |
| RANGE-P08 | `{"N": 18446744073709551615, "offset": 0, "length": 18446744073709551615}` | `{"allow": true, "code": "OK"}` | `{"allow": true, "code": "OK"}` | PASS |
| RANGE-P09 | `{"N": 18446744073709551615, "offset": 18446744073709551613, "length": 2}` | `{"allow": true, "code": "OK"}` | `{"allow": true, "code": "OK"}` | PASS |
| RANGE-N01 | `{"N": 16, "offset": 16, "length": 1}` | `{"allow": false, "code": "E_BOUNDS"}` | `{"allow": false, "code": "E_BOUNDS"}` | PASS |
| RANGE-N02 | `{"N": 16, "offset": 17, "length": 1}` | `{"allow": false, "code": "E_BOUNDS"}` | `{"allow": false, "code": "E_BOUNDS"}` | PASS |
| RANGE-N03 | `{"N": 16, "offset": 15, "length": 2}` | `{"allow": false, "code": "E_BOUNDS"}` | `{"allow": false, "code": "E_BOUNDS"}` | PASS |
| RANGE-N04 | `{"N": 16, "offset": 0, "length": 17}` | `{"allow": false, "code": "E_BOUNDS"}` | `{"allow": false, "code": "E_BOUNDS"}` | PASS |
| RANGE-N05 | `{"N": 16, "offset": 4, "length": 13}` | `{"allow": false, "code": "E_BOUNDS"}` | `{"allow": false, "code": "E_BOUNDS"}` | PASS |
| RANGE-N06 | `{"N": 18446744073709551615, "offset": 18446744073709551614, "length": 3}` | `{"allow": false, "code": "E_BOUNDS"}` | `{"allow": false, "code": "E_BOUNDS"}` | PASS |
| RANGE-N07 | `{"N": 16, "offset": 18446744073709551615, "length": 2}` | `{"allow": false, "code": "E_BOUNDS"}` | `{"allow": false, "code": "E_BOUNDS"}` | PASS |
| RANGE-D01 | `{"N": 16, "offset": -1, "length": 1}` | `{"allow": false, "code": "E_DOMAIN"}` | `{"allow": false, "code": "E_DOMAIN"}` | PASS |
| RANGE-D02 | `{"N": 16, "offset": 0, "length": 0}` | `{"allow": false, "code": "E_DOMAIN"}` | `{"allow": false, "code": "E_DOMAIN"}` | PASS |
| RANGE-D03 | `{"N": 16, "offset": 1, "length": -1}` | `{"allow": false, "code": "E_DOMAIN"}` | `{"allow": false, "code": "E_DOMAIN"}` | PASS |
| RANGE-D04 | `{"N": 0, "offset": 0, "length": 1}` | `{"allow": false, "code": "E_DOMAIN"}` | `{"allow": false, "code": "E_DOMAIN"}` | PASS |
| RANGE-D05 | `{"N": -1, "offset": 0, "length": 1}` | `{"allow": false, "code": "E_DOMAIN"}` | `{"allow": false, "code": "E_DOMAIN"}` | PASS |
| RANGE-D06 | `{"N": 18446744073709551616, "offset": 0, "length": 1}` | `{"allow": false, "code": "E_DOMAIN"}` | `{"allow": false, "code": "E_DOMAIN"}` | PASS |
| RANGE-D07 | `{"N": 16, "offset": 18446744073709551616, "length": 1}` | `{"allow": false, "code": "E_DOMAIN"}` | `{"allow": false, "code": "E_DOMAIN"}` | PASS |
| RANGE-D08 | `{"N": 16, "offset": 0, "length": 18446744073709551616}` | `{"allow": false, "code": "E_DOMAIN"}` | `{"allow": false, "code": "E_DOMAIN"}` | PASS |
| RANGE-D09 | `{"N": 0, "offset": -1, "length": 0}` | `{"allow": false, "code": "E_DOMAIN"}` | `{"allow": false, "code": "E_DOMAIN"}` | PASS |
| RANGE-T01 | `{"N": 16, "offset": "0", "length": 1}` | `{"allow": false, "code": "E_TYPE"}` | `{"allow": false, "code": "E_TYPE"}` | PASS |
| RANGE-T02 | `{"N": 16, "offset": 0, "length": 1.0}` | `{"allow": false, "code": "E_TYPE"}` | `{"allow": false, "code": "E_TYPE"}` | PASS |
| RANGE-T03 | `{"N": 16, "offset": true, "length": 1}` | `{"allow": false, "code": "E_TYPE"}` | `{"allow": false, "code": "E_TYPE"}` | PASS |
| RANGE-T04 | `{"N": 16, "offset": 0, "length": false}` | `{"allow": false, "code": "E_TYPE"}` | `{"allow": false, "code": "E_TYPE"}` | PASS |
| RANGE-T05 | `{"N": null, "offset": 0, "length": 1}` | `{"allow": false, "code": "E_TYPE"}` | `{"allow": false, "code": "E_TYPE"}` | PASS |
| RANGE-T06 | `{"N": 16, "offset": null, "length": 1}` | `{"allow": false, "code": "E_TYPE"}` | `{"allow": false, "code": "E_TYPE"}` | PASS |
| RANGE-T07 | `{"N": 16, "offset": 0, "length": null}` | `{"allow": false, "code": "E_TYPE"}` | `{"allow": false, "code": "E_TYPE"}` | PASS |
| RANGE-T08 | `{"N": 16, "offset": [], "length": 1}` | `{"allow": false, "code": "E_TYPE"}` | `{"allow": false, "code": "E_TYPE"}` | PASS |
| RANGE-T09 | `{"N": 0, "offset": "x", "length": 0}` | `{"allow": false, "code": "E_TYPE"}` | `{"allow": false, "code": "E_TYPE"}` | PASS |
| RANGE-T10 | `{"N": true, "offset": 0, "length": 1}` | `{"allow": false, "code": "E_TYPE"}` | `{"allow": false, "code": "E_TYPE"}` | PASS |
| RANGE-T11 | `{"N": 16, "offset": 0, "length": "2"}` | `{"allow": false, "code": "E_TYPE"}` | `{"allow": false, "code": "E_TYPE"}` | PASS |

## 9个错误变体：参考检测结果

在参考函数的隔离变体中注入单一错误，运行预先指定的识别案例。SIDE_EFFECT变体改变本地哨兵，验证本地状态断言能识别返回值以外的错误；它不是对真实工具I/O的安全证明。变体的预期断言失败表示killed，不能将实际编译/测试器错误计为killed。

| 变体 | 识别案例 | actual返回 | 哨兵变化 | 结果 |
|---|---|---|---|---|
| STRICT_END | RANGE-P03 | `{"allow": false, "code": "E_BOUNDS"}` | False | killed |
| MISSING_LOWER | RANGE-D01 | `{"allow": true, "code": "OK"}` | False | killed |
| ZERO_LENGTH | RANGE-D02 | `{"allow": true, "code": "OK"}` | False | killed |
| WRAP_ADD | RANGE-N06 | `{"allow": true, "code": "OK"}` | False | killed |
| COERCE_TYPES | RANGE-T01 | `{"allow": true, "code": "OK"}` | False | killed |
| WRONG_PRIORITY | RANGE-T09 | `{"allow": false, "code": "E_DOMAIN"}` | False | killed |
| ALWAYS_ALLOW | RANGE-N03 | `{"allow": true, "code": "OK"}` | False | killed |
| ALWAYS_DENY | RANGE-P01 | `{"allow": false, "code": "E_BOUNDS"}` | False | killed |
| SIDE_EFFECT | RANGE-P01 | `{"allow": true, "code": "OK"}` | True | killed |

## 复核方法与交付范围

外部临时检查程序递归解析所有Markdown frontmatter（拒绝重复键），建立节点/分类型关系图，读取真实模板和案例清单，剥离frontmatter后解析Markdown链接。模型用实际案例表和七节点tree fixture，注入第二父、环、孤立节点、旧版本PASS、错误结果、超预算等反例并断言预期。原始检查结果已转写以上逐项表。

检查使用容器中的Python、PyYAML、NetworkX与markdown-it-py，程序不放入交付项目，不构成运行依赖或持续CI。后续规则修改需要重新验证，不能继承本报告PASS。

打包与补丁应用后的逐文件校验记录在包外校验清单，避免压缩包/报告摘要自引用。
