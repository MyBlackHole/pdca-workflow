# 两包两阶段安装部署与配置校验 — 规格文档

## 问题陈述

报表中心需按两包两阶段方式交付安装：预安装包初始化主机基础环境（Python 3.11.15 / PostgreSQL 17 / Redis），正式包安装应用、初始化 Report DB、注册服务并健康检查；需支持 bclinux x86_64 与 aarch64 双平台、升级/回退、配置校验与权限基线。

## 解决方案

产出预安装包（`rdb-report-init-<os>-<arch>.tar.gz`：`1.pre_install` + `2.install`）与正式包（`rdb_report_<version>_<os>-<arch>.tar.gz`：`install.sh`、`version.txt`、`manifest`、服务单元、Schema migration、固定模板、依赖 wheel、`--check-config` 校验），部署目录 `/opt/aio/report_center/`，systemd 服务 `rdb-report-web`/`rdb-report-collection`，配置文件权限基线。

## Seam 分析

- 测试接缝：容器/虚拟机内安装/升级/回退脚本演练；`--check-config` 对非法配置（非法键/超时顺序/超周期）拒绝；权限与 manifest 平台校验。
- Mock/Stub：双平台用对应 bclinux 容器基座；PostgreSQL/Redis 用包内初始化。

## 用户故事

1. 作为运维，我想要两阶段安装包，以便在 bclinux x86_64/aarch64 干净部署。
2. 作为运维，我想要 `--check-config` 与升级回退，以便安全变更采集参数与应用版本。

## 实现决策

- 落地仓库：**report-center 新仓库**。
- 依赖：T0215、T0218、T0219、T0220（应用产物）。
- 预安装阶段不创建 Report DB 业务 Schema/服务/端口（§2.2.2）；正式安装校验 manifest/平台/预安装标识/兼容矩阵，初始化 DB + `admin`（`must_change_password=true`）+ 健康检查（§2.2.3）。
- 配置：`report.cfg`（密钥/连接串）、`report-web.yaml`、`collection-jobs.yaml`/`template.yaml`/`d/`，权限 `0640 root:rdb-report`、域目录 `0750 rdb-report:rdb-report`（§6.1）。
- 版本与依赖变更须同步 manifest、依赖锁定、双平台产物与兼容矩阵（§2.3）。

## 测试决策

- 双平台安装/卸载/升级/回退演练；迁移备份-回退-恢复演练；配置校验命令负例；健康检查门禁。

## 验收标准

- [ ] AC-1: 预安装包 `1.pre_install` 校验 bclinux 发行版/CPU 架构/组件检测，`2.install` 安装 Python 3.11.15/PostgreSQL 17/Redis 依赖，任一失败非零退出，不标记预安装完成（§2.2.2）。
- [ ] AC-2: 预安装阶段不创建 Report DB 业务 Schema/默认账号/Web 入口/报表中心服务（§2.2.2）。
- [ ] AC-3: 正式包校验 SHA-256/MD5、manifest、平台、预安装标识；失败即退出不写运行目录（§2.2.3）。
- [ ] AC-4: 首次安装创建 `admin` 幂等且 `must_change_password=true`；升级不重置密码/管理员标记/启用状态；升级沿用迁移备份/校验/回退规则（§2.2.3、§3.1.3）。
- [ ] AC-5: 健康检查覆盖进程存活/端口/Report DB/Redis/模板注册表/JobStore/登录入口；未通过不得标记成功（§2.2.3）。
- [ ] AC-6: `rdb-report-collection --check-config` 校验全局/模板/全部未删除域文件与超时顺序（query<cli<rpc、任务总超时≤周期），非法拒绝生效（§6.1）。
- [ ] AC-7: x86_64 与 aarch64 均留存安装/卸载/升级/回退验收记录（§2.2.1）。

## 范围外

- 不做 HA/双活/主备切换（§2.1 明确一期不支持）。
- 不做 1000 域横向扩展。

## 备注

- 依赖：T0215、T0218、T0219、T0220；下游：T0222（验收基座）。
