---
schema: pdca.asset/v1
id: ontology:principle/fail-explicit-never-silent
type: principle
layer: Knowledge
status: active
summary: 显式失败禁止静默原则
source_task: T0508
relations:
  specializes: [ontology:principle]
  relates_to:
  - ontology:domain/core-fsck-interactive-error-handling
  - ontology:domain/core-sb-error-persistence-display
  - ontology:domain/core-checksum-negotiation-narrow
attributes:
  - name: applicability
    desc: 错误上报、免校验快路、未知输入处理
    constraint: ""
    testable_signal: 运行 python3 scripts/ontology-validate.py --ontology-dir ontology 确认本节点 attributes 非空且 relations 无空悬；抽查源节点 core-fsck-interactive-error-handling 存在
  - name: violations
    desc: 违反本原则的典型后果
    constraint: ""
    testable_signal: 通读正文违反节，确认每条后果有源节点依据且可在引用代码中有对应实现
---

# 显式失败禁止静默

来源：T0508 提炼；源节点 `core-fsck-interactive-error-handling`、
`core-sb-error-persistence-display`、`core-checksum-negotiation-narrow`；
对照 bcachefs `fs/init/error.c`、`fs/sb/errors.c`、
`fs/data/checksum.h`、`fs/data/read.c`。

## 背景问题

最贵的 bug 不是报错，而是"报对了一半"：错口令返回成功加垃圾密钥，
症状后移为校验错；解压错掩盖校验错，丢掉三次重试；未知错误码被当
成已知处理。每一条都让排查多走数周。

## 约定

1. **未知输入默认拒绝或兜底**：未知特性位拒挂，未知错误码返无效
   占位，绝不误判成功。反例：口令谓词反转致正确口令报错、错误
   口令成功（已修复）。
2. **免校验快路显式分支**：内联空洞零填、裸读分支必须显式标出，
   禁止静默跳过后上报成功。
3. **错误优先级不可掩盖**：解压错永不覆盖校验错；校验好时解压错
   才有意义，保证重试链不断。
4. **饱和计数钳位标记**：达上限后缀标记表地板值，超限钳位不回绕，
   回绕归零会被校验拒掉。
5. **事务错误透传**：重启必须回传令上层重试，其余只打点降级；提问
   必须先解锁加超时，禁止持锁等用户。
6. **降级三守卫加超时**：计数打点入队三连，到期三条件才降级，不成
   则整盘只读；成功清零计时。

## 违反后果

- 掩盖原始错误：重试链断裂，硬错提前，永久标记健康数据为坏。
- 静默跳过校验：损坏数据流入上层，爆发点远离案发点。
- 计数回绕：错误数清零，审计失明。
