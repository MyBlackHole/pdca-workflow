/**
 * @file sbt.c
 * @author yezi (you@domain.com)
 * @brief 
 * @version 0.1
 * @date 2023-05-26
 * 
 * @copyright Copyright (c) 2023
 * 
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <getopt.h>
#include <time.h>
#include <sys/epoll.h>
#include <sys/stat.h>
#include <fcntl.h>

#include <stdbool.h>
#include <sys/select.h>
#include <sys/eventfd.h>

#include <pthread.h>
#include <sys/sendfile.h>

#include <assert.h>
#include <stdint.h>
#include <sys/wait.h>
#include <dirent.h>
#include <ftw.h>
#include <sched.h>
#include <syslog.h>

#include "dmsbt_dll.h"
#include "logger.h"
#include "protocol.h"
#include "network.h"

typedef struct dmsbtex_global_ {
	int32_t piece_size;
	int32_t sbt_api_version;
	char sbt_vendor_desc[128];
	int32_t sbt_mm_version;

	char baseon_backupset[256];
	char backupdirs[256];
	char default_backupdirs[256];
} dmsbtex_global_t;

#define MAX_SBTINIT2_BACKUPDIRS 1024
typedef struct dmsbtex_ {
	int opt_type;
	int agent;
	dm_hs_session_t io;
	dmsbtex_global_t dmsbtex_global;

	sbtinit_output_t sbtinit_out[5];
	sbtinit2_output_t sbtinit2_out[MAX_SBTINIT2_BACKUPDIRS];
	sbtbfinfo_t sbtbfinfo_out[6];

	int sbtinit2_backupsets_info; /* Need backup sets information, and need all if SBTINIT2_BACKUPDIRS not set */
	int sbtinit2_is_backup;
	int sbtinit2_is_increment;
	char backupset[200];
	char backup_file[256];
	char create_time[64];
	char expire_time[64];
	char backup_volumlab[256];
	char backup_comment[256];

	int backup_dirs_num;
	char *backup_dirs[MAX_SBTINIT2_BACKUPDIRS];

	int checksum_enabled;
	int compress_enabled;
	int srv_port;
	char srv_ip[64];
	char log_path[256];

	int config_inited;

	int buflen;
	char *host;
	char *net;

	dmsbtex_tls_config_t tls_cfg;
} dmsbtex_t;

int init_sbt_config(const char *cfg, dmsbtex_t *sbt);

static int init_dmsbtex_global(dmsbtex_global_t *sbt_global)
{
	memset(sbt_global, 0x00, sizeof(*sbt_global));
	sbt_global->piece_size = 2048;
	sbt_global->sbt_api_version = DMSBT_DLL_VERSION;
	snprintf(sbt_global->sbt_vendor_desc,
		 sizeof(sbt_global->sbt_vendor_desc), "ShangHai An Tai Fei");
	sbt_global->sbt_mm_version = DMSBT_DLL_VERSION;
	return 1;
}

#define CHECK_CONFIG(sbt)                                                  \
	do {                                                               \
		if (!(sbt)->config_inited) {                               \
			syslog(LOG_ERR, "%s: config not initialized\n", __func__); \
			return SBT_EC_FAIL;                                \
		}                                                          \
	} while (0)

#define CONFIG_DIR "/opt/aio/airflow/tools/dm_sbt"
////////////////////////////////////////////////////////////////////////////////
sbtcode_t sbtversion(sbtuint2 *version)
{
	*version = DMSBT_DLL_VERSION;
	return SBT_EC_SUCCESS;
}

sbtcode_t sbtinit(void **gvar_out, sbtinit_input_t *in, sbtinit_output_t **out)
{
	dmsbtex_t *sbt = NULL;

	openlog("dm_libdmsbtex", LOG_PID | LOG_CONS, LOG_KERN);

	sbt = (dmsbtex_t *)malloc(sizeof(dmsbtex_t));
	if (sbt == NULL) {
		syslog(LOG_ERR, "malloc for sbt failure.\n");
		return SBT_EC_FAIL;
	}
	memset(sbt, 0x00, sizeof(*sbt));

	sbt->buflen = TCP_PACKAGE_SIZE;
	sbt->host = (char *)malloc(sbt->buflen + sizeof(network_header_t) * 4);
	sbt->net = (char *)malloc(sbt->buflen + sizeof(network_header_t) * 4);
	if (sbt->host == NULL || sbt->net == NULL) {
		syslog(LOG_ERR, "malloc for host/net failure.\n");
		free(sbt->host);
		free(sbt->net);
		free(sbt);
		return SBT_EC_FAIL;
	}

	init_dmsbtex_global(&sbt->dmsbtex_global);

	sbt->sbtinit_out[0].o_type = SBTINIT_MAXSIZE;
	sbt->sbtinit_out[0].o_obj = &sbt->dmsbtex_global.piece_size;
	sbt->sbtinit_out[1].o_type = SBTINIT_MMS_APIVSN;
	sbt->sbtinit_out[1].o_obj = &sbt->dmsbtex_global.sbt_api_version;
	sbt->sbtinit_out[2].o_type = SBTINIT_MMS_DESC;
	sbt->sbtinit_out[2].o_obj = sbt->dmsbtex_global.sbt_vendor_desc;
	sbt->sbtinit_out[3].o_type = SBTINIT_MMS_VSN;
	sbt->sbtinit_out[3].o_obj = &sbt->dmsbtex_global.sbt_mm_version;
	sbt->sbtinit_out[4].o_type = SBTINIT_INEND;
	sbt->sbtinit_out[4].o_obj = NULL;

	*gvar_out = sbt;
	*out = sbt->sbtinit_out;

	return SBT_EC_SUCCESS;
}

