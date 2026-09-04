#include "common.h"
#include "fs_meta.h"
#include "fsbackup-common.h"
#include "transfer_file.h"
#include "logger.h"
#include "rpc.h"
#include "config.h"
#include "thread_pool.h"
#include "rpc-conn.h"
#include "rpc-command.h"

#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <errno.h>
#include <string.h>
#include <sys/stat.h>

extern int err_code;

void InitRpcArg(rpc_args *pArg, const CliConfig *pConfig)
{
	if (pArg == NULL || pConfig == NULL) {
		return;
	}
	pArg->scp_type = (pConfig->resume ? 2 : 1);
	pArg->svr_port = pConfig->source_port;
	pArg->is_compress = pConfig->compress;
	pArg->is_encrypt = pConfig->encrypt;
	pArg->is_checksum = pConfig->crc;
	pArg->parallel = 1; //(parallel <= 0 ? 1 : parallel);
	if (pConfig->source_host[0]) {
		snprintf(pArg->svr_ip, sizeof(pArg->svr_ip), "%s",
			 pConfig->source_host);
	}
}

int SendBlockRequest(struct session_info *session, download_info_t *downInfo,
		     block_info_t *blockCache, const int curCount)
{
	int ret = 0;
	if (downInfo == NULL || blockCache == NULL) {
		fprintf(stderr, "invalid arg\n");
		return -1;
	}
	if (curCount <= 0) {
		return 0;
	}
	trans_t transToken = NULL;
	//down block
	ret = rpc_download_block_start(session, downInfo, &transToken);
	if (ret != 0) {
		if (ret == EIO) {
			err_code = ret;
			return 0;
		}
		if (ret == 2222) {
			fprintf(stderr, "Warning: [%s] not existed.\n",
				downInfo->remote_file);
			return 0;
		} else {
			fprintf(stderr, "call rpc down block start failed,%s\n",
				downInfo->remote_file);
			return -1;
		}
	}
	fprintf(stderr, "remote_file:%s, down block count:%d.\n",
		downInfo->remote_file, curCount);
	ret = rpc_download_block(transToken, blockCache, curCount);
	if (ret < 0) {
		fprintf(stderr,
			"remote_file:%s, down block count:%d failed. \n",
			downInfo->remote_file, curCount);
	} else {
		// 下载成功了，但是数据不全
		// 因为源端修改了
		if (ret == EIO) {
			err_code = ret;
			ret = 0;
		}
		rpc_download_block_finish(transToken);
	}
	return ret;
}

#define MAX_TRANS_BLOCK 30000

struct backup_block_ctx {
	block_info_t blocks[MAX_TRANS_BLOCK];
	int block_count;
	int max_block_count;
	FsPathVal *path_val;
	session_info *curr_session;
	const CliConfig *p_config;
	std::string local_path;
	std::string remote_path;
	int *ret;
	int index;
	struct backup_path_ctx *ctx;
};

struct backup_thread_ctx_s {
	backup_block_ctx backup_block;
	thread_pool_t *thread_pool;
	struct session_info *conn;
};

typedef struct backup_thread_ctx_s backup_thread_ctx_t;

struct backup_path_ctx {
	std::string data_save_path;
	std::string backup_path;

	rpc_args *opts;
	thread_pool_t *thread_pools;
	struct session_info **conns;
	struct rpc_conn *dir_rpc_conn; // dedicated connection for directory ops

	uint64_t index;

	int *ret;

	backup_thread_ctx_t *backup_thread_ctxs;
	FsMeta *fs_meta;
	const CliConfig *p_config;

	std::string covered_prefix;
};

struct backup_file_task_t {
	std::string local_path;
	std::string remote_path;

	bool preserve;

	int *ret;

	rpc_args *opts;

	backup_thread_ctx_t *backup_thread_ctx;
	FsPathVal path_val;
};

