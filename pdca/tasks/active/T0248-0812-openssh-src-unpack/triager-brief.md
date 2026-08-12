# Triage Brief — T0248

- **分类**: enhancement / development（外部源码包解压准备，为后续源码分析/补丁研究提供工作目录）
- **需求**: 解压 `/home/black/Downloads/openssh-9.6p1-16.oe2403sp4.src.rpm`，得到 openssh 9.6p1 源码树与 openEuler 24.03 SP4 全量补丁
- **查重**: 全局 grep `openssh|src.rpm|rpm2cpio` 无命中（knowledge 与 tasks 均无 openssh 相关既有任务）；不重复
- **事实核查**:
  - src.rpm 存在（2.49 MB），`rpm` 可读（Name=openssh, Version=9.6p1, Release=16.oe2403sp4）
  - 包内包含 `openssh-9.6p1.tar.gz`、`.asc` 签名、`openssh.spec`、约 100+ 个 backport/feature/bugfix patch（含 CVE-2024/2025/2026 系列、SM2/SMx 国密 feature、系统服务 unit 等）
  - 系统具备 `rpm2cpio` 与 `cpio` 工具，磁盘剩余 145G
- **关键未知（需 P1/P2 决策）**: 解压目标目录、是否校验 `.asc` 签名、是否连源码 tarball 一并解压、后续用途（源码分析/构建/补丁审计）

---

## 核查命令记录

```
rpm -qp --qf 'Name: %{NAME} ...' openssh-9.6p1-16.oe2403sp4.src.rpm
# Name: openssh Version: 9.6p1 Release: 16.oe2403sp4
rpm2cpio ... | cpio -t   # 列出包内内容清单
```