sbtcode_t sbtinit2(void *gvar_in, sbtinit2_input_t *in, sbtinit2_output_t **out)
{
	int idx = 0;
	dmsbtex_t *sbt = (dmsbtex_t *)gvar_in;
	sbtinit2_input_t *in_arg = in;

	while (in_arg->i_type != SBTINIT_INEND) {
		if (in_arg->i_type == SBTINIT2_TRACE_LEVEL) {
			syslog(LOG_INFO, "[SBTINIT2_TRACE_LEVEL %lu ]",
			       (unsigned long)in_arg->i_obj);
		} else if (in_arg->i_type == SBTINIT2_MAXSIZE) {
			syslog(LOG_INFO, "[SBTINIT2_MAXSIZE %lu ]",
			       (unsigned long)in_arg->i_obj);
		} else if (in_arg->i_type == SBTINIT2_DBNAME) {
			syslog(LOG_INFO, "[SBTINIT2_DBNAME [%s] ]",
			       (sbtchar *)in_arg->i_obj);
		} else if (in_arg->i_type == SBTINIT2_DBMAGIC) {
			syslog(LOG_INFO, "[SBTINIT2_DBMAGIC %lu ]",
			       (unsigned long)in_arg->i_obj);
		} else if (in_arg->i_type == SBTINIT2_BACKUPSET) {
			snprintf(sbt->backupset, sizeof(sbt->backupset), "%s",
				 (sbtchar *)in_arg->i_obj);
			syslog(LOG_INFO, "[SBTINIT2_BACKUPSET [%s] ]",
			       sbt->backupset);
		} else if (in_arg->i_type == SBTINIT2_BACKUPDIRS) {
			syslog(LOG_INFO, "[SBTINIT2_BACKUPDIRS [%s] ]",
			       (sbtchar *)in_arg->i_obj);
		} else if (in_arg->i_type == SBTINIT2_BASEON_BACKUPSET) {
			syslog(LOG_INFO, "[SBTINIT2_BASEON_BACKUPSET [%s] ]",
			       (sbtchar *)in_arg->i_obj);
		} else if (in_arg->i_type == SBTINIT2_BACKUPSETS_INFO) {
			sbt->sbtinit2_backupsets_info =
				(unsigned long)in_arg->i_obj;
			syslog(LOG_INFO, "[SBTINIT2_BACKUPSETS_INFO %u ]",
			       sbt->sbtinit2_backupsets_info);
		} else if (in_arg->i_type == SBTINIT2_IS_BACKUP) {
			sbt->sbtinit2_is_backup = (unsigned long)in_arg->i_obj;
			syslog(LOG_INFO, "[SBTINIT2_IS_BACKUP %u ]",
			       sbt->sbtinit2_is_backup);
		} else if (in_arg->i_type == SBTINIT2_IS_INCREMENT) {
			sbt->sbtinit2_is_increment =
				(unsigned long)in_arg->i_obj;
			syslog(LOG_INFO, "[SBTINIT2_IS_INCREMENT %u ]",
			       sbt->sbtinit2_is_increment);
		} else if (in_arg->i_type == SBTINIT2_BACKUPNAME) {
			syslog(LOG_INFO, "[SBTINIT2_BACKUPNAME [%s] ]",
			       (sbtchar *)in_arg->i_obj);
		} else if (in_arg->i_type == SBTINIT2_DEF_BAKDIR) {
			snprintf(sbt->dmsbtex_global.default_backupdirs,
				 sizeof(sbt->dmsbtex_global.default_backupdirs),
				 "%s", (sbtchar *)in_arg->i_obj);
			syslog(LOG_INFO, "[SBTINIT2_DEF_BAKDIR [%s] ]",
			       sbt->dmsbtex_global.default_backupdirs);
		} else {
			syslog(LOG_ERR, "-----------------unknown type %u",
			       in_arg->i_type);
		}
		++in_arg;
	}

	char config_file[4096] = { 0 };
	snprintf(config_file, sizeof(config_file), "%s/%s/sbt.conf", CONFIG_DIR,
		 sbt->backupset);

	if (init_sbt_config(config_file, sbt) != 0) {
		syslog(LOG_ERR, "init_sbt_config failure.\n");
		return SBT_EC_FAIL;
	}

	struct sockaddr_in addr;
	char logfile[256] = { 0 };
	snprintf(logfile, sizeof(logfile), "log-sbtinit-%d-%lu.log", getpid(),
		 pthread_self());
	init_logger(sbt->log_path, logfile);
	InfoLog("config file: %s", config_file);

	memset(&addr, 0x0, sizeof(struct sockaddr_in));
	addr.sin_family = AF_INET;
	addr.sin_port = htons(sbt->srv_port);
	addr.sin_addr.s_addr = inet_addr(sbt->srv_ip);
	sbt->agent = socket(AF_INET, SOCK_STREAM, 0);
	if (connect(sbt->agent, (struct sockaddr *)&addr,
		    sizeof(struct sockaddr_in)) < 0) {
		close(sbt->agent);
		sbt->agent = 0;
		InfoLog("connect to [%s:%d] failure. status: %s(errno: %d)\n",
			sbt->srv_ip, sbt->srv_port, strerror(errno), errno);
		close_logger();
	} else {
		if (sbt_session_client_init(&sbt->io, sbt->agent,
					    &sbt->tls_cfg) != 0) {
			close(sbt->agent);
			sbt->agent = -1;
			close_logger();
			return SBT_EC_FAIL;
		}
		sbt->config_inited = 1;
	}

	if (sbt->sbtinit2_backupsets_info && sbt->sbtinit2_is_backup == 0 &&
	    sbt->sbtinit2_is_increment == 0) {
		sbt->sbtinit2_out[0].o_type = SBTINIT2_BACKUPSET;
		sbt->sbtinit2_out[0].o_obj = sbt->backupset;
		// sbt->sbtinit2_out[1].o_type = SBTINIT2_BASEON_BACKUPSET;
		// sbt->sbtinit2_out[1].o_obj = sbt->dmsbtex_global.baseon_backupset;
		// sbt->sbtinit2_out[1].o_type = SBTINIT2_BACKUPDIRS;
		// sbt->sbtinit2_out[1].o_obj = sbt->dmsbtex_global.default_backupdirs; ////sbt->dmsbtex_global.backupdirs;
		// sbt->sbtinit2_out[2].o_type = SBTINIT_INEND;
		// sbt->sbtinit2_out[2].o_obj = NULL;

		for (idx = 1; idx < (MAX_SBTINIT2_BACKUPDIRS - 1) &&
			      idx <= sbt->backup_dirs_num;
		     ++idx) {
			sbt->sbtinit2_out[idx].o_type = SBTINIT2_BACKUPDIRS;
			sbt->sbtinit2_out[idx].o_obj =
				sbt->backup_dirs[idx - 1];

			InfoLog("sbt->backup_dirs[%d]:%s", idx - 1,
				sbt->backup_dirs[idx - 1]);
		}
		sbt->sbtinit2_out[idx].o_type = SBTINIT_INEND;
		sbt->sbtinit2_out[idx].o_obj = NULL;
	} else if (sbt->sbtinit2_backupsets_info && sbt->sbtinit2_is_backup &&
		   sbt->sbtinit2_is_increment) {
		for (idx = 0; idx < (MAX_SBTINIT2_BACKUPDIRS - 1) &&
			      idx < sbt->backup_dirs_num;
		     ++idx) {
			sbt->sbtinit2_out[idx].o_type = SBTINIT2_BACKUPDIRS;
			sbt->sbtinit2_out[idx].o_obj = sbt->backup_dirs[idx];

			InfoLog("sbt->backup_dirs[%d]:%s", idx,
				sbt->backup_dirs[idx]);
		}
		sbt->sbtinit2_out[idx].o_type = SBTINIT_INEND;
		sbt->sbtinit2_out[idx].o_obj = NULL;
	} else if (sbt->sbtinit2_backupsets_info == 0 &&
		   sbt->sbtinit2_is_backup == 0 &&
		   sbt->sbtinit2_is_increment == 0) {
		sbt->sbtinit2_out[0].o_type = SBTINIT2_BACKUPSET;
		sbt->sbtinit2_out[0].o_obj = sbt->backupset;
		sbt->sbtinit2_out[1].o_type = SBTINIT_INEND;
		sbt->sbtinit2_out[1].o_obj = NULL;
	} else {
		sbt->sbtinit2_out[0].o_type = SBTINIT_INEND;
		sbt->sbtinit2_out[0].o_obj = NULL;
	}

	*out = sbt->sbtinit2_out;

	return SBT_EC_SUCCESS;
}

