# H11 Model → Implement → Verify 现场场景

**状态：场景已定义，尚未执行。** tests/host-acceptance.md 的 H11 保持 NOT_RUN。本文件是操作员步骤和固定 oracle，不是自动化 runner，也不应整份注入 Agent。

## 隔离与入口预检

- fixture 目录为 tests/.pdca-h11-live-<run-id>/，内部至少分为互相独立的 Git 工作副本 pdca-root/ 与 target/、control/ 与测试临时目录。target/ 的 Git top-level 必须解析为 TARGET_ROOT；不得在其中创建 .pdca/。不得复制、读取或写入真实 records/。fixture 位于外层仓库的 tests/ 下时，开始与结束均记录外层 HEAD（`GIT_OPTIONAL_LOCKS=0 git -C <outer-root> rev-parse HEAD`）和 fixture 精确路径的工作树状态；用 `GIT_OPTIONAL_LOCKS=0 git -C <outer-root> status --porcelain=v1 --untracked-files=all --ignored=matching -- <fixture-relative-path>` 区分实际未跟踪/被忽略状态，不根据点号前缀推断，不改外层 ignore 配置，并将 fixture 状态与产品改动区分。证据仍引用 fixture 时不得清理。
- OpenCode 以合成 TARGET_ROOT（fixture 的 target/）作为业务项目根；pdca-root/ 是集中 PDCA Git 根。实际加载的 Skill Base 必须物理来自 pdca-root/，其 Git top-level 必须解析为 pdca-root/。由于 target/ 项目根不会自动加载 pdca-root/opencode.json，OpenCode 实际加载的 user-level instructions 必须明确引用 fixture 的 pdca-root/AGENTS.md；记录并核验该文件的实际来源，不能用真实安装的全局 Skill 或维护仓库根 instructions 冒充。
- 首次绑定前只核对可独立验证的事实：实际加载的物理 Skill Base/entry Git 根解析为 fixture 的 pdca-root/，TARGET_ROOT 解析为 fixture 的 target/，并根据已确认的 project_id 从入口契约推导预期 records_root = pdca-root/records/ 与 ontology_root = pdca-root/ontology/projects/<project_id>/。此时不得把预期值记录成已验证的绑定字段。身份门禁通过后，只读取唯一获准的 fixture binding record，再逐字段比较其 records_root、ontology_root、target_root 与上述预期路径；若不一致，立即停止后续读取并记 unknown。task 尚不存在时不检查 task 固定 pdca_root；task 创建后再核对其固定值与入口 Git 根一致。PDCA_ROOT 未设置时仍从物理 Skill Base 解析入口根；若显式设置，也必须规范化后相等。不得用 cwd、fixture 名称或手工指定 PDCA_ROOT 代替 Skill Base 根解析。
- 如果 OpenCode 实际加载的是仓库外或真实工作副本中的 Skill/instructions、绑定前物理根不一致、fixture-local 来源不可核验，或实际宿主不能把记录写域限定到 fixture，立即停止且不读绑定记录；H11 保持 NOT_RUN，原因记为 unknown。绑定记录读取后的字段不一致时停止任何后续读取。不得通过浏览器登录、下载包、访问真实 records/ 或手工伪造原生回执绕过。
- 使用 tmux 启动本机现有 OpenCode Mini 和已配置模型。记录 OpenCode/模型版本、项目配置、MCP/工具 schema、实际加载的 instructions/Skills 来源、入口根、真实 session ID、原始调用和用户消息来源、对象版本、结果与限制。免费模型限流时可改用本机已列出的其他免费模型；若均不可用，记录服务限流并保持 NOT_RUN，不要求浏览器登录。
- 所有测试进程的 TMPDIR、BUN_TMPDIR、PYTHONPYCACHEPREFIX 指向 fixture 内临时目录。测试命令输出通过当前会话取得；不要在 /tmp 写测试文件、日志、构建产物或缓存。
- 必须由用户在实际对象出现后逐步确认 root modeling seed、DECOMP seed、task 创建和当前 phase。每次只发当前授权，不预批未来 phase；不得伪造 task/session/event/receipt ID。一个场景 attempt 内的 Plan→Do→Check→Act 必须保持同一 Agent；恢复须有原生 continue 证据，不得由父会话代答或用新 Agent 冒充。原始 transcript 仅保存到获准的私有 evidence 位置；未获准导出的 transcript 不复制进仓库。
- 该场景只覆盖一个无状态 formatter node，不覆盖 bounded-counter candidate 的 read() 可观察性问题。该引用是范围排除声明，不授权读取其它 candidate 文件。

