---
schema: pdca.asset/v1
id: ontology:domain/report-center-deployment-assembly-patterns
type: domain
layer: Knowledge
status: active
dcterms_license: CC-BY-4.0
dcterms_created: 2026-09-04
dcterms_modified: 2026-09-04
owl_versionIRI: http://pdca.local/ontology/report-center-deployment-assembly-patterns/1.0.0
summary: Report Center 部署装配模式
domain:
- ontology:domain/report-center
relations:
  specializes:
  - ontology:domain/report-center
  relates_to:
  - ontology:concept/pdca
attributes:
- name: applicability
  desc: 领域知识适用场景
  constraint: 见正文
  testable_signal: "运行 grep -q '两阶段安装' ontology/domain/report-center/report-center-deployment-assembly-patterns.md && python3 scripts/ontology-validate.py --ontology-dir ontology 2>&1 | grep -q 'OK'"
---


# Report Center 部署装配模式

来源: records/T0221-0804-deployment-install/conclusion.md

## 适用场景

需要为已有运行服务补齐"可交付安装链路"时（预安装依赖检测、正式安装编排、DB 初始化、健康检查门禁、配置前置校验）。

## 核心模式：两阶段安装

### 阶段 1：预安装（`1.pre_install` + `2.install`）
- 只做环境准备：发行版/CPU 架构检测、依赖组件清单、用户/venv 创建。
- **不碰业务数据**：不建 Schema、不建账号、不开 Web 入口、不注册服务（AC-2）。
- 失败即非零退出且**不写 `.preinstall_done` 标记**——标记是后续阶段的门禁输入。

### 阶段 2：正式安装（`install.sh`）
校验顺序（任一项失败即退出，不写运行目录）：
1. 包完整性（sha256/md5）
2. manifest 逐行路径校验（跳过注释/空行）
3. 平台检查（x86_64/aarch64）
4. 预安装标识（`.preinstall_done` 存在）

编排顺序：
- 部署文件 → `--check-config` 预检（配置非法即中止）→ `--install-db`（DB 迁移 + admin 幂等）→ 健康检查门禁 → 写 `.install_done`。

## install-do 装配入口（关键范式）

独立 `--install-db` 命令作为"装配校验入口"，与安装编排解耦：

```bash
python -m collection_service.cli --install-db --conf-dir <dir> --admin-password <pwd>
```

- 从 `report.cfg` 读 `db_dsn`
- 应用全部未应用迁移（`applied_versions()` 幂等判断）
- `ensure_bootstrap_admin("admin", hash(pwd))`：首装创建 `must_change_password=true`；升级**复用已有不重置**
- 缺 `REPORT_ADMIN_PASSWORD` 环境变量 → 拒绝退出（防首装弱口令）

**收益**：升级回退有真实 DB 幂等保证，而非 shell 占位；`--install-db` 可独立于 install.sh 由运维手动执行。

## 健康检查门禁（AC-5）

- 探针框架（`deploy_health.py`）：process/port/db/redis/templates/jobstore/login 8 项
- **失败即不标记成功**（不写 `.install_done`）
- `--force` 供演练/紧急跳过
- 关键取舍：db/jobstore/login 的"真实可达性"由 `--install-db` 强保证，健康检查探针可保持框架占位——避免重复连接逻辑

## 配置前置校验（AC-6）

- `--check-config`：全局 report.cfg + 域周期文件（collection-jobs.d）+ 三阶段超时顺序（query<cli<rpc、任务总超时≤周期）
- 非法返回非零，安装前预检拒绝生效——安全变更（改采集参数/版本）前置防线

## 经验教训

1. **install.sh 调子脚本必须显式传参**：healthcheck 曾因只传 `--conf-dir` 漏传 `--install-dir`，探针路径落到默认 `/opt/aio/...`。子脚本所有路径参数都应从主脚本透传。
2. **shell 占位要尽早替换为真实装配**：AC-4 曾用注释占位"迁移由部署模块执行"，双轴审查判 Blocking——DB 初始化是安装核心，必须真实调用。
3. **沙箱禁 bind 端口的演练限制**：健康检查"通过路径"依赖单测；成功路径端到端验证需真实主机。
4. **打包与运行时目录分离**：`.preinstall_done`/`.install_done` 用绝对路径标记，manifest 只列相对路径，避免打包期路径泄漏。
