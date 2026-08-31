---
schema: pdca.asset/v1
id: ontology:domain/skill-code-review-checklist
name: code-review-checklist
summary: Conduct code reviews, review pull requests, and perform quality assurance.
description: Use when conducting code reviews, reviewing pull requests, or performing quality assurance on C, C++, Rust, Go, or Python code
invocation: manual
type: domain
layer: Knowledge
status: active
relations:
  specializes:
    - ontology:concept/pdca-task
  relates_to:
    - ontology:concept/domain-modeling
    - ontology:concept/triage
  testable_signal: "检查本文件内容完整性，且经 python3 scripts/ontology-validate.py --ontology-dir ontology 校验本节点 attributes 非空且不含泛化短语"

---


---
name: code-review-checklist
description: Use when conducting code reviews, reviewing pull requests, or performing quality assurance on C, C++, Rust, Go, or Python code
---

# Code Review Checklist

## 通用审查维度

**正确性**: 是否覆盖了所有边界条件？错误路径有处理吗？并发安全吗？
**安全性**: 输入有校验吗？SQL 注入/XSS/路径穿越防护？敏感信息不落日志？
**性能**: 有无 N+1 查询？有无不必要的内存分配？热点路径能 benchmark 吗？
**可维护性**: 命名自文档化？函数职责单一？无死代码/调试代码？
**错误处理**: 错误被吞掉了吗？调用方能否区分错误类型？资源正确释放？

## 严重度
- 🔴 **Blocking**: 功能缺失/安全漏洞/数据丢失 — 必须修复
- 🟠 **Warning**: 代码异味/缺少注释/风格不一致 — 建议修复
- 🟢 **Info**: 非功能性建议/可优化项 — 记录即可

## 审查意见格式
```
({severity}) {file}:{line} — {问题说明}

{建议的修改}
```

## 审查前自检
- [ ] 功能完整（对照 prd.md 验收标准）
- [ ] 编译通过，测试通过
- [ ] 无 TODO/FIXME/调试代码
- [ ] 无硬编码密钥/敏感信息

## 已知坑

- checklist 必须逐项过并给出依据；跳过或"通过"无依据的审查无价值。
