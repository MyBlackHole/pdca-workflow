---
schema: pdca.record-shape-index/v1
authority: CONTRACT-01
protocol_revision: 3.4.11
profile: fixed_formal_record_example
records:
  task:
    ref: task.md
    digest: b2f46ba694f0f288715bf043447d03d99d5b1e087590ce414968693e0eea3474
  baseline:
    ref: baseline.md
    digest: 034ce6798c1855a8112213ca9d9b00c49bec8691e0e18d346fb2a9722f629c22
  request:
    ref: request.md
    digest: bcafc055e891eac0fc16dd71f31f75d37beab1c88052eb4e8b37dd7bb465436a
  response:
    ref: response.md
    digest: 0a241ce5dc35f4ef3ca6b3be724daa9303b85903ff2991a1a852b45716bfe164
  request-decision:
    ref: request-decision.md
    digest: cc18294dac45233d11336b2260f8b0e723b34bfdc1c0338c0b295634fda6aaae
  transition:
    ref: transition.md
    digest: ec48d1fa50cb0874865c9d6f88ede62f2c4f49571e77a2ace6548249ad569782
  test-suite:
    ref: test-suite.md
    digest: 0fb039ba4b3dfd1ba2521346c909bc28afbc993817f390cb194a67fdbe5bd7dc
  test-case:
    ref: test-case.md
    digest: 788c8b2d0ad1ea006f8a286cde838d0a1cce40ad72d4e9a6f5d37a208a31e66f
  test-case-binding:
    ref: test-case-binding.md
    digest: ab0cd78e8e1726774fc5df68ed45b550f91af69a2973f6ab3df316ca9ac9bc06
  test-run:
    ref: test-run.md
    digest: 043f179ce6a248fb599b37e1fe7e03e3f8b4fc144729f8a8c96b401108ea3492
  review-package:
    ref: review-package.md
    digest: bc1b1d848c1ce4a27965de33851532e0ca3d80d7e3a7595e18dcadb5d1ce5268
  delivery:
    ref: delivery.md
    digest: 2bac635a9deff3fc18435a0049eb31c3eefc16a1f86b86c2b48d73f31bc3325c
  archive-receipt:
    ref: archive-receipt.md
    digest: 38d659178b57bf8758499f5ae06b3867180ec61d56836cc2ef63078b3b3c88d9
  work-node:
    ref: work-node.md
    digest: b5899a58f698035cd84c147be8c11d44df47714c91c05d8ffd0970f38e9e3b20
  tree-spec:
    ref: tree-spec.md
    digest: 2837918d9d4f9ed822ab6aa7eff900b13e7af3f44575c934571bdacab6e0867d
  tree-manifest:
    ref: tree-manifest.md
    digest: 416346b8c368daa1d84862053f376c245991baa94439a2a6a2d9ce8cb0935ec4
  dependency-snapshot:
    ref: dependency-snapshot.md
    digest: 74c05fb156b9f9b38c5d836a3e262c96bb62ae9eef9ab4f7cb4a473ace88e081
  dependency-check:
    ref: dependency-check.md
    digest: 5d47369eddf1910f6f9dc06a65381e5168a33b03669e7aad25fcfab2c5c3728d
  subject-snapshot:
    ref: subject-snapshot.md
    digest: 92b8720b53bafac083a07ecb455c05abd5c82ae5d1577360e1bde690eb916e6d
  gate-check:
    ref: gate-check.md
    digest: f3d1bf1bd05b2629f47b1711bd9b2874c9f0ac8478caafb184c146235b6af027
  conformance-review:
    ref: conformance-review.md
    digest: 9de86e9afac0323ceb8177c1a45ff0d1d34a61412e49f74f4f49006e9c823943
---

# 按记录类型读取字段契约

先读CONTRACT正文，再按当前任务的记录类型定位；不要把全部字段投影注入每次Plan。这里是定位/固定索引，不是另一份规则。

| 时点 | 常用类型 |
|---|---|
| Plan/请求 | baseline、request、response、request-decision、gate-check |
| 测试/Check | test-suite、test-case、test-case-binding、test-run、review-package |
| 转换/结束 | transition、delivery、archive-receipt、task |
| 整树冻结 | work-node、tree-spec、tree-manifest、dependency-snapshot、dependency-check |

CONTROL/RESOURCE的停止和撤权条件跨阶段始终适用。辅助证据和检查覆盖见[关系边界](../record-relations.md)；真实输入可见性、签名、消息来源及写权不能由字段自证。

非正常尝试与等待记录另按[生命周期投影](../lifecycle-records.md)加载，不改变以上正常四边profile。
