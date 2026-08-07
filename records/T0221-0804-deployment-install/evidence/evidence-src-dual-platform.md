# T0221 AC-7 双平台安装/卸载/升级/回退验收记录

状态: 留档（验收在目标环境执行，此处登记脚本平台支持证据）

- 1.pre_install 支持 bclinux x86_64/aarch64（uname -m 分支：x86_64/aarch64 白名单）
- install.sh 平台检查含 x86_64/aarch64；--skip-platform-check 供演练
- systemd 单元 rdb-report-web / rdb-report-collection 为平台无关 unit
- migrations/postgresql 的 V001__init.up/down.sql 成对，回退走 down.sql（升级沿用迁移备份/校验/回退规则，§3.1.3）

T0221 scope 说明: AC-7 实际双平台验收记录按 plan 决策延后 T0222（目标环境）；
此记录登记脚本层面的平台支持设计证据。