## 固定合成需求与 oracle

正式 Model task 前，把下列 source 内容写入 fixture 的 spec/format-count.md，记录相对路径、SHA-256 和显式 environment identity；该文件内容和范围须先展示给用户确认。本文本身不构成用户批准。

1. format_count(n) 对不含布尔值的整数 n ∈ [0,2] 返回精确字符串 count=N，其中 N 是同一输入整数 n 的十进制表示。
2. 对布尔值、非整数（包括 1.5、2.0、"1"）及范围外整数抛出 ValueError；函数无状态，不读写外部资源。

范围只限上述两条 source statement；不得补入持久化、并发、国际化、命令行或其它需求。Model 可以按语义把 source statement 细分为多个 requirement，但每个 requirement 都须回指实际支持它的 source，并标明依据属于直接陈述、语义拆分或推论及其理由。直接陈述必须带可逐字核对的短 source excerpt；语义拆分须列出前提 source 与拆分理由；推论不得冒充 source 明文或独立产品 requirement。不得把未表达该主张的 source 冒充为直接依据，也不得把 provenance、source 区间归属、AC 映射或验证方法等元数据单独计作产品 requirement。若审查发现这些元数据实际指向行为约束（如有效输入范围），须把该约束作为行为义务单独列出并回指原始 source，不能因其出现在元数据中而忽略。实现顺序等建议必须标为推论，不能升级成 requirement 或 AC，除非 source 明确支持。不能把 source statement 数量当作 AC 数量。scope、source closure、requirement classification 或含义存在相关 unknown 时，不得宣告 work-level complete。

本场景固定以下六项验收条件。Model Plan 必须逐项固定，不得省略、合并后降低或另行改写；若发现映射不适用，先停止并报告，不能静默更换 oracle。

| AC | 固定语义 | 必需 CASE 与期望 |
|---|---|---|
| AC-FORMAT | 仅对 0、1、2 返回精确格式 | CASE-VALID-COUNT：依次为 count=0、count=1、count=2 |
| AC-BOOL | True 与 False 均不是本场景接受的整数输入 | CASE-REJECT-BOOL：bool 的两个取值 True、False 均抛出 ValueError |
| AC-NONINTEGER | 非整数值；本场景具体覆盖非整值浮点、整值浮点与字符串 | CASE-REJECT-NONINTEGER：1.5、2.0、"1" 均抛出 ValueError |
| AC-RANGE | 超出 [0,2] 的整数拒绝 | CASE-REJECT-RANGE：-1、3 均抛出 ValueError |
| AC-STATELESS | 相同输入的结果不受先前调用顺序影响，且函数实现不依赖可变外部状态 | CASE-STATELESS-INTERLEAVE：调用 0、1、0、2、1、2，逐次结果分别为 count=0、count=1、count=0、count=2、count=1、count=2；结合对固定函数实现的检查。隐藏且不可观察的状态保留 unknown |
| AC-NO-EXTERNAL-IO | 被测函数调用期间不读写文件、网络、子进程或环境变量 | CASE-NO-EXTERNAL-IO：在导入目标模块后、调用前安装独立 Python 子进程 audit hook；hook 只把文件、socket、subprocess、os.system 事件名追加到内存列表，不写日志文件。只评估目标函数调用窗口中的事件，测试 harness 自身 I/O 不计入该窗口；另用 spy 检查环境访问，并检查固定函数实现未读取或写入外部资源。期望事件为空。测试只能声称覆盖已观测的事件面，无法核验时该 AC 为 unknown |

固定 source-to-AC 主责映射为：source statement 1 → AC-FORMAT；source statement 2 → AC-BOOL、AC-NONINTEGER、AC-RANGE、AC-STATELESS、AC-NO-EXTERNAL-IO。主责映射指定各 AC 的主要义务来源，不禁止记录必要的 supporting source refs：AC-RANGE 的阈值 [0,2] 由 source statement 1 定义，范围外拒绝行为由 source statement 2 规定；AC-BOOL 的直接拒绝义务由 source statement 2 支持，source statement 1 的非布尔有效域是相容的边界上下文。Model 可把 source 拆成更细 requirement，但每个 requirement 都须回指原 source，并映射到至少一个适用 AC；未覆盖的细分义务不能因父 statement covered 而消失。不得把 supporting ref 当成额外 AC 或另一个主责映射。

