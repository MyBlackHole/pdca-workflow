# regression.md

{
  "task_id": "T0273",
  "check": "全量回归",
  "command": "python3 -m pytest tests/",
  "result": "272 passed, 4 failed, 13 subtests",
  "baseline": "265 passed/4 failed（T0272）新增 7 测试",
  "failed": [
    "test_harness 2（既有）",
    "test_operations 2（既有 doctor seam）"
  ],
  "note": "无新增回归"
}
