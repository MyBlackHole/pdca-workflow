---
schema: pdca.text-fixture/v1
fixture_only: true
cases:
- id: NEGATION
  text: 子节点仅为 seed，未执行实现；不得声称孩子已实现。
  expected: accept
- id: AFFIRMATION
  text: 子节点已经全部实现并通过验收。
  expected: reject
- id: ABSENCE
  text: 本次没有看到“已实现”的断言，所以反例识别已经通过。
  expected: reject
- id: UNKNOWN
  text: 或许某个孩子在别处执行过，现无可核验记录。
  expected: unknown
---

# 固定中文正确/错误样本

这四条是实际字节夹具，不是用户消息。未知样本不得被模型默认为成功。外部工具用有限、明确的词句模式检查本组既定语法，并对always-pass/always-fail/只含“已实现”就拒绝的错误检查器做负控制；不宣称解决任意自然语言语义。

真实AI验收必须独立输入每条文本并保存其判定及对应原文，不把expected传为其actual。正确样本含禁止句，关键词-only应产生误报；错误正断言应拒绝；没有真正运行负样本而宣称识别通过同样拒绝。