每条 CASE 逐个输入保留 actual、expected、异常类型/输出、工具与运行环境、subject digest、限制和 counterevidence；case verdict 按其所有输入聚合，任一输入偏离 oracle 即该 CASE fail。AC-NONINTEGER 与 AC-RANGE 的固定输入是代表性 probes，不穷尽 source 的类别级义务。要宣称对应 source requirement 已完整覆盖，Verify 还须把固定 release 代码中的类型/范围判定作为独立 observation，与 source、projection rule 和 mapping 一并核验；无法证明类别级行为时，该 requirement/AC 保留 unknown，不得仅凭样例 CASE 通过外推为完整覆盖。CASE→AC 与 requirement→AC 映射须在 Verify Plan 中固定并由 Check 逐项对账。

CountLabelFormatter 是唯一 work instance，其对应唯一 work node。Model 必须评估 composition/dependency 并在模型中记录“当前单 node 场景无适用邻接 node/接口”的依据 ref；不能把该验证链省略或只写无依据的“不适用”。

## 阶段顺序与停止点

### 1. Model

1. 从 fixture 的 project/workspace 身份进入 $pdca，先完成入口根与写域预检，再绑定唯一合成 target/root。
2. 用户确认唯一 root modeling bootstrap seed 后，按 TASK-01 创建 task。Model task 必须为 fresh Agent；每阶段由用户在实际请求出现后单独启动。
3. Model Plan 固定 source 文件及 digest、环境身份、scope、所有 source requirement、每项 requirement 的实际 source ref/短 excerpt/依据类型/推导理由与 requirement→AC 映射、上述六项 AC/oracle 与固定 source-to-AC 映射、node responsibility、无 composition/dependency 的判断依据，以及本场景不写产品 target 的事实。保存 Plan 的原生 receipt 与内容 digest。
4. Do 只产出 candidate ontology：唯一 model root、definition/work instance、constraints、provenance、coverage、unknown、TREE/NODE candidate；不写 formatter 代码、不创建 child。
5. Check 对账 Plan source set 与 model root 的 source refs/requirement inventory，逐条核对短 excerpt 与原文、确认 source ref 实际支持对应主张且依据类型/推导理由一致，并检查 requirement 清单没有重复计入 provenance 元数据或把推论升级为行为义务。source 引用不实、映射无依据或同一结论内部自相矛盾时，停止并记录相关 unknown，不通过重写分类静默掩盖。完成 ontology semantic closure，并执行四遍 flow-check：Scope Review、Consistency Review、Adversarial Review、Evidence Review。
6. 只有 closure 通过且所有 in-scope requirement 均 covered、相关 unknown 为空时，Act 才固定 ontology revision、root ref、完整 payload digest、tree revision（单 root tree 也须显式固定）、qualified node、requirement coverage、provenance 与 unknown。将 Model Plan 中 source requirement inventory、requirement→AC mapping、六项 AC/oracle 与 source-to-AC mapping 的固定 receipt/digest 回指到该 node 的 qualification/DECOMP 输入；后续 scene 使用同一 ref，不宣称 AC 是 ontology root 中未定义的字段。若宿主不能固定并恢复此 ref，停止并记 unknown。task 创建后另核对其 pdca_root 与入口 Git 根一致。否则记录真实 task/verdict，停止，不进入 Implement。

### 2. Implement

