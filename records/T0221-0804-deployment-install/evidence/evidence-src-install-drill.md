# T0221 install.sh 安装演练证据

环境: 通用 Linux（沙箱禁 bind 端口，健康检查端口探针为环境限制）。REPORT_DB_DSN=postgresql://test:test@127.0.0.1:5433/report_test。

## AC-1 预安装演练（1.pre_install）
- 支持发行版检测（bclinux/arch 演练注入）、CPU 架构、组件清单
- 组件缺失 → MISSING=1 → exit 1 且不写 .preinstall_done ✓
- 依赖齐全 → 写 .preinstall_done ✓

## AC-2 预安装阶段
- 1.pre_install / 2.install 无任何 CREATE TABLE/Schema/默认账号操作（grep 验证）✓

## AC-3 正式包校验（install.sh）
- 完整性 sha256/md5、manifest 逐行路径校验（跳过注释/空行）、平台检查、预安装标识
- 缺 manifest / 缺 .preinstall_done → 拒绝退出 ✓

## AC-4 真实 DB 迁移 + admin 幂等（install.sh → --install-db）
首次: "DB 初始化完成：admin 创建"（迁移全部应用 + admin must_change_password=true）
升级:  "DB 初始化完成：admin 复用已有"（ensure_bootstrap_admin 幂等，不重置）✓
缺 REPORT_ADMIN_PASSWORD → 拒绝退出 ✓

## AC-5 健康检查门禁
- 端口未起（沙箱禁 bind）→ 健康检查失败 → "不标记成功" + exit 1 + 无 .install_done ✓
- --force 跳过门禁 → 写 .install_done（{"version":"0.5.0","installed_at":...}）✓
- deploy_health 单测 5 用例覆盖探针 valid/failed 判定 ✓

## AC-6 --check-config 预检
install.sh 安装前调用 check-config，配置非法 → 安装中止 ✓
