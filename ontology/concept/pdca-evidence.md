---
schema: pdca.asset/v2
id: ontology:concept/pdca-evidence
type: concept
semantic_kind: class
layer: Knowledge
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
status: active
authority: normative
revision: 4.0.0-rc.1
dcterms_modified: '2026-09-14'
summary: EVIDENCE-01：对象—执行—观察—判断
---

# EVIDENCE-01：对象—执行—观察—判断

证据记录固定被检查对象、预期AC／oracle、实际输入、执行工具与版本、原始结果位置、退出状态及局限。命令成功不等于业务符合，检测器正确发现违例可表示检测成功而对象失败。

顺序：确认对象及摘要 → 核对执行是否实际发生 → 比较actual/expected → 检查反证／覆盖 → 汇总必需AC。没有run不能补PASS；测试标记为not_run／error／unknown而不是推定失败产品或成功。

问题报告区分确定违例、待核验主张和建议。具体代码／模型位置、可达路径、触发条件、支持及反证应可复核；搜不到名字不证明不存在。未来设计风险与已观察问题分开。

同一最终产物的必需证据集合才能支持交付。产物改变使相关Check和未来Act对象失效；旧run保留不覆盖。用户认可结果不覆盖实际违例或unknown。