1. 仅从 Model Act 已固定的 ontology revision、tree revision 和 qualified node 形成 DECOMP-01 scene seed。seed 固定 node/work/scene identity、responsibility、I/O、source requirement inventory 与 requirement→AC mapping 的固定 receipt/digest refs、六项 AC/oracle ref、parent/composition/dependency refs 与 initial scope/context anchors。NODE qualification 六项逐一核验：独立 semantic responsibility、可固定 I/O、可定位 relation/constraint 来源、产物可独立拒收、独立验证边界、可说明 parent/sibling composition responsibility；单 node 场景须用 Model Act 的 composition/dependency ref 说明最后一项，而不能略过。用户确认 seed 后，按 TASK-01 → CONTEXT-01 → CAP-01 → CONFIRM-01 → 单次原生 dispatch 创建 Implement task，并保存 task/attempt/assignment/Agent 身份和 receipt。
2. Implement task 使用 fresh Agent。CONTEXT-01 分别固定 initial context、allowed read scope、allowed write scope；本 attempt 的 Plan→Do→Check→Act 保持同一 Agent。Implement Plan 在 Do 前固定 node/revision、AC/oracle ref、mapping baseline、src/count_label.py:format_count、每项 source→target→projection rule→expected verification signal、获准 target write scope、测试文件 tests/test_count_label.py、导入约定与执行命令。verification signal 只定位观察，不替代 observation。
3. 只使用已预装的 Python 3 标准库 unittest，不使用 pytest 或第三方依赖。测试文件固定用 from src.count_label import format_count 导入，命令环境固定 PYTHONPATH=<TARGET_ROOT>。运行前记录 python3 的实际路径和版本；缺失时停止并记录 NOT_RUN，不下载包。测试进程设置 PYTHONDONTWRITEBYTECODE=1，并将 TMPDIR 与 PYTHONPYCACHEPREFIX 指向 fixture 内目录。固定命令为 env PYTHONPATH=<TARGET_ROOT> PYTHONDONTWRITEBYTECODE=1 TMPDIR=<FIXTURE_ROOT>/tmp PYTHONPYCACHEPREFIX=<FIXTURE_ROOT>/pycache python3 -m unittest discover -s <TARGET_ROOT>/tests -p test_count_label.py -v，完整原始结果作为 Implement Check evidence。
4. Do 实现 formatter 和产品测试；每个实现相关语义都有 source → target → projection rule 双向映射。不得修改已固定模型语义；发现模型缺失或错误时停止当前实现并按 EVOLVE-01 报告，不在 Implement/Verify 场景修补模型。
5. Check 对照 baseline 检查 source→target 遗漏与 target→source 无模型依据增项，实际运行产品测试，并执行 Scope、Consistency、Adversarial、Evidence 四遍 review。Act 固定 release digest 与 mapping version；测试或映射未核验则保留 unknown/not_run。

### 3. Verify

1. 从已固定 ontology/tree revision 与 qualified node 按 DECOMP-01/NODE qualification 形成 Verify seed，并逐项核验同一组六项 qualification；单 node 的 parent/sibling composition responsibility 回指 Model Act 的显式结论。seed 带入 Model Plan 中 source requirement inventory、requirement→AC mapping、AC/source-to-AC mapping 的固定 receipt 与 digest。用户单独确认后按 TASK-01 → CONTEXT-01 → CAP-01 → CONFIRM-01 → 单次原生 dispatch 创建 Verify task。使用 fresh Agent；CONTEXT-01 分别固定 initial context、allowed read scope、allowed write scope。task/attempt/assignment、node/revision、responsibility、核心 relation/constraint、source/requirement/AC refs、AC/oracle ref、release digest、mapping version 必须一致且可由原生证据核验。Verify 只读 release subject 与 oracle，不写 release target，也不改变已固定语义。
2. Verify Plan 先固定六项 AC、上表所有 CASE/oracle、Model Plan 的 source requirement inventory、requirement→AC mapping 与 AC digest/ref、实现 digest、mapping version、读写范围和证据 schema；不得替换、降低或遗漏固定 node/seed 的 AC。
3. Do 独立取得 release subject 的 observations；Implement 报告和 signal 只可定位检查，不是 observation。逐项执行六条 CASE，记录每个 AC×CASE×input 的 actual、环境/工具、原始结果、subject digest、限制和反证。
4. Verify Do/Check 逐条给出四条验证链的结论及 refs：requirement→model（固定 source ref、requirement inventory 与 coverage）；model→implementation（mapping baseline 双向检查）；implementation→behavior（release subject 的实际 observations）；composition/dependency（显式核验单 node 无适用邻接接口的模型 ref）。
5. 必须覆盖一条实现反证路径。使用 Verify 内的独立 mutant control（不是第四个 scene），并把它绑定到同一 work/node/revision、AC-BOOL 与 mapping version；它是被审 node 的已知违约实现 subject，不是 release subject。Verify Plan 固定对 release 的只读范围和独立 control 的读取范围；操作员另行获得 fixture control/ 写域授权后，才可在 Verify Do 前创建下列固定内容的 mutant module。Verify Agent 不写 control，也不写 release target。该控制只验证 AC-BOOL 反例检测，不代表 release 实现的变异分数，也不得改变 release verdict。

       def format_count(n):
           if not isinstance(n, int) or not 0 <= n <= 2:
               raise ValueError("n must be an integer from 0 through 2")
           return f"count={n}"

   使用与 release 不同的模块名、绝对路径、独立 Python 子进程与隔离 import path；记录控制源码引用、本次生成的 SHA-256 和实际加载路径。对 True、False 分别留 actual，并分开记录 mutant subject 与检测用例的结果：任一 bool 被接受时，mutant subject 的 AC-BOOL 符合性为 fail、control_detection=detected、detection_check=PASS；若两项都抛出 ValueError，则 control_detection=not_detected、detection_check=FAIL，只说明这两个输入没有观察到 mutant 反例，不得据此给整个 mutant subject 判 PASS，未测 AC 保留 unknown/not_run。所有结果都只能归入 mutant subject，不能并入 release acceptance_results 或 release verdict。
