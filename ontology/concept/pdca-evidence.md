---
schema: pdca.asset/v2
id: ontology:concept/pdca-evidence
type: concept
semantic_kind: class
layer: Knowledge
status: active
authority: normative
revision: 3.4.9
summary: 证据、测试运行与不可变版本
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: '2026-09-13'
relations:
  specializes:
  - ontology:concept/entity
  relates_to:
  - ontology:concept/pdca-acceptance-criterion
  - ontology:concept/external-evidence-collection
  - ontology:concept/task-unit-test
  - ontology:concept/task-rework
  - ontology:entity/evidence-test-result
  - ontology:entity/evidence-review
  - ontology:entity/evidence-convergence-map
---

# 证据、测试运行与不可变版本

## EVIDENCE-01：登记真实观测

`evidence.md` 是当前任务的证据索引；原始产物保存在任务 `artifacts/` 或契约授权的目标位置。每条证据有 task_id、唯一 evidence_id、evidence_type_ref、来源/实际执行动作、产物相对路径或固定版本、真实内容摘要、结果和关联 AC。

允许的类型由 `evidence-*` 节点对本概念的 specializes 声明，本版含 `test-result`、`review`、`convergence-map`。工具日志保存实际命令/参数的安全摘要、工作目录、退出状态和原始输出；不得伪造执行或补写假时间。不在证据内泄露密钥。

摘要由真实工具计算。摘要只能用于核对内容是否一致，不证明作者身份、真实时间或事实本身；没有可信宿主签名时不得称其不可篡改。

## 路径与来源

路径不能通过 `..`、绝对路径混用或符号链接逃出授权范围。外部材料先按 `external-evidence-collection` 导入当前任务固定副本；原路径、来源版本与副本摘要都保留。无权限读的输入不通过复制绕过。

不得读取其他任务活动上下文。明确导入的依赖产物仍需在本任务验证版本、适用条件及与 AC 的关联，不继承其“通过”结论。

## 覆盖与真实性分开

验收映射对每个 AC 指向证据或明确失败/unknown/not_run说明。`convergence-map` 是映射本身，不能用自己证明自己。Do→Check 要求可判定的完整记录，不要求每个业务 AC 已经 pass。

更正证据必须新建版本并引用被替代项，保留原始观测。已提交独立审查/confirmation 的证据变更会使旧包摘要失效，必须重新核验并按场景重新审查；不能只更新清单而保留旧通过回执。

门禁使用证据时重新读取对应字节核对摘要；不能只相信索引中的摘要字符串。只读路径指针失效或内容漂移时，停止依赖该证据并报告。


## 冻结包与可变工作记录

`task.md`、`evidence.md`、`conclusion.md`是当前工作视图，不是历史确认的稳定字节对象。提交门禁前，按下列规则生成任务内不可变审查包：

- Do结果固定和Check确认分别使用 `artifacts/reviews/<review-id>/`。包清单列出 task_id、baseline_digest、阶段、AC映射、产物/证据/结论的固定版本位置和真实摘要。
- 先固定叶子对象，再生成清单并计算清单摘要。请求的subject_ref指向清单，subject_digest是该清单实际字节摘要；确认回执/独立审查报告和后续转换回执不属于它确认的清单，避免循环摘要。
- 固定位置可以是任务内副本或可重新读取的不可变版本；只有不断变化的项目工作路径不算固定位置。首次冻结时必须核对真实产物与快照一致，不能用无关副本替换实际结果。
- 请求发出后不覆盖包；变更生成新的review-id和请求，旧包/响应保留并标记被替代。提交前还应核对仍作为交付对象的工作产物未发生未经审查的漂移。
- Check→Act后可以在工作版conclusion.md追加处置，并引用已确认包。历史回执验证固定包，而不是重算已追加字段的工作版摘要；改变原判定或已交付成果并非普通追加，必须显式处置。

