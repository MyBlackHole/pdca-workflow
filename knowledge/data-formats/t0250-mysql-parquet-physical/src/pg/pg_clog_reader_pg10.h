#pragma once

/* CLOG 可见性 — T0250 PG 物理直读核心（相对 T0163 启发式的升级） */
typedef unsigned int TransactionId;
typedef unsigned int XidStatus;

#define InvalidTransactionId ((TransactionId) 0)

#define TRANSACTION_STATUS_IN_PROGRESS 0x00
#define TRANSACTION_STATUS_COMMITTED 0x01
#define TRANSACTION_STATUS_ABORTED 0x02
#define TRANSACTION_STATUS_SUB_COMMITTED 0x03

/* 返回 xid 的提交状态（0=IN_PROGRESS 1=COMMITTED 2=ABORTED 3=SUB_COMMITTED）。
 * dir = PGDATA/pg_xact 路径。 */
int pg_clog_xid_status(const char *pgxact_dir, TransactionId xid);