sbtcode_t sbtbackup(void *gvar_in, sbtint4 bfile_type, sbtchar *bfile_name)
{
	int ret = 0;
	int len = 0;
	int err = 0;
	time_t create_time = 0;
	network_header_t *host = NULL;
	dmsbtex_t *sbt = (dmsbtex_t *)gvar_in;
	CHECK_CONFIG(sbt);

	snprintf(sbt->backup_file, sizeof(sbt->backup_file), "%s/%s",
		 sbt->backupset, bfile_name);
	InfoLog("come here [bfile_type %d bfile_name %s (%s)]", bfile_type,
		bfile_name, sbt->backup_file);
	sbt->opt_type = OPT_BACKUP;

	host = (network_header_t *)sbt->host;
	memset(host, 0x00, sizeof(*host));
	host->cmd = CMD_BACKUP_OPEN;
	host->bytes = strlen(sbt->backup_file);
	host->org_bytes = host->bytes;
	memcpy(sbt->host + sizeof(*host), sbt->backup_file, host->bytes);
	len = host->bytes;
	ret = send_packet(&sbt->io, sbt->host, sbt->net,
			  sbt->host + sizeof(*host), len);
	if (len != ret) {
		ErrorLog(
			"begin backup failure. sbt->backup_file:%s, [len %d != ret %d]",
			sbt->backup_file, len, ret);
		return SBT_EC_FAIL;
	} else {
		InfoLog("begin backup. sbt->backup_file:%s, [len %d == ret %d]",
			sbt->backup_file, len, ret);
	}

	ret = recv_packet(&sbt->io, sbt->host, sbt->net,
			  sbt->host + sizeof(*host), sbt->buflen);
	err = *((int *)(sbt->host + sizeof(*host)));
	if (ret <= 0 || host->cmd != CMD_BACKUP_OPEN_RESP ||
	    host->bytes != sizeof(ret) || err != 0) {
		ErrorLog(
			"begin backup failure. sbt->backup_file:%s, [ ret %d err %d cmd 0x%x bytes %d]",
			sbt->backup_file, ret, err, host->cmd, host->bytes);
		return SBT_EC_FAIL;
	} else {
		InfoLog("begin backup success. sbt->backup_file:%s, [ ret %d err %d cmd 0x%x bytes %d]",
			sbt->backup_file, ret, err, host->cmd, host->bytes);
	}

	////snprintf(sbt->backup_file, sizeof(sbt->backup_file), "%s/%s", sbt->backupset, bfile_name);
	////snprintf(sbt->backup_file, sizeof(sbt->backup_file), "%s", bfile_name);
	create_time = time(NULL);
	memcpy(sbt->create_time, &create_time, sizeof(create_time));
	create_time += 3600ul * 24ul * 365ul * 200ul; /**expire 200 year**/
	memcpy(sbt->expire_time, &create_time, sizeof(create_time));
	snprintf(sbt->backup_volumlab, sizeof(sbt->backup_volumlab), "%s",
		 "zfs-pool");
	snprintf(sbt->backup_comment, sizeof(sbt->backup_comment), "%s",
		 sbt->dmsbtex_global.sbt_vendor_desc);

	return SBT_EC_SUCCESS;
}

