/*
 * stub_pg.c — PostgreSQL backend 运行时符号的最小 stub。
 *
 * 目的：允许直接链接官方 backend 源文件（heaptuple.c / mcxt.c / aset.c），
 * 仅提供错误处理与中断检查的降级实现；错误路径只打印后 abort。
 */
#include "postgres.h"

#include <signal.h>
#include <stdio.h>
#include <stdlib.h>

#include "utils/elog.h"

#ifdef fprintf
#undef fprintf
#endif
#ifdef snprintf
#undef snprintf
#endif
#ifdef sprintf
#undef sprintf
#endif
#ifdef strerror
#undef strerror
#endif

#include "common/hashfn.h"
#include "utils/datum.h"
#include "utils/hsearch.h"
#include "mb/pg_wchar.h"

bool
errstart(int elevel, const char *domain)
{
	(void) elevel;
	(void) domain;
	return true;
}

bool
errstart_cold(int elevel, const char *domain)
{
	return errstart(elevel, domain);
}

__attribute__((noreturn)) void
errfinish(const char *filename, int lineno, const char *funcname)
{
	fprintf(stderr, "postgres error (stub): %s:%d %s\n",
			filename ? filename : "?", lineno, funcname ? funcname : "?");
	abort();
}

int
errcode(int sqlerrcode)
{
	return sqlerrcode;
}

int
errcode_internal(int sqlerrcode)
{
	return sqlerrcode;
}

int
errmsg(const char *fmt, ...)
{
	(void) fmt;
	return 0;
}

int
errmsg_internal(const char *fmt, ...)
{
	(void) fmt;
	return 0;
}

int
errdetail(const char *fmt, ...)
{
	(void) fmt;
	return 0;
}

int
errdetail_internal(const char *fmt, ...)
{
	(void) fmt;
	return 0;
}

int
errdetail_log(const char *fmt, ...)
{
	(void) fmt;
	return 0;
}

int
errhint(const char *fmt, ...)
{
	(void) fmt;
	return 0;
}

int
errhint_internal(const char *fmt, ...)
{
	(void) fmt;
	return 0;
}

int
errcontext_msg(const char *fmt, ...)
{
	(void) fmt;
	return 0;
}

int
errhidestmt(bool hide_stmt)
{
	(void) hide_stmt;
	return 0;
}

int
errhidecontext(bool hide_ctx)
{
	(void) hide_ctx;
	return 0;
}

int
errbacktrace(void)
{
	return 0;
}

int
errposition(int cursorpos)
{
	return cursorpos;
}

int
internalerrposition(int cursorpos)
{
	return cursorpos;
}

int
internalerrquery(const char *query)
{
	(void) query;
	return 0;
}

int
err_generic_string(int field, const char *str)
{
	(void) field;
	(void) str;
	return 0;
}

int
geterrcode(void)
{
	return 0;
}

int
geterrposition(void)
{
	return 0;
}

int
getinternalerrposition(void)
{
	return 0;
}

int
set_errcontext_domain(const char *domain)
{
	(void) domain;
	return 0;
}

char *
format_elog_string(const char *fmt, ...)
{
	(void) fmt;
	return (char *) "format_elog_string";
}

ErrorContextCallback *
error_context_stack = NULL;

sigjmp_buf *
PG_exception_stack = NULL;

__attribute__((noreturn)) void
ExceptionalCondition(const char *conditionName, const char *fileName,
					 int lineNumber)
{
	fprintf(stderr, "TRAP: \"%s\" %s:%d\n", conditionName, fileName,
			lineNumber);
	abort();
}

volatile sig_atomic_t InterruptPending = false;

void
ProcessInterrupts(void)
{
}

/*
 * 以下符号仅在"缺失值缓存"路径（atthasmissing=true）或统计打印路径出现，
 * 本工具数据不触发；提供最小实现避免链接失败。
 */
uint32
hash_bytes(const unsigned char *k, int keylen)
{
	/* FNV-1a 简化实现 */
	const unsigned char *p = k;
	uint32		h = 2166136261U;
	int			n = keylen;

	while (n-- > 0)
	{
		h ^= *p++;
		h *= 16777619U;
	}
	return h;
}

__attribute__((noreturn)) void
hash_create_abort(void)
{
	fprintf(stderr, "unexpected dynahash use (stub)\n");
	abort();
}

HTAB *
hash_create(const char *tabname, long nelem, const HASHCTL *info, int flags)
{
	(void) tabname;
	(void) nelem;
	(void) info;
	(void) flags;
	hash_create_abort();
	return NULL;
}

void *
hash_search(HTAB *hashp, const void *keyPtr, HASHACTION action,
			bool *foundPtr)
{
	(void) hashp;
	(void) keyPtr;
	(void) action;
	(void) foundPtr;
	hash_create_abort();
	return NULL;
}

Datum
datumCopy(Datum value, bool typByVal, int typLen)
{
	(void) typByVal;
	(void) typLen;
	hash_create_abort();
	return value;
}

int
pg_mbcliplen(const char *mbstr, int len, int limit)
{
	(void) mbstr;
	return Min(len, limit);
}

bool
stack_is_too_deep(void)
{
	return false;
}

char *
pg_strerror_r(int errnum, char *buf, size_t buflen)
{
	if (buf && buflen > 0)
	{
		snprintf(buf, buflen, "%s", strerror(errnum));
		return buf;
	}
	return (char *) "";
}
