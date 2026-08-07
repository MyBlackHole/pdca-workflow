# T0221 AC-6 配置校验测试证据

命令: `.venv/bin/python -m pytest tests/test_deploy_check.py tests/test_cli_check_config.py tests/test_deploy_health.py tests/test_deploy_install.py -q`

结果: 17 passed（deploy_check 9 + cli_check_config 6 + deploy_health 5 + deploy_install 3）

覆盖：
- AC-6: 超时顺序 query<cli<rpc 合法/非法、域周期目录缺失、install-db 参数校验
- AC-5: HealthReport 探针框架 valid/failed 判定
- AC-4: run_db_init 迁移应用 + admin 幂等（二次调用返回 False 不重建）

全量回归: 313 passed, 6 errors（均为既有 REPORT_TOKEN_PRIVATE_KEY 环境问题，非本次变更）