sbtcode_t sbtwrite(void *gvar_in, sbtbyte *buf, sbtuint4 buf_len)
{
	int ret = 0;
	sbtuint4 offset = 0;
	sbtuint4 total = 0;
	sbtuint4 bytes = 0;
	network_header_t *host = NULL;
	dmsbtex_t *sbt = (dmsbtex_t *)gvar_in;
	CHECK_CONFIG(sbt);
	InfoLog("come here [buf_len %d]", buf_len);

	host = (network_header_t *)sbt->host;

	offset = 0;
	total = buf_len;
	while (offset < buf_len) {
		memset(host, 0x00, sizeof(*host));
		host->cmd = CMD_BACKUP;
		bytes = (sbt->buflen < total) ? sbt->buflen : total;
		host->bytes = bytes;
		host->org_bytes = host->bytes;
		ret = send_packet(&sbt->io, sbt->host, sbt->net,
				  (char *)buf + offset, bytes);
		if (bytes != ret) {
			ErrorLog(
				"backup failure. buf_len:%d, [total %d bytes %d != ret %d]",
				buf_len, total, bytes, ret);
			return SBT_EC_FAIL;
		} else {
			InfoLog("backup success. buf_len:%d, [total %d bytes %d == ret %d]",
				buf_len, total, bytes, ret);
		}

		offset += bytes;
		total -= bytes;
	}

	return SBT_EC_SUCCESS;
}