void download_block_thread(void *arg)
{
	backup_block_ctx *backup_block = (backup_block_ctx *)arg;

	const CliConfig *p_config = backup_block->p_config;
	block_info_t *blocks = backup_block->blocks;
	int block_count = backup_block->block_count;
	session_info *curr_session = backup_block->curr_session;
	std::string local_path = backup_block->local_path + "." +
				 std::to_string(backup_block->index) + ".block";
	std::string remote_path = backup_block->remote_path;

	int ret = 0;
	int retry = g_pConfig->retry;
	download_info_t *downInfo = new download_info_t();

	if (*backup_block->ret != 0) {
		goto exit__;
	}

	downInfo->is_checksum = p_config->crc;
	downInfo->is_compress = p_config->compress;
	downInfo->is_encrypt = p_config->encrypt;

	strncpy(downInfo->local_file, local_path.c_str(),
		sizeof(downInfo->local_file) - 1);
	strncpy(downInfo->remote_file, remote_path.c_str(),
		sizeof(downInfo->remote_file) - 1);

	RPC_SESSION_OPT_RETRY(curr_session,
			      ((ret = SendBlockRequest(curr_session, downInfo,
						       blocks, block_count)) !=
				       0 &&
			       rpc_session_restart(curr_session) != 0),
			      retry);
	if (ret != 0) {
		fprintf(stderr, "SendBlockRequest failed, ret:%d\n", ret);
		goto exit__;
	}
exit__:

	delete downInfo;
	return;
}

int download_block(backup_path_ctx *ctx, std::string remote_path,
		   std::string local_path, block_info_t *blocks,
		   int block_count, int index)
{
	int ret = 0;
	backup_thread_ctx_t *backup_thread_ctxs = ctx->backup_thread_ctxs;
	thread_pool_t *tp = NULL;

	backup_block_ctx *task_ctx = new backup_block_ctx;
	task_ctx->local_path = local_path;
	task_ctx->remote_path = remote_path;
	task_ctx->block_count = block_count;
	task_ctx->ret = ctx->ret;
	memcpy(task_ctx->blocks, blocks, sizeof(block_info_t) * block_count);
	task_ctx->index = index;

	(ctx->index)++;
	task_ctx->curr_session =
		backup_thread_ctxs[ctx->index % ctx->p_config->parallel].conn;
	task_ctx->p_config = ctx->p_config;
	tp = backup_thread_ctxs[ctx->index % ctx->p_config->parallel]
		     .thread_pool;

try_file_again:
	ret = thread_task_post(tp, download_block_thread, task_ctx);
	if (ret != 0) {
		if (errno == EAGAIN) {
			sleep(1);
			goto try_file_again;
		}
		ErrorLog("thread_task_post failed, %s(%d)", strerror(errno),
			 errno);
		delete task_ctx;
		return ret;
	}

	return ret;
}

static int fs_bit_callback(FsPathVal *path_val, int64_t offset, size_t size,
			   void *arg)
{
	backup_block_ctx *backup_block = (backup_block_ctx *)arg;
	block_info_t *blocks = backup_block->blocks;
	int &block_count = backup_block->block_count;

	if (*backup_block->ret != 0) {
		WarningLog("stop bit enum");
		return 1;
	}

	blocks[block_count].offset = offset;
	blocks[block_count].size = size;
	block_count++;

	if (block_count >= backup_block->max_block_count) {
		if (download_block(backup_block->ctx, backup_block->remote_path,
				   backup_block->local_path,
				   backup_block->blocks,
				   backup_block->block_count,
				   backup_block->index++) != 0) {
			ErrorLog("download_block failed\n");
			return -1;
		}
		block_count = 0;
	}
	return 0;
}

int backup_file_block(const char *path, FsPathVal *path_val,
		      struct backup_path_ctx *ctx)
{
	int ret = 0;
	FsMeta *fs_meta = ctx->fs_meta;

	backup_block_ctx *backup_block = new backup_block_ctx;

	backup_block->ctx = ctx;
	backup_block->remote_path = ctx->backup_path + path;
	backup_block->local_path = ctx->data_save_path + path;

	backup_block->block_count = 0;
	backup_block->max_block_count = MAX_TRANS_BLOCK;
	backup_block->index = 0;
	backup_block->ret = ctx->ret;

	// TODO max_block_size 配置
	if (fs_meta->BitForEachCallback(fs_bit_callback, path_val, 65536,
					backup_block) != 0) {
		ErrorLog("BitForEachCallback failed\n");
		*ctx->ret = -1;
		goto return__;
	}

	if (backup_block->block_count > 0 &&
	    download_block(ctx, backup_block->remote_path,
			   backup_block->local_path, backup_block->blocks,
			   backup_block->block_count,
			   backup_block->index++) != 0) {
		ErrorLog("download_block failed\n");
		*ctx->ret = -1;
		goto return__;
	}

return__:
	delete backup_block;
	return ret;
}

