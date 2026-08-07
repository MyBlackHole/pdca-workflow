# T0224 异步导出与分布式配额测试证据

命令: `.venv/bin/python -m pytest tests/test_export_async.py tests/test_export_async_api.py tests/test_export_task.py tests/test_quota_distributed.py tests/test_web_config.py tests/test_quota.py tests/test_export_service.py -q`

定向结果: 33 passed
全量回归: 337 passed, 0 failed, 6 errors（均为既有 REPORT_TOKEN_PRIVATE_KEY 未配置环境问题，非本次变更）

覆盖:
- AC-1/AC-2: 异步端点 POST/GET、状态机 queued→running→completed/failed 持久化、产物落盘+下载、404、过期清理（export_async 3 + export_async_api 4 + export_task 6）
- AC-4: 异步不受 csv_max_rows=2 截断（5 行全量导出）
- AC-5: Redis 分布式租约多实例共享、耗尽 429、无 Redis fallback（quota_distributed 5 + quota 兼容 6）
- AC-6: report.cfg [web.export]/[web.quota] 参数接线（web_config 5）
- AC-7: V003__export_task 迁移 up/down 成对 + 全量回归

迁移修复: test_down_rolls_back_tables 改为倒序回滚全部 specs（V003→V001）再清审计重放，
兼容新增独立表迁移（原仅回滚 V001，遗留 V002/V003 表导致重放冲突）。