sbtcode_t sbtclose(void *gvar_in)
{
	int ret = 0;
	int len = 0;
	int err = 0;
	int cmd_resp = 0;
	network_header_t *host = NULL;
	dmsbtex_t *sbt = (dmsbtex_t *)gvar_in;
	CHECK_CONFIG(sbt);
	InfoLog("come here");

	host = (network_header_t *)sbt->host;
	memset(host, 0x00, sizeof(*host));
	if (sbt->opt_type == OPT_BACKUP) {
		host->cmd = CMD_BACKUP_CLOSE;
		cmd_resp = CMD_BACKUP_CLOSE_RESP;
	} else if (sbt->opt_type == OPT_RESTORE) {
		host->cmd = CMD_RESTORE_CLOSE;
		cmd_resp = CMD_RESTORE_CLOSE_RESP;
	}
	host->bytes = 0;
	host->org_bytes = host->bytes;
	len = host->bytes;
		ret = send_packet(&sbt->io, sbt->host, sbt->net,
			  sbt->host + sizeof(*host), len);
	if (len != ret) {
		ErrorLog("sbt close failure. [len %d != ret %d]", len, ret);
		return SBT_EC_FAIL;
	}

		ret = recv_packet(&sbt->io, sbt->host, sbt->net,
			  sbt->host + sizeof(*host), sbt->buflen);
	err = *((int *)(sbt->host + sizeof(*host)));
	if (ret < 0 || host->cmd != cmd_resp || host->bytes != sizeof(ret) ||
	    err != 0) {
		ErrorLog(
			"sbt close failure. [ ret %d err %d cmd 0x%x bytes %d]",
			ret, err, host->cmd, host->bytes);
		return SBT_EC_FAIL;
	}
	return SBT_EC_SUCCESS;
}

sbtcode_t sbtinfo(void *gvar_in, sbtbfinfo_t **bak_file_info)
{
	dmsbtex_t *sbt = (dmsbtex_t *)gvar_in;
	CHECK_CONFIG(sbt);
	InfoLog("come here [%s]", sbt->backup_file);

	sbt->sbtbfinfo_out[0].sbtbfinfo_type = SBTBFINFO_NAME;
	sbt->sbtbfinfo_out[0].sbtbinfo_value = sbt->backup_file;
	sbt->sbtbfinfo_out[1].sbtbfinfo_type = SBTBFINFO_CRETIME;
	sbt->sbtbfinfo_out[1].sbtbinfo_value = sbt->create_time;
	sbt->sbtbfinfo_out[2].sbtbfinfo_type = SBTBFINFO_EXPTIME;
	sbt->sbtbfinfo_out[2].sbtbinfo_value = sbt->expire_time;
	sbt->sbtbfinfo_out[3].sbtbfinfo_type = SBTBFINFO_LABLE;
	sbt->sbtbfinfo_out[3].sbtbinfo_value = sbt->backup_volumlab;
	sbt->sbtbfinfo_out[4].sbtbfinfo_type = SBTBFINFO_COMMENT;
	sbt->sbtbfinfo_out[4].sbtbinfo_value = sbt->backup_comment;
	sbt->sbtbfinfo_out[5].sbtbfinfo_type = SBTBFINFO_END;
	sbt->sbtbfinfo_out[5].sbtbinfo_value = NULL;

	*bak_file_info = sbt->sbtbfinfo_out;
	return SBT_EC_SUCCESS;
}

sbtcode_t sbtend(void *gvar_in, sbtbool del_flag)
{
	int idx = 0;
	int err = SBT_EC_SUCCESS;
	dmsbtex_t *sbt = (dmsbtex_t *)gvar_in;
	InfoLog("come here del_flag [%s]", del_flag ? "TRUE" : "FALSE");

	if (del_flag == 1 && sbt->opt_type == OPT_BACKUP) {
		err = SBT_ERR_BACKUP;
	}
	for (idx = 0; idx < sbt->backup_dirs_num; ++idx) {
		if (sbt->backup_dirs[idx]) {
			free(sbt->backup_dirs[idx]);
		}
	}

	close_logger();
	if (sbt->agent > 0) {
		sbt_session_cleanup(&sbt->io);
		close(sbt->agent);
	}
	free(sbt->host);
	free(sbt->net);
	free(sbt);
	closelog();

	return err;
}