static void backup_file_thread(void *ctx)
{
	int ret = -1;
	int retry = g_pConfig->retry;
	backup_file_task_t *task = (backup_file_task_t *)ctx;
	backup_thread_ctx_t *backup_thread_ctx = task->backup_thread_ctx;
	struct session_info *curr_session = backup_thread_ctx->conn;
	std::string local_path = task->local_path;
	std::string remote_path = task->remote_path;
	rpc_args *rpc_arg = task->opts;
	ret = 0;

	if (*task->ret != 0) {
		goto return__;
	}

	RPC_SESSION_OPT_RETRY(
		curr_session,
		((ret = do_scp_download(curr_session->sockfd,
					remote_path.c_str(), local_path.c_str(),
					rpc_arg, 0)) != 0 &&
		 rpc_session_restart(curr_session) != 0),
		retry);
	if (ret != 0) {
		fprintf(stderr, "do_scp_download failed, ret:%d\n", ret);
		*task->ret = ret;
		goto return__;
	}

return__:
	delete task;
	return;
}

static void backup_link_thread(void *ctx)
{
	int ret = -1;
	int retry = g_pConfig->retry;
	backup_file_task_t *task = (backup_file_task_t *)ctx;
	backup_thread_ctx_t *backup_thread_ctx = task->backup_thread_ctx;
	struct session_info *curr_session = backup_thread_ctx->conn;
	std::string local_path = task->local_path;
	std::string remote_path = task->remote_path;
	rpc_args *rpc_arg = task->opts;
	ret = 0;

	if (*task->ret != 0) {
		goto return__;
	}

	RPC_SESSION_OPT_RETRY(curr_session,
			      ((ret = do_scp_download_link(curr_session->sockfd,
							   remote_path.c_str(),
							   local_path.c_str(),
							   rpc_arg)) != 0 &&
			       rpc_session_restart(curr_session) != 0),
			      retry);
	if (ret != 0) {
		if (ret == -ENOENT) {
			WarningLog("symlink remote %s not exist, skip",
				   remote_path.c_str());
		} else {
			fprintf(stderr,
				"do_scp_download_link %s failed, ret:%d\n",
				remote_path.c_str(), ret);
			*task->ret = ret;
		}
	}

return__:
	delete task;
	return;
}

static bool is_path_covered(const char *path, const std::string &covered)
{
	if (covered.empty()) {
		return false;
	}
	std::string p(path);
	if (p.rfind(covered, 0) != 0)
		return false;
	return p.length() == covered.length() || p[covered.length()] == '/';
}

static bool is_ephemeral_dir(const char *path)
{
	if (path == NULL || *path == '\0') {
		return false;
	}
	const char *base = strrchr(path, '/');
	base = base ? base + 1 : path;
	return strncmp(base, "mount_verify", 12) == 0 ||
	       strncmp(base, "DISK_CHECK", 10) == 0;
}

struct dir_walk_ctx {
	struct backup_path_ctx *bctx;
	std::string remote_root;
};

static int dir_walk_callback(void *user, const char *rel_path, struct stat *st)
{
	void (*backup_func)(void *) = NULL;

	if (S_ISLNK(st->st_mode)) {
		backup_func = backup_link_thread;
	} else if (S_ISREG(st->st_mode)) {
		backup_func = backup_file_thread;
	} else {
		return 0;
	}

	struct dir_walk_ctx *wctx = (struct dir_walk_ctx *)user;
	struct backup_path_ctx *ctx = wctx->bctx;

	std::string full_remote = wctx->remote_root + "/" + rel_path;
	std::string rel = full_remote.substr(ctx->backup_path.length());
	std::string local = ctx->data_save_path + rel;

	struct backup_file_task_t *task = new backup_file_task_t;
	task->remote_path = full_remote;
	task->local_path = local;
	task->opts = ctx->opts;
	task->ret = ctx->ret;

	(ctx->index)++;
	task->backup_thread_ctx =
		&ctx->backup_thread_ctxs[ctx->index % ctx->p_config->parallel];
	thread_pool_t *tp = task->backup_thread_ctx->thread_pool;

try_again: {
	int r = thread_task_post(tp, backup_func, task);
	if (r != 0) {
		if (errno == EAGAIN) {
			sleep(1);
			goto try_again;
		}
		ErrorLog("thread_task_post failed, %s(%d)", strerror(errno),
			 errno);
		delete task;
		return r;
	}
}

	return 0;
}

