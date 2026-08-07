# T0224 V003 迁移证据

V003__export_task.up.sql / down.sql 成对存在。
test_migrations.py test_down_rolls_back_tables 已适配（倒序回滚全部 specs V002→V001，
compat 新增独立表 V003：先回滚 V003 create，重放全量后状态一致）。
定向 test_migrations: 7 passed；全量回归 337 passed。