sbtcode_t sbtrestore(void *gvar_in, sbtchar *filename)
{
	int ret = 0;
	int len = 0;
	int err = 0;
	network_header_t *host = NULL;
	sbt_restore_open_t *open_host = NULL;
	sbt_restore_open_t *open_net = NULL;
	dmsbtex_t *sbt = (dmsbtex_t *)gvar_in;
	CHECK_CONFIG(sbt);
	InfoLog("come here [%s]", filename);
	sbt->opt_type = OPT_RESTORE;

	host = (network_header_t *)sbt->host;
	open_host = (sbt_restore_open_t *)(sbt->host + sizeof(*host));
	open_net = (sbt_restore_open_t *)(sbt->net + sizeof(*host));
	// if(sbt->sbtinit2_backupsets_info || strrchr((char *)filename, '.') == NULL)
	// {
	//     snprintf(open_host->open_file, sizeof(open_host->open_file), "%s.meta", filename);
	// }
	// else
	{
		snprintf(open_host->open_file, sizeof(open_host->open_file),
			 "%s", filename);
	}
	sbt_restore_open_hton(open_host, open_net);

	memset(host, 0x00, sizeof(*host));
	host->cmd = CMD_RESTORE_OPEN;
	host->bytes = sizeof(*open_net);
	host->org_bytes = host->bytes;
	memcpy(sbt->host + sizeof(*host), open_net, host->bytes);
	len = host->bytes;
	ret = send_packet(&sbt->io, sbt->host, sbt->net,
			  sbt->host + sizeof(*host), len);
	if (len != ret) {
		ErrorLog(
			"begin restore failure. open_host->open_file:%s, [len %d != ret %d]",
			open_host->open_file, len, ret);
		return SBT_EC_FAIL;
	} else {
		InfoLog("begin restore. open_host->open_file:%s, [len %d == ret %d]",
			open_host->open_file, len, ret);
	}

	memset(host, 0x00, sizeof(*host));
	ret = recv_packet(&sbt->io, sbt->host, sbt->net,
			  sbt->host + sizeof(*host), sbt->buflen);
	err = *((int *)(sbt->host + sizeof(*host)));
	if (ret <= 0 || host->cmd != CMD_RESTORE_OPEN_RESP ||
	    host->bytes != sizeof(ret) || err != 0) {
		ErrorLog(
			"begin restore failure. [ ret %d err %d cmd 0x%x bytes %d]",
			ret, err, host->cmd, host->bytes);
		return SBT_EC_FAIL;
	} else {
		InfoLog("begin restore success. [ ret %d err %d cmd 0x%x bytes %d]",
			ret, err, host->cmd, host->bytes);
	}

	return SBT_EC_SUCCESS;
}

sbtcode_t sbtread(void *gvar_in, sbtbyte *buf, sbtuint4 buf_len)
{
	int ret = 0;
	int len = 0;
	network_header_t *host = NULL;
	sbt_restore_read_t *read_host = NULL;
	sbt_restore_read_t *read_net = NULL;
	dmsbtex_t *sbt = (dmsbtex_t *)gvar_in;
	CHECK_CONFIG(sbt);
	InfoLog("come here [buf_len %d]", buf_len);

	host = (network_header_t *)sbt->host;
	read_host = (sbt_restore_read_t *)sbt->host + sizeof(*host);
	read_net = (sbt_restore_read_t *)sbt->net + sizeof(*host);

	memset(read_host, 0x00, sizeof(*read_host));
	read_host->read_bytes = buf_len;
	sbt_restore_read_hton(read_host, read_net);

	memset(host, 0x00, sizeof(*host));
	host->cmd = CMD_RESTORE;
	host->bytes = sizeof(*read_net);
	host->org_bytes = host->bytes;
	memcpy(sbt->host + sizeof(*host), read_net, host->bytes);
	len = host->bytes;
	ret = send_packet(&sbt->io, sbt->host, sbt->net,
			  sbt->host + sizeof(*host), len);
	if (len != ret) {
		ErrorLog("restore failure. [len %d != ret %d]", len, ret);
		return SBT_EC_FAIL;
	} else {
		InfoLog("restore. [len %d == ret %d]", len, ret);
	}

	memset(host, 0x00, sizeof(*host));
	ret = recv_packet(&sbt->io, sbt->host, sbt->net, (char *)buf,
			  buf_len);
	if (ret != buf_len || host->cmd != CMD_RESTORE_RESP ||
	    host->bytes != buf_len || buf_len != host->bytes) {
		ErrorLog(
			"begin restore failure. [ ret %d cmd 0x%x buf_len %u bytes %u]",
			ret, host->cmd, buf_len, host->bytes);
		return SBT_EC_FAIL;
	} else {
		InfoLog("begin restore success.  [ ret %d cmd 0x%x buf_len %u bytes %u]",
			ret, host->cmd, buf_len, host->bytes);
	}

	return SBT_EC_SUCCESS;
}