static int backup_new_directory(struct backup_path_ctx *ctx, const char *path,
				const char *path_tmp)
{
	int ret = 0;
	std::string local = ctx->data_save_path + path;
	std::string remote_root = ctx->backup_path + path_tmp;
	struct dir_walk_ctx wctx;
	wctx.bctx = ctx;
	wctx.remote_root = remote_root;

	InfoLog("backup_new_directory: %s (remote: %s)", path,
		remote_root.c_str());

	if (mkdir_path(local.c_str()) != 0) {
		ErrorLog("mkdir_path %s failed", local.c_str());
		return -1;
	}

	ret = rpc_conn_cli_readdir_tree(ctx->dir_rpc_conn, remote_root.c_str(),
					dir_walk_callback, &wctx);
	if (ret != 0) {
		int saved_errno = errno;
		// 对临时目录的消失（ENOENT/ENOTDIR/IO_EOF=-3）做容错，避免整体增量中断
		if (is_ephemeral_dir(path) &&
		    (saved_errno == ENOENT || saved_errno == ENOTDIR ||
		     ret == -3)) {
			WarningLog(
				"backup_new_directory: skip ephemeral dir %s (remote: %s) ret=%d errno=%d (%s)",
				path, remote_root.c_str(), ret, saved_errno,
				strerror(saved_errno));
			return 0;
		}
		ErrorLog("backup_new_directory: readdir_tree %s failed, ret=%d",
			 remote_root.c_str(), ret);
		return -1;
	}

	return 0;
}

static int fs_path_callback(const char *path, FsPathVal *path_val, void *arg)
{
	int ret = 0;
	const char *path_tmp = path + 1;
	struct backup_path_ctx *ctx = (backup_path_ctx *)arg;
	backup_thread_ctx_t *backup_thread_ctxs = ctx->backup_thread_ctxs;
	rpc_args *opts = ctx->opts;
	thread_pool_t *tp = NULL;

	if (*ctx->ret != 0) {
		WarningLog("stop path enum");
		return 1;
	}

	if (is_path_covered(path, ctx->covered_prefix)) {
		InfoLog("%s is covered by parent dir backup, skip", path);
		return 0;
	}

	switch (path_val->type) {
	case TYPE_DEL:
		InfoLog("%s is del, ignore it", path);
		break;
	case TYPE_NEW: {
		if (S_ISDIR(path_val->st_mode)) {
			ctx->covered_prefix = path;
			if (backup_new_directory(ctx, path, path_tmp) != 0) {
				ErrorLog("backup_new_directory %s failed",
					 path);
				ret = -1;
			}
			break;
		}

		void (*backup_func)(void *) = NULL;
		if (S_ISLNK(path_val->st_mode)) {
			backup_func = backup_link_thread;
		} else if (S_ISREG(path_val->st_mode)) {
			backup_func = backup_file_thread;
		} else {
			break;
		}

		backup_file_task_t *task_ctx = new backup_file_task_t;
		task_ctx->remote_path = ctx->backup_path + path_tmp;
		task_ctx->local_path = ctx->data_save_path + path_tmp;
		task_ctx->opts = opts;
		task_ctx->ret = ctx->ret;

		(ctx->index)++;
		task_ctx->backup_thread_ctx =
			&backup_thread_ctxs[ctx->index %
					    ctx->p_config->parallel];
		tp = task_ctx->backup_thread_ctx->thread_pool;

try_again:
		ret = thread_task_post(tp, backup_func, task_ctx);
		if (ret != 0) {
			if (errno == EAGAIN) {
				sleep(1);
				goto try_again;
			}
			ErrorLog("thread_task_post failed, %s(%d)",
				 strerror(errno), errno);
			delete task_ctx;
			return ret;
		}

		break;
	}
	case TYPE_UPDATE: {
		if (backup_file_block(path_tmp, path_val, ctx) != 0) {
			ErrorLog("backup_file_block failed\n");
			ret = -1;
		}
		break;
	}
	default:
		fprintf(stderr, "file %s byte_id:%ld, fileSizeExt:%ld skip\n",
			path, path_val->byte_id, path_val->size_ext);
		ret = -1;
		break;
	}

	return ret;
}

