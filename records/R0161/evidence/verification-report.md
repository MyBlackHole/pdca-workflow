# T0161 验证矩阵

以下命令均在仓库根目录执行并以退出码 0 结束。

| 命令 | 结果 | 支持的验收项 |
| --- | --- | --- |
| `python3 -m unittest tests.test_execution_and_invocation_contracts -v` | 6 tests OK；覆盖 schema canonical 约束、顺序/重复 marker、route alignment、alias/非法边和审计 fail-closed。 | AC-1, AC-2, AC-3, AC-5, AC-6, AC-7, AC-11 |
| `python3 -m unittest discover -s tests -p 'test_*.py' -q` | 全量单元测试通过。 | AC-1 至 AC-12 |
| `python3 scripts/resolve-ai-execution-contract.py --verify-document` | `status=ok`，`route_count=2`。 | AC-2, AC-3, AC-4 |
| `python3 scripts/resolve-skill-invocation.py --verify-documents` | `status=ok`，`asset_count=44`，`edge_count=39`，`alias_count=3`。 | AC-5, AC-6, AC-7, AC-8, AC-9 |
| `python3 scripts/run-ai-friendliness-fixtures.py --all` | 22/22 passed，failed=0；含 execution 顺序、manual edge、stale alias 及既有 lifecycle 反例。 | AC-2, AC-3, AC-6, AC-7, AC-9, AC-10, AC-12 |
| `python3 scripts/audit-skill-content.py --check-budget` | 44 assets，0 broken references，budget status=passed。 | AC-7, AC-8, AC-11, AC-12 |
| `python3 scripts/generate-skills-index.py --check` | `valid=true`，`asset_count=44`。 | AC-8, AC-11 |
| `python3 -m compileall -q scripts` | 通过。 | AC-11, AC-12 |
| `python3 scripts/pdca-doctor.py --json` | `valid=true`，57 references checked；仅提示外部项目应配置 `PDCA_HOME`。 | AC-12 |
| `git diff --check` | 通过。 | AC-11 |

范围核对：本次没有新增 package/dependency 清单、网络调用或 task schema/global Do-to-Check gate 改动。