sbtcode_t sbterror(void *gvar_in, sbtchar **errdesc_out)
{
	dmsbtex_t *sbt = (dmsbtex_t *)gvar_in;
	CHECK_CONFIG(sbt);
	InfoLog("come here sbterror");
	return SBT_EC_SUCCESS;
}

sbtcode_t sbtcommand(void *gvar_in, sbtchar *cmdstr)
{
	dmsbtex_t *sbt = (dmsbtex_t *)gvar_in;
	CHECK_CONFIG(sbt);
	InfoLog("come here sbtcommand");
	return SBT_EC_SUCCESS;
}

sbtcode_t sbtdelete(void *gvar_in, sbtchar *filename)
{
	dmsbtex_t *sbt = (dmsbtex_t *)gvar_in;
	CHECK_CONFIG(sbt);
	InfoLog("come here");
	return SBT_EC_SUCCESS;
}

/////////////////////////////////////////////////////////////////////////////////////////////////////
/**
 * read configure file for parameters
 */

int init_sbt_config(const char *cfg, dmsbtex_t *sbt)
{
	int err = -1;
	int bytes = 0;
	int idx = 0;
	int fd = -1;
	const int BUFLEN = 0x400000;
	char *buff = NULL;
	char backup_dir[256] = { 0 };
	const char *first = NULL;
	const char *pos = NULL;
	int64_t file_size = 0;
	/* T0367：从 sbt-config.conf 解析 mTLS 状态与算法（覆盖 env/ini 基线） */
	int file_mtls = 0;
	int file_mtls_present = 0;
	int file_alg_present = 0;
	char file_alg[128];

	fd = open(cfg, O_RDONLY);
	if (fd < 0) {
		syslog(LOG_ERR, "open %s failure. status: %s(errno: %d)\n", cfg,
		       strerror(errno), errno);
		return -1;
	}

	buff = (char *)malloc(BUFLEN);
	if (buff == NULL) {
		syslog(LOG_ERR, "malloc %p failure. for %s\n", buff, cfg);
		goto return__;
	}

	file_size = lseek(fd, 0, SEEK_END);
	lseek(fd, 0, SEEK_SET);
	bytes = read(fd, buff, BUFLEN);
	if (bytes != file_size) {
		syslog(LOG_ERR, "bad %s\n", cfg);
		goto return__;
	}
	buff[bytes] = 0x00;
	first = buff;

	snprintf(sbt->log_path, sizeof(sbt->log_path), "sbt-log");
	pos = strstr(first, "--log-path");
	if (pos == NULL) {
		syslog(LOG_ERR, "error %s [%s]\n", cfg, first);
		goto return__;
	}
	pos += 10;
	while ((*pos == ' ' || *pos == '\t' || *pos == '=') && *pos != 0x00)
		++pos;
	idx = 0;
	while (*pos != ' ' && *pos != '\t' && *pos != '\r' && *pos != '\n' &&
	       *pos != '#' && *pos != 0x00 &&
	       idx < (sizeof(sbt->log_path) - 1)) {
		sbt->log_path[idx] = *pos;
		++idx;
		++pos;
	}
	sbt->log_path[idx] = 0x00;

	pos = strstr(first, "--host");
	if (pos == NULL) {
		syslog(LOG_ERR, "bad %s [%s]\n", cfg, first);
		goto return__;
	}
	pos += 6;
	while ((*pos == ' ' || *pos == '\t' || *pos == '=') && *pos != 0x00)
		++pos;
	idx = 0;
	while (*pos != ' ' && *pos != '\t' && *pos != '\r' && *pos != '\n' &&
	       *pos != '#' && *pos != 0x00 && idx < (sizeof(sbt->srv_ip) - 1)) {
		sbt->srv_ip[idx] = *pos;
		++idx;
		++pos;
	}
	sbt->srv_ip[idx] = 0x00;

	pos = strstr(first, "--port");
	if (pos == NULL) {
		syslog(LOG_ERR, "bad %s [%s]\n", cfg, first);
		goto return__;
	}
	pos += 6;
	while ((*pos == ' ' || *pos == '\t' || *pos == '=') && *pos != 0x00)
		++pos;
	sbt->srv_port = atoi(pos);

	pos = strstr(first, "--checksum-enabled");
	if (pos == NULL) {
		syslog(LOG_ERR, "bad %s [%s]\n", cfg, first);
		goto return__;
	}
	pos += 18;
	while ((*pos == ' ' || *pos == '\t' || *pos == '=') && *pos != 0x00)
		++pos;
	sbt->checksum_enabled = atoi(pos);

	pos = strstr(first, "--compress-enabled");
	if (pos == NULL) {
		syslog(LOG_ERR, "bad %s [%s]\n", cfg, first);
		goto return__;
	}
	pos += 18;
	while ((*pos == ' ' || *pos == '\t' || *pos == '=') && *pos != 0x00)
		++pos;
	sbt->compress_enabled = atoi(pos);

	/* T0367：先以 sbt_tls_config_init 初始化（env/ini 基线），
	 * 再仅覆盖配置文件中存在的 mTLS 键；键缺失则跳过（保留 env/ini）。
	 * 值非法：fail-closed 返回 -1。置于 backup-dirs 之前，
	 * 避免 --backup-dirs 缺失时的 goto next__ 跳过解析。 */
	pos = strstr(first, "--mtls-enabled");
	if (pos != NULL) {
		pos += 14;
		while ((*pos == ' ' || *pos == '\t' || *pos == '=') && *pos != 0x00)
			++pos;
		file_mtls = atoi(pos);
		if (file_mtls != 0 && file_mtls != 1) {
			syslog(LOG_ERR, "bad %s: invalid --mtls-enabled\n", cfg);
			goto return__;
		}
		file_mtls_present = 1;
	}

	pos = strstr(first, "--tls-algorithm");
	if (pos != NULL) {
		pos += 15;
		while ((*pos == ' ' || *pos == '\t' || *pos == '=') && *pos != 0x00)
			++pos;
		idx = 0;
		while (*pos != ' ' && *pos != '\t' && *pos != '\r' &&
		       *pos != '\n' && *pos != '#' && *pos != 0x00 &&
		       idx < (sizeof(file_alg) - 1)) {
			file_alg[idx] = *pos;
			++idx;
			++pos;
		}
		file_alg[idx] = 0x00;
		if (strcmp(file_alg, RPC_TLS_ALGORITHM_SM4_GCM_SM3) != 0 &&
		    strcmp(file_alg, RPC_TLS_ALGORITHM_AES_256_GCM_SHA384) != 0) {
			syslog(LOG_ERR, "bad %s: unknown --tls-algorithm %s\n",
			       cfg, file_alg);
			goto return__;
		}
		file_alg_present = 1;
	}

	sbt->backup_dirs_num = 0;
	memset(sbt->backup_dirs, 0x00, sizeof(sbt->backup_dirs));
	pos = strstr(first, "--backup-dirs");
	if (pos == NULL) {
		syslog(LOG_INFO, "info %s [%s]\n", cfg, first);
		goto next__;
	}
	pos += 13;
	while ((*pos == ' ' || *pos == '\t' || *pos == '=') && *pos != 0x00)
		++pos;
	while (*pos != ' ' && *pos != '\t' && *pos != '\r' && *pos != '\n' &&
	       *pos != '#' && *pos != 0x00) {
		idx = 0;
		while (*pos != ',' && *pos != ';' && *pos != ' ' &&
		       *pos != '\t' && *pos != '\r' && *pos != '\n' &&
		       *pos != '#' && *pos != 0x00 &&
		       idx < (sizeof(backup_dir) - 1)) {
			backup_dir[idx] = *pos;
			++idx;
			++pos;
		}
		if (1 < idx) {
			backup_dir[idx] = 0x00;
			sbt->backup_dirs[sbt->backup_dirs_num] =
				strdup(backup_dir);
			if (sbt->backup_dirs[sbt->backup_dirs_num] == NULL) {
				syslog(LOG_INFO,
				       "error for string dup %s %s [%s]\n", cfg,
				       backup_dir, first);
			}
			++sbt->backup_dirs_num;
		}

		if (*pos == ',' || *pos == ';') {
			++pos;
		}
	}

next__:
	/* 基线：cert_dir + mtls/algorithm 先由 env/ini 初始化（sbt_tls_config_init）。
	 * 解析失败不阻断：以默认 cert_dir 兜底，文件键仍可在下方生效。 */
	if (sbt_tls_config_init(&sbt->tls_cfg) != 0) {
		memset(&sbt->tls_cfg, 0, sizeof(sbt->tls_cfg));
		snprintf(sbt->tls_cfg.cert_dir, sizeof(sbt->tls_cfg.cert_dir),
			 "%s", DEFAULT_CERT_DIR);
	}
	/* 仅覆盖配置文件中存在的键；键缺失则保留 env/ini 基线。 */
	if (file_mtls_present)
		sbt->tls_cfg.mtls_enabled = file_mtls;
	if (file_alg_present) {
		snprintf(sbt->tls_cfg.algorithm_name,
			 sizeof(sbt->tls_cfg.algorithm_name), "%s", file_alg);
		sbt->tls_cfg.algorithm = dm_hs_algorithm_from_name(file_alg);
	}
	err = 0;
return__:
	free(buff);
	close(fd);
	return err;
}