int TransferIncrementData(const CliConfig *p_config,
			  const std::string &save_path,
			  const std::string &data_save_path)
{
	int ret = 0;
	int backup_ret = 0;

	struct backup_path_ctx path_enum_ctx = {};
	struct session_info **conns = NULL;
	thread_pool_t *thread_pools = NULL;
	backup_thread_ctx_t *backup_thread_ctxs = NULL;
	struct rpc_conn *dir_rpc_conn = NULL;

	rpc_args *rpc_arg = new rpc_args();
	int retry = g_pConfig->retry;
	std::string meta_save_path = save_path + "/meta";

	FsMeta meta(meta_save_path, 0, MDB_RDONLY | MDB_NOTLS | MDB_NOLOCK);

	if (meta.InitFsMeta() != 0) {
		fprintf(stderr, "init fs meta failed\n");
		goto exit__;
	}

	if (meta.OnBegin(true) != 0) {
		fprintf(stderr, "on begin failed\n");
		goto exit__;
	}

	InitRpcArg(rpc_arg, p_config);
	memcpy(rpc_arg->local_ip, p_config->local_ip,
	       sizeof(rpc_arg->local_ip) - 1);
	rpc_arg->local_port = p_config->local_port;

	RPC_CONN_RETRY((dir_rpc_conn = rpc_conn_start(rpc_arg)) == NULL, retry);
	if (dir_rpc_conn == NULL) {
		fprintf(stderr, "rpc_conn_start for dir_rpc_conn failed\n");
		goto exit__;
	}

	conns = (struct session_info **)malloc(p_config->parallel *
					       sizeof(struct session_info *));
	if (conns == NULL) {
		ErrorLog("malloc failed, %s(%d)", strerror(errno), errno);
		goto exit__;
	}

	for (int i = 0; i < p_config->parallel; i++) {
		RPC_SESSION_OPT_RETRY(
			conns[i],
			((conns[i] = rpc_session_start(rpc_arg)) == NULL),
			retry);
		if (conns[i] == NULL) {
			fprintf(stderr, "rpc_session_start failed\n");
			goto exit__;
		}
	}

	thread_pools = (thread_pool_t *)malloc(p_config->parallel *
					       sizeof(thread_pool_t));
	if (thread_pools == NULL) {
		ErrorLog("malloc failed, %s(%d)", strerror(errno), errno);
		goto exit__;
	}

	for (int i = 0; i < p_config->parallel; i++) {
		thread_pools[i].threads = 1;
		thread_pools[i].max_queue = 1000;

		ret = thread_pool_init(&thread_pools[i]);
		if (ret != 0) {
			fprintf(stderr, "thread_pool_init failed\n");
			goto exit__;
		}
	}

	backup_thread_ctxs = (backup_thread_ctx_t *)malloc(
		p_config->parallel * sizeof(backup_thread_ctx_t));
	if (backup_thread_ctxs == NULL) {
		ErrorLog("malloc failed, %s(%d)", strerror(errno), errno);
		goto exit__;
	}

	for (int i = 0; i < p_config->parallel; i++) {
		backup_thread_ctxs[i].thread_pool = &thread_pools[i];
		backup_thread_ctxs[i].conn = conns[i];
	}

	path_enum_ctx.index = 0;
	path_enum_ctx.thread_pools = thread_pools;
	path_enum_ctx.conns = conns;
	path_enum_ctx.dir_rpc_conn = dir_rpc_conn;
	path_enum_ctx.opts = rpc_arg;
	path_enum_ctx.data_save_path = data_save_path;
	path_enum_ctx.backup_path = p_config->backup_path;
	path_enum_ctx.p_config = p_config;
	path_enum_ctx.ret = &backup_ret;
	path_enum_ctx.backup_thread_ctxs = backup_thread_ctxs;
	path_enum_ctx.fs_meta = &meta;

	if (meta.PathForEachCallback(fs_path_callback, NULL, &path_enum_ctx) !=
	    0) {
		ret = -1;
		fprintf(stderr, "PathForEachCallback failed\n");
		goto exit__;
	}

	meta.OnAbort();

	ret = 0;
exit__:

	if (backup_ret != 0) {
		ret = -1;
	}

	if (thread_pools) {
		for (int i = 0; i < p_config->parallel; i++) {
			thread_pool_destroy(&thread_pools[i]);
		}
		free(thread_pools);
		thread_pools = NULL;
	}

	if (dir_rpc_conn != NULL) {
		rpc_conn_free(dir_rpc_conn);
	}

	if (conns != NULL) {
		for (int i = 0; i < p_config->parallel; i++) {
			if (conns[i] != NULL) {
				rpc_session_stop(conns[i]);
			}
		}
		free(conns);
		conns = NULL;
	}

	if (backup_thread_ctxs) {
		free(backup_thread_ctxs);
		backup_thread_ctxs = NULL;
	}

	delete rpc_arg;
	return ret;
}