6. Check 执行四遍 review，逐项核对 AC↔CASE↔observation、四条验证链、source coverage、release 与 mutant subject/version 隔离、CASE 聚合规则及所有固定 digest；Act 只终态化当前 Verify task。

## H11 证据与判定

判定前逐项核对以下证据；缺项不得由摘要、自述或另一个 subject 的结果补齐：

- **入口与隔离**：OpenCode/模型/工具版本与配置、实际 loaded Skill/instructions 来源、fixture 入口 Git root、PDCA_ROOT、绑定记录中实际 records/ontology/target 字段及与预期路径的逐项比较、外层 HEAD 与 fixture 精确路径工作树状态的开始/结束快照、项目/workspace/task/node/scene IDs、source 文件 digest、environment identity。
- **三个 scene 各自证据**：seed 与 NODE qualification 的逐项判定、依据和 evidence refs、TASK/CONTEXT/CAP/CONFIRM 固定物、一次 dispatch 的原始参数和 native receipt、Agent/session 身份、Plan 内容、每次 phase_started/phase_completed receipt、同一 attempt 的 continue 依据、Check 四遍结论、Act 对象版本和 verdict。
- **逐项行为证据**：每个 AC×CASE×input 的 expected/actual、工具与环境、原始结果、被测 subject/mapping digest、限制、counterevidence，以及 CASE 和 AC 的聚合结果。
- **跨 scene 与结构结论**：Model Plan 的 source requirement inventory、requirement→AC、AC/source-to-AC 固定 receipt/digest 经 Model Act、qualified node 和 DECOMP seed 到 Implement/Verify 的回指；Model root/tree/node/coverage 到 mapping/release，再到 CASE/observation 的回指；composition/dependency 已评估结论 ref；无关 scene 明确 not_run。
- **mutant control**：同一 work/node/revision/AC/mapping 下的独立 subject、内容/digest、来源、执行隔离、实际加载路径、逐输入 observation 和 counterevidence。预期 control_detection=detected、detection_check=PASS；若实际未检测到反例，记录 control_detection=not_detected、detection_check=FAIL。Mutant subject verdict 不等于 release verdict，也不改变 release delivery status。

结果分开记录 task_execution、subject_conformance、scene_coverage、delivery_usable；按各字段的原生证据分别定值，缺少可定值证据时保留 unknown/not_run。Check 不提前推断 task_execution、scene_coverage 或 delivery_usable；没有获准的 delivery disposition 时，不把符合性结果当作 delivery_usable。

- **release 符合路径**：所有固定 AC 的 release observation 均符合 oracle、三 scene 证据齐全、四条验证链都有结论、跨 scene identity/mapping/evidence 可追溯；这些结果本身不替代 delivery_usable 的独立判定。
- **release 不符合路径**：release 有确定反例时记录对应 release subject 的 subject_conformance=fail，保留原 evidence；不得将其改记为 NOT_RUN，也不得与 mutant fail 混合。正确发现 fail 的 task 仍可有 task_execution=completed，但不满足 release 完成或 work-level complete。
- **mutant 反证路径**：同一固定 work/node/revision 的 mutant control 对 bool 输入产生真实违规 observation，记录 mutant subject 的 AC-BOOL subject_conformance=fail 与 control_detection=detected。该路径满足 H11 的实现反证覆盖要求，但 verdict 只属于独立 control subject，不得合并到 release verdict；若未检出，反证覆盖失败。
- **work-level complete**：固定 source set 已完整对账；所有 in-scope requirement 均 covered；任何 partial、uncovered 或影响 scope/meaning/source/classification 的 unknown 都阻止 complete；source set 边界不明、来源未审或不可读也阻止 complete。排除项须回指 source ref、固定 scope boundary 和理由。声明须回指 Model Plan source set、work root/revision/digest、node 集合、requirement scope/coverage、必需 scene 证据和 composition/dependency 结论；单个 node/task PASS 不足。
- **证据或宿主能力不足**：host acceptance 状态记 NOT_RUN，另列对应事实为 unknown/not_run 及缺失 refs；不得用 NOT_RUN/unknown 混成一个 verdict，也不得宣称 H11 通过。

执行后仅在获准私有 evidence 位置保留所需原始证据；仓库内只放脱敏摘要和必要原生回执引用。fixture 清理前确认私有 evidence 引用可追溯；不得删除或覆盖仍被证据引用的对象。
