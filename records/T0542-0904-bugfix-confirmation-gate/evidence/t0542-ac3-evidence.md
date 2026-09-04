# AC-3 证据：全量门禁与契约测试通过

## 契约测试

```bash
python3 -m pytest tests/test_diagnosing_bugs_enhance.py tests/test_fix_confirmation_gate.py -q
# 22 passed in 0.64s
```

test_fix_confirmation_gate.py 新增 12 项契约：
- schema 含 fix_confirmation 且 validates confirmed/rejected
- CLI 支持 fix_confirmation 且可 append
- diagnosing-bugs 含 Phase 4.5、fix_confirmation:confirmed、禁止改代码
- bug-analysis 含 根因≠现象、三类、双向预测、fix_confirmation
- bug-commit-format 含三类、fix_confirmation
- flow-do 含 确认修复方案 且顺序正确
- execution-contract 含 fix-approval 且顺序正确
- flow_audit 含 fix-confirmation 检查
- verify-document 通过

## 本体与执行契约校验

```bash
python3 scripts/ontology-validate.py --ontology-dir ontology
# OK: ontology 通过本体契约校验

python3 scripts/resolve-ai-execution-contract.py --verify-document --root .
# {"status":"ok","path":"ontology/process/flow-do.md","route_count":2}

python3 scripts/resolve-ai-execution-contract.py --scenario bugfix --root .
# 含 fix-approval 的 7-phase 正确返回
```

## 科学方法论依据

- 网络检索：HITL Approval-Gate、Zeller Scientific Debugging、Strategic Human Gate 均有实证与文献支持（见 discussion 记录）
- 用户已确认方向：fix_confirmation 三要素、存量 WARN、根因三类区分

## 其他门禁

- flow_audit 对存量 bugfix 缺确认记 WARN 不阻断，符合档 B 设计
- skill-content-baseline 已更新 4 文件 bytes 与理由