基线同样不可变；门禁回执inputs只能引用本次实际冻结的输入，不能指向之后会覆写的状态镜像。恢复时发现固定包字节变化必须阻断，不能把合法工作记录追加误判成固定包损坏。


## 任务单元测试证据

每次run绑定work/tree/node/scene/attempt、suite/case/fixture/实现及孩子版本，记录实际环境/调用、expected/actual、断言结果、清理、原始输出和真实摘要。TEST-01规定结果类型；不能用测试程序error当非法输入被正确拒绝。

Do内修复保留旧失败run，当前产物改变后旧PASS仅适用于旧版本。REWORK-01要求最终版本全必需回归并传播stale；实际证据和教学fixture分目录、分身份、分用途。不能把examples中的期望结果复制为生产actual。

## 证据保留与集合快照

临时路径不是归档证据；先保存原始输入、错误样本、checker版本和完整观测，核对固定副本摘要，再清理执行目录。清理证明不得把证据删除。无法取得的历史原文明确unavailable，不能从新版本反造旧版本。相同路径+不同revision标签仍需可分别读取的旧/新字节。

复合输入使用逐成员清单，路径/用途/来源版本/摘要和必须性明确；图检查绑定其实际图摘要。核查集合应检查成员集合相等、引用全部可解析、字节一致，不只看外层哈希。固定快照可在授权对象内保存或按明确许可导入，不泄露凭据。

维护复核的observed_at与历史执行时间分离；后来算出的摘要不具有历史时间证明力。向旧任务追加问题只能使用独立完整性事件，不能补签消息或覆盖原结果。


## 引用核验与事实分类

非空ref、形式正确的digest和真实字节匹配是三个不同层次。逐引用核对固定对象的可解析位置、真实摘要、schema/角色和适用task/work/tree/node/scene/attempt/run；类型也是身份，true不等于attempt=1，缺失值彼此相等不建立绑定。具名对象或跨根材料须有明确映射及读权限；未支持解析的引用列为incomplete，不当作已闭合。必要引用及成员集合来自固定要求，不能让被审清单自己决定分母。

来源真实、结果正确、证据充分分别登记。缺项时保留“未随本包取得”的范围，先查原宿主或导出链；不以补写新时间、摘要、确认或Agent ID恢复旧结论。对旧记录新增审查裁决与本次观察，保留原件；确定误判可被纠正，但不能把整批记录重新归为模拟材料。

<a id="evidence-consumption"></a>
## 消费证据：从原始结果走到当前判定

进入Check或采用依赖交付时，按固定要求集逐项执行下表；用既有AC映射、conclusion或审查报告记下结果，不另建证据类型。提供者的摘要与“已验证”说明是待核验主张。

| 核验顺序 | 实际动作 | 不成立时 |
|---|---|---|
| 对象 | 比较预期与实际的task/attempt、artifact、suite及输入版本，读取固定成员字节 | 旧PASS只适用旧对象；缺字节保留unknown/unavailable，不猜not_run |
| 执行 | 读真实命令/环境、退出状态、原始输出和断言，确认方法覆盖当前主张 | error不能当正确拒绝；明确未执行才记not_run |
| 含义 | 把actual与独立oracle对照，区分检测器运行正常和被审对象符合 | 工具成功发现违例时，对象仍fail，不能因进程成功改成pass |
| 汇总 | 将每项结果回链到最终结论，检查遗漏、矛盾和受影响范围 | 必需缺口或stale不能被比例、模板默认值或其他通过项覆盖 |

最小消费行：`AC/主张 → 预期对象 → 实读对象和证据 → actual/判据 → 采用或拒用理由 → 对当前结论的影响`。映射必须引用原始观察，不把映射本身当第二份证据。

例：测试成功发现字段数量不符，进程exit=0仅证明检测器正常返回；精确字段声明仍不符合。反过来，测试器因环境异常退出，不证明它正确拒绝了恶意输入。审查任务质量与对象符合性继续按VERDICT-01分别判定。
