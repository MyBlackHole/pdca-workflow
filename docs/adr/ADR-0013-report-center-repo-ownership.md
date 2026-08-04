# ADR-0013：报表中心实现仓库归属

## 状态

已接受（2026-08-04，经 Plan 澄清确认，方向确认阶段修订一次）

## 背景

需求 140 的最终技术方案（`cdm-report-center-final-technical-solution.md`）隐含设想：`report-web`、`collection-service`、Report DB 共享包归属于独立 `report-center` 仓库；`cdm-data-cli` 可能随 `aio-cdm` 同仓交付（"若 CLI 与 aio-cdm 同仓交付，只新增 CLI 入口、查询适配和输出转换代码"）。

但当前唯一代码仓库是 `aio-cdm`（本仓），且无既有 report-center 实现。

## 决策

`cdm-data-cli` 落地于当前 `aio-cdm` 仓库（新增 CLI 入口、查询适配和输出转换，复用既有 ORM 只读模型）；`report-web`、`collection-service`、Report DB Adapter/Repository/Migration、模板与安装配置归独立 `report-center` 新仓库。

## 取舍

- 收益：`report-center` 与 CDM 主业务解耦，符合主方案隐含的独立仓库设想；报表中心依赖（FastAPI、APScheduler、pycryptodome）不污染 `aio-cdm` 主仓；跨仓兼容清单（方案 3.4.1）边界清晰。
- 代价：需建立新仓库、跨仓契约测试与配套发布（CLI JSONL/RPC 契约）；`report-center` 引用 `aio-cdm` 既有资产（`EncryptedTrim` 模式、`AIOAPScheduler` 模式、`aio-public-module.RemoteClient`）需以只读/复用方式引入。
- 边界：跨仓兼容清单（方案 3.4.1）中的"不修改既有 ORM 模型"约束仍然成立；`aio-cdm` 既有 ORM 只被 CLI 复用读取，不修改；`report-center` 经既有 rpc 工具通道调用 CLI，不直连 CDM 业务库。

## 影响

拆解后各子任务的落地路径分属两个仓库：①契约文档、cdm-data-cli、验收压测中的 CLI 部分落 `aio-cdm`；②report-web、collection-service、Report DB、部署安装落 `report-center`（新建）。契约文档与跨仓测试作为两侧对齐基线。