/*
* TransferTargetPath: 将目标路径从远程服务器传输到本地服务器
* @param pConfig: 客户端配置
* @param rpcHost: 远程服务器地址
* @param backupPath: 备份路径
* @param StoreDataPath: 备份数据存放路径
* @param remotePath: 远程路径
* @param bFullBak: 是否全量备份
* @param strExcludes: 排除文件列表
* @return 0:成功 -1:失败
*/
int TransferTargetPath(const CliConfig *pConfig, const std::string &save_dir,
		       const std::string &data_save_dir,
		       const std::string &remote_path, const bool full_bak,
		       const std::string &excludes)
{
	int ret = -1;
	std::string bcm_path = save_dir + "bcm" + "/";

	if (pConfig == NULL || pConfig->host[0] == '\0' ||
	    pConfig->rpc_port == 0) {
		ErrorLog("pConfig is %p", pConfig);
		return ret;
	}
	if (pConfig->host[0] == '\0' || pConfig->rpc_port == 0) {
		ErrorLog("bah [%s:%d]", pConfig->host, pConfig->rpc_port);
		return ret;
	}
	if (access(save_dir.c_str(), F_OK) != 0) {
		ErrorLog("%s not a dir", save_dir.c_str());
		return ret;
	}
	int64_t beginTime = GetTimetampNS();

	if (full_bak) {
		int retry = g_pConfig->retry;
		rpc_args rpcArg = { 0 };
		InitRpcArg(&rpcArg, pConfig);
		strncpy(rpcArg.remote, remote_path.c_str(),
			sizeof(rpcArg.remote) - 1);
		strncpy(rpcArg.local, data_save_dir.c_str(),
			sizeof(rpcArg.local) - 1);
		memcpy(rpcArg.local_ip, pConfig->local_ip,
		       sizeof(rpcArg.local_ip) - 1);
		rpcArg.exclude_path = excludes;
		rpcArg.local_port = pConfig->local_port;
		InfoLog("begin transfer files:%s checksum:%d, compress:%d, encrypt:%d",
			remote_path.c_str(), rpcArg.is_checksum,
			rpcArg.is_compress, rpcArg.is_encrypt);

		if (pConfig->resume) {
			strncpy(rpcArg.bcm, bcm_path.c_str(),
				sizeof(rpcArg.bcm) - 1);
		}

		if (pConfig->parallel > 0) {
			rpcArg.parallel = pConfig->parallel;
		}

		struct session_info *curr_session = NULL;

		RPC_SESSION_OPT_RETRY(
			curr_session,
			((curr_session = rpc_session_start(&rpcArg)) == NULL),
			retry);
		if (curr_session == NULL) {
			ErrorLog("start session failed");
			ret = -1;
			goto exit__;
		}

		ret = rpc_download_file(curr_session);
		rpc_session_stop(curr_session);
		if (ret != 0) {
			ErrorLog("download full dir %s from %s:%u failed",
				 remote_path.c_str(), rpcArg.remote,
				 pConfig->rpc_port);
			goto exit__;
		}
	} else {
		ret = TransferIncrementData(pConfig, save_dir, data_save_dir);
		if (ret != 0) {
			ErrorLog("download increment %s from %s:%u failed",
				 remote_path.c_str(), remote_path.c_str(),
				 pConfig->rpc_port);
		}
	}
exit__:
	int64_t endTime = GetTimetampNS();
	double usTime = (endTime - beginTime) / 1000.0;
	InfoLog("elapsed time:%0.2lf us (%0.2lf s)", usTime, usTime / 1000000);
	return ret;
}
