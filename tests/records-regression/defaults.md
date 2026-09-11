---
schema: pdca.test-defaults/v1
fixture_only: true
environment: 授权只读包+独立输出目录
observation: 固定输入/方法摘要、实际reason_codes和错误
cleanup: 不改固定包，仅删除临时执行沙箱
---

# 公共设置

这是维护材料检查，不是正式节点任务或真实宿主准入。检查方法只读取subjects中input及其引用。case/expected由外层harness比较，不向被检查方法传入。静态正例表示在合成来源前提下记录关系成立，不表示真实授权。
