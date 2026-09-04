#include "buf.h"
#include "common.h"
#include "logger.h"
#include "rpc-command.h"
#include "rpc-common.h"
#include "rpc-config.h"
#include "rpc-io.h"
#include "rpc-protocol.h"
#include "lz4.h"
#include "file-stat.h"
#include "rpc.h"
#include "dev_ioctl.h"
#include "rpc-conn.h"
#include "crypt.h"

#include <dirent.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <sys/types.h>
#include <netinet/tcp.h>
#include <limits.h>
#include <string.h>
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <unistd.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <sys/sendfile.h>
#include <sys/wait.h>
#include <time.h>
#include <string>

struct trans_handle {
	int fd;
	int sockfd;
	char *host_buf;
	char *net_buf;
	char *host_resp_buf;
	char *net_resp_buf;
	/** compress enabled 0 disabled, 1 enabled default: 1*/
	unsigned int is_compress;
	/** encrypt enabled  0 disabled, 1 enabled default: 0*/
	unsigned int is_encrypt;
	/** checksum enabled 0 disabled, 1 enabled default: 0*/
	unsigned int is_checksum;
	struct stat st;
	char remote_file[512];
	char local_file[512];
	struct session_info *session;
	trans_handle()
	{
		memset(this, 0x00, sizeof(*this));

		fd = -1;
		sockfd = -1;
		host_buf = new char[MSG_BUFF_LEN];
		net_buf = new char[MSG_BUFF_LEN];
		host_resp_buf = new char[MSG_BUFF_LEN];
		net_resp_buf = new char[MSG_BUFF_LEN];
		reset_buf();
	}
	~trans_handle()
	{
		if (fd != -1) {
			close(fd);
		}

		if ((sockfd != -1) && (session == NULL)) {
			close(sockfd);
		}

		delete[] host_buf;
		delete[] net_buf;
		delete[] host_resp_buf;
		delete[] net_resp_buf;
	}
	void reset_buf()
	{
		memset(host_buf, 0x00, MSG_BUFF_LEN);
		memset(net_buf, 0x00, MSG_BUFF_LEN);
		memset(host_resp_buf, 0x00, MSG_BUFF_LEN);
		memset(net_resp_buf, 0x00, MSG_BUFF_LEN);
	}
};

int rpc_key_verify(struct session_info *session, const char *key)
{
	int ret = 0;
	int sockfd = session->sockfd;
	msg_key_verify_resp_t msg_resp;
	char net_buf[256];
	char host_buf[256];

	if (key == NULL || strlen(key) == 0) {
		ErrorLog("key is empty");
		return -1;
	}

	size_t key_len = strlen(key);
	if (key_len > 240) {
		ErrorLog("key too long, max 240 characters");
		return -1;
	}

	msg_key_verify_t *msg_req_host = (msg_key_verify_t *)host_buf;
	msg_key_verify_t *msg_req_net = (msg_key_verify_t *)net_buf;
	msg_req_host->key_len = key_len;
	memcpy(msg_req_host->key, key, msg_req_host->key_len);
	data_encrypt((unsigned char *)msg_req_host->key, msg_req_host->key_len);

	msg_key_verify_hton(msg_req_host, msg_req_net);

	int msg_size = sizeof(msg_base_t) + sizeof(unsigned int) +
		       msg_req_host->key_len;
	ret = rpc_send(sockfd, net_buf, msg_size, 0);
	if (ret < 0) {
		ErrorLog("send key verify request failed, ret=%d", ret);
		return -1;
	}

	ret = rpc_recv(sockfd, host_buf, sizeof(msg_key_verify_resp_t), 0);
	if (ret < 0) {
		ErrorLog("recv key verify response failed, ret=%d", ret);
		return -1;
	}

	msg_key_verify_resp_ntoh(&msg_resp, (msg_key_verify_resp_t *)host_buf);

	if (msg_resp.err != 0) {
		ErrorLog("key verification failed");
		return -1;
	}

	return 0;
}

struct session_info *rpc_session_start(rpc_args *rpc)
{
	session_info *session = new session_info();
	session->rpc = rpc;

	session->sockfd = connect_server(rpc->svr_ip, rpc->svr_port,
					 rpc->local_ip, rpc->local_port);
	if (session->sockfd < 0) {
		goto error__;
	}

	return session;
error__:
	delete session;
	return NULL;
}

int rpc_session_restart(struct session_info *session)
{
	int ret = 0;
	struct rpc_args *rpc = session->rpc;

	close(session->sockfd);
	session->sockfd = -1;

	session->sockfd = connect_server(rpc->svr_ip, rpc->svr_port,
					 rpc->local_ip, rpc->local_port);
	if (session->sockfd < 0) {
		ret = session->sockfd;
		goto error__;
	}

error__:
	return ret;
}

int rpc_session_stop(struct session_info *session)
{
	int ret = 0;

	if (session->sockfd > 0) {
		close(session->sockfd);
	}

	session->sockfd = -1;

	delete session;

	return ret;
}

int rpc_download_block_start(struct session_info *session,
			     const download_info_t *info__, trans_t *t__)
{
	int ret = -1;
	char *pos = NULL;
	char path[1024] = { 0 };
	trans_handle *trans = new trans_handle();
	msg_download_block_t *host = (msg_download_block_t *)trans->host_buf;
	msg_download_block_t *net = (msg_download_block_t *)trans->net_buf;
	msg_download_block_resp_t *resp_host =
		(msg_download_block_resp_t *)trans->host_resp_buf;
	msg_download_block_resp_t *resp_net =
		(msg_download_block_resp_t *)trans->net_resp_buf;

	*t__ = NULL;

	snprintf(path, sizeof(path), "%s", info__->local_file);
	pos = strrchr(path, '/');
	if (pos) {
		*pos = 0x00;
	}
	create_dir(path, 0777);
	if (g_rpc_config->check_data) {
		trans->fd = open(info__->local_file,
				 O_WRONLY | O_CREAT | O_SYNC | O_TRUNC, 0666);
	} else {
		trans->fd = open(info__->local_file,
				 O_WRONLY | O_CREAT | O_TRUNC, 0666);
	}
	strncpy(trans->local_file, info__->local_file,
		sizeof(trans->local_file));
	if (trans->fd < 0) {
		ErrorLog("open:[%s] failure", info__->local_file);
		goto return__;
	}
	strcpy(trans->remote_file, info__->remote_file);

	trans->session = session;
	trans->sockfd = session->sockfd;

	host->opt_type = 1; /**open only*/
	trans->is_compress = host->is_compress = info__->is_compress;
	trans->is_encrypt = host->is_encrypt = info__->is_encrypt;
	trans->is_checksum = host->is_checksum = info__->is_checksum;
	host->bolck_num = 0;
	strcpy(host->data, info__->remote_file);
	host->data_len = strlen(host->data);
	msg_download_block_hton(host, net);
	if (rpc_send(trans->sockfd, net, host->uiLEN, 0) != (int)host->uiLEN) {
		ErrorLog("rpc send download block failure: %s(errno: %d)",
			 strerror(errno), errno);
		goto return__;
	}
	ret = read_is_ready(trans->sockfd, g_rpc_config->read_timeout);
	if (ret <= 0) {
		ErrorLog("recv request response time out.");
		ret = -1;
		goto return__;
	}
	if (rpc_recv(trans->sockfd, resp_net, MSG_BUFF_LEN, 0) < 0) {
		ErrorLog("rpc recv failure: %s(errno: %d)", strerror(errno),
			 errno);
		goto return__;
	}
	msg_download_block_resp_ntoh(resp_host, resp_net);
	if ((resp_host->uiResult != 0) ||
	    (resp_host->uiMT != (MT_EXECUTE_DOWNLOAD_BLOCK_RESP))) {
		ret = resp_host->uiResult;
		if (ret == 2222) {
			ErrorLog(
				"Warning [%s] not existed. [ret: %d, MT: 0x%x]",
				info__->remote_file, resp_host->uiResult,
				resp_host->uiMT);
		} else {
			ErrorLog(
				"rpc download block request start failure: %s  [ret: %d, "
				"MT: 0x%x]",
				info__->remote_file, resp_host->uiResult,
				resp_host->uiMT);
		}
		goto return__;
	}

	file_stat_ntoh(resp_host->data, &resp_host->data_len, &trans->st);
	*t__ = trans;
	ret = 0;
return__:
	if (ret && trans) {
		if (ret == 2222) {
			ret = EIO;
		}
		delete trans;
	}
	return ret;
}

int rpc_download_block(trans_t t__, block_info_t *blocks, const int num)
{
	int ret = -1;
	int64_t all_size = 0;
	int r_num = 0;
	int64_t recv_bytes = 0;
	const int buflen = (MSG_BUFF_LEN - 2048);
	data_block_t *block = NULL;
	trans_handle *trans = dynamic_cast<trans_handle *>((trans_handle *)t__);
	if (!trans) {
		return 0;
	} else if (num < 1) {
		ErrorLog("block num %d too short.", num);
		return -1;
	}
	if ((int)(buflen / sizeof(blocks[0])) < num) /** max num 32,640 **/
	{
		ErrorLog("block num %d too big.", num);
		return -1;
	}

	const unsigned int is_compress = trans->is_compress;
	const unsigned int is_encrypt = trans->is_encrypt;
	const unsigned int is_checksum = trans->is_checksum;
	msg_download_block_t *host = (msg_download_block_t *)trans->host_buf;
	msg_download_block_t *net = (msg_download_block_t *)trans->net_buf;
	msg_download_block_resp_t *resp_host =
		(msg_download_block_resp_t *)trans->host_resp_buf;
	msg_download_block_resp_t *resp_net =
		(msg_download_block_resp_t *)trans->net_resp_buf;
	trans->reset_buf();

	host->opt_type = 2; /**read only*/
	host->is_compress = is_compress;
	host->is_encrypt = is_encrypt;
	host->is_checksum = is_checksum;
	host->bolck_num = 0;
	host->data_len = sizeof(blocks[0]) * num;
	memcpy(host->data, blocks, host->data_len);

	all_size += host->data_len;

	block = (data_block_t *)host->data;

	if (g_rpc_config->check_data) {
		fprintf(stdout, "srcFile:%s download block: [",
			trans->local_file);
	}
	for (int i = 0; i < num; ++i) {
		if (g_rpc_config->check_data) {
			fprintf(stdout, "(offset:%lu, size:%lu)",
				block[i].offset, block[i].size);
		}
		all_size += block[i].size;
	}

	if (g_rpc_config->check_data) {
		fprintf(stdout, "]\n");
	}
	fflush(stdout);
	for (int i = 0; i < num; ++i) {
		if (buflen < (int)block[i].size) {
			ErrorLog("error: buflen: %d < block size: %ld .",
				 buflen, block[i].size);
			return -1;
		}
		data_block_hton(&block[i]);
		++host->bolck_num;
	}

	if (!write_is_ready(trans->sockfd, g_rpc_config->read_timeout)) {
		ErrorLog("send download %s data request failure for time out.",
			 trans->remote_file);
		goto return__;
	}
	msg_download_block_hton(host, net);
	if (rpc_send(trans->sockfd, net, host->uiLEN, 0) != (int)host->uiLEN) {
		ErrorLog("rpc send download block failure: %s(errno: %d)",
			 strerror(errno), errno);
		goto return__;
	}

	r_num = 0;
	while (r_num < num) {
		if (read_is_ready(trans->sockfd, g_rpc_config->read_timeout) ==
		    false) {
			ErrorLog("recv request response time out.");
			goto return__;
		}
		if (rpc_recv(trans->sockfd, resp_net, MSG_BUFF_LEN, 0) < 0) {
			ErrorLog("rpc recv failure: %s(errno: %d)",
				 strerror(errno), errno);
			goto return__;
		}
		msg_download_block_resp_ntoh(resp_host, resp_net);
		if ((resp_host->uiResult != 0) ||
		    (resp_host->uiMT != (MT_EXECUTE_DOWNLOAD_BLOCK_RESP))) {
			ErrorLog("rpc download block request failure: %s",
				 trans->remote_file);
			goto return__;
		}

		if (is_encrypt) {
			if (is_compress) {
				data_dencrypt((unsigned char *)resp_net->data,
					      resp_host->data_len);
			} else {
				data_dencrypt((unsigned char *)resp_host->data,
					      resp_host->data_len);
			}
		}

		if (is_compress) {
			resp_host->data_len = LZ4_decompress_safe(
				resp_net->data, resp_host->data,
				resp_host->data_len, MSG_BUFF_LEN);
			if (resp_host->data_len != resp_host->original_len) {
				ErrorLog(
					"decompress data for %s failure data_len: %u != "
					"original_len: %u",
					trans->remote_file, resp_host->data_len,
					resp_host->original_len);
				goto return__;
			}
		}

		if (is_checksum) {
			unsigned int checksum = 0;
			for (unsigned int i = 0; i < resp_host->data_len; ++i) {
				checksum += resp_host->data[i];
			}
			if (checksum != resp_host->checksum) {
				ErrorLog(
					"download file [%s] write failure for [checksum: %u != "
					"host->checksum :%u]",
					trans->remote_file, checksum,
					resp_host->checksum);
				goto return__;
			}
		}

		if (write(trans->fd, resp_host->data, resp_host->data_len) !=
		    (ssize_t)resp_host->data_len) {
			ErrorLog("rpc write failure: %s(errno: %d)",
				 strerror(errno), errno);
			goto return__;
		}
		recv_bytes += resp_host->data_len;
		InfoLog("original_len: %ld, data_len: %ld",
			resp_host->original_len, resp_host->data_len);
		r_num += resp_host->bolck_num;
	}

	if (g_rpc_config->check_data) {
		int fd = 0;
		mode_t mode = 0777;
		struct stat st = { 0 };
		fd = open(trans->local_file, O_RDONLY, mode);
		if (fd < 0) {
			ErrorLog("fstat %s failure: %s(errno: %d)",
				 trans->local_file, strerror(errno), errno);
			return -EIO;
		}

		if (fstat(fd, &st) != 0) {
			ErrorLog("fstat %s failure: %s(errno: %d)",
				 trans->local_file, strerror(errno), errno);
			close(fd);
			return -EIO;
		}

		if (st.st_size != recv_bytes) {
			ErrorLog(
				"block download check [%s] failure: recv_bytes:%ld != st.st_size:%ld",
				trans->local_file, recv_bytes, st.st_size);
			close(fd);
			return -EIO;
		} else {
			InfoLog("block download check [%s] success: recv_bytes:%ld == st.st_size:%ld change time:%ld.%ld\n",
				trans->local_file, recv_bytes, st.st_size,
				st.st_ctime, st.st_ctim.tv_nsec);
		}
		close(fd);
	}
	if (all_size != recv_bytes) {
		ret = EIO;
		WarningLog(
			"block download [%s] Warning: all_size:%ld != recv_bytes:%ld\n",
			trans->local_file, all_size, recv_bytes);
	} else {
		ret = 0;
	}
return__:
	return ret;
}

int rsync_download_block(trans_t t__, block_info_t *blocks, const int num)
{
	int ret = -1;
	char *buf = NULL;
	int offset = 0;
	int r_num = 0;
	int64_t bytes = 0;
	int64_t total_write = 0;
	int try_times = 0;
	const int buflen = (MSG_BUFF_LEN - 2048);
	data_block_t *block = NULL;
	trans_handle *trans = dynamic_cast<trans_handle *>((trans_handle *)t__);
	if (!trans) {
		ErrorLog("bad bolck trans handle.");
		return -10;
	} else if (num < 1) {
		ErrorLog("block num %d too short.", num);
		return -20;
	}
	if ((int)(buflen / sizeof(blocks[0])) < num) /** max num 32,640 **/
	{
		ErrorLog("block num %d too big.", num);
		return -30;
	}

	const unsigned int is_compress = trans->is_compress;
	const unsigned int is_encrypt = trans->is_encrypt;
	const unsigned int is_checksum = trans->is_checksum;
	msg_download_block_t *host = (msg_download_block_t *)trans->host_buf;
	msg_download_block_t *net = (msg_download_block_t *)trans->net_buf;
	msg_download_block_resp_t *resp_host =
		(msg_download_block_resp_t *)trans->host_resp_buf;
	msg_download_block_resp_t *resp_net =
		(msg_download_block_resp_t *)trans->net_resp_buf;
	trans->reset_buf();

	host->opt_type = 2; /**read only*/
	host->is_compress = is_compress;
	host->is_encrypt = is_encrypt;
	host->is_checksum = is_checksum;
	host->bolck_num = 0;
	host->data_len = sizeof(blocks[0]) * num;
	memcpy(host->data, blocks, host->data_len);

	block = (data_block_t *)host->data;
	for (int i = 0; i < num; ++i) {
		if (buflen < (int)block[i].size) {
			ErrorLog("error: buflen: %d < block size: %ld .",
				 buflen, block[i].size);
			return -40;
		}
		data_block_hton(&block[i]);
		++host->bolck_num;
	}

	if (!write_is_ready(trans->sockfd, g_rpc_config->read_timeout)) {
		ErrorLog("send download %s data request failure for time out.",
			 trans->remote_file);
		goto return__;
	}
	msg_download_block_hton(host, net);
	if (rpc_send(trans->sockfd, net, host->uiLEN, 0) != (int)host->uiLEN) {
		ErrorLog("rpc send download block failure: %s(errno: %d",
			 strerror(errno), errno);
		goto return__;
	}

	r_num = 0;
	while (r_num < num) {
		if (read_is_ready(trans->sockfd, g_rpc_config->read_timeout) ==
		    false) {
			ErrorLog("recv request response time out.");
			goto return__;
		}
		if (rpc_recv(trans->sockfd, resp_net, MSG_BUFF_LEN, 0) < 0) {
			ErrorLog("rpc recv failure: %s(errno: %d)",
				 strerror(errno), errno);
			goto return__;
		}
		msg_download_block_resp_ntoh(resp_host, resp_net);
		if ((resp_host->uiResult != 0) ||
		    (resp_host->uiMT != (MT_EXECUTE_DOWNLOAD_BLOCK_RESP))) {
			ErrorLog("rsync download block request failure: %s",
				 trans->remote_file);
			goto return__;
		}

		if (is_encrypt) {
			if (is_compress) {
				data_dencrypt((unsigned char *)resp_net->data,
					      resp_host->data_len);
			} else {
				data_dencrypt((unsigned char *)resp_host->data,
					      resp_host->data_len);
			}
		}

		if (is_compress) {
			resp_host->data_len = LZ4_decompress_safe(
				resp_net->data, resp_host->data,
				resp_host->data_len, MSG_BUFF_LEN);
			if (resp_host->data_len != resp_host->original_len) {
				ErrorLog(
					"decompress data for %s failure data_len: %u != "
					"original_len: %u",
					trans->remote_file, resp_host->data_len,
					resp_host->original_len);
				goto return__;
			}
		}

		if (is_checksum) {
			unsigned int checksum = 0;
			for (unsigned int i = 0; i < resp_host->data_len; ++i) {
				checksum += resp_host->data[i];
			}
			if (checksum != resp_host->checksum) {
				ErrorLog(
					"download file [%s] write failure for [checksum: %u != "
					"host->checksum :%u]",
					trans->remote_file, checksum,
					resp_host->checksum);
				goto return__;
			}
		}

#if 1
		offset = 0;
		for (int i = 0; i < (int)resp_host->bolck_num &&
				offset < (int)resp_host->data_len;
		     ++i) {
			block = (data_block_t *)(resp_host->data + offset);
			data_block_ntoh(block);
			offset += sizeof(*block);

			buf = resp_host->data + offset;
			offset += block->size;
			if (0 < block->size) {
				try_times = 0;
				total_write = 0;
				do {
					bytes = pwrite(
						trans->fd, buf + total_write,
						block->size - total_write,
						block->offset + total_write);
					if (0 <= bytes) {
						total_write += bytes;
					} else {
						ErrorLog(
							"rpc write bytes: %ld failure: %s(errno: %d)",
							bytes, strerror(errno),
							errno);
						break;
					}
					/* code */
				} while (total_write < (ssize_t)block->size &&
					 ++try_times < 10);

				if (total_write != (ssize_t)block->size) {
					ErrorLog(
						"rpc write failure: %s(errno: %d)",
						strerror(errno), errno);
					goto return__;
				}
			}
		}
		if (offset != (int)resp_host->data_len) {
			ErrorLog(
				"rsync download block request failure for offset: %d != "
				"resp_host->data_len: %u",
				offset, resp_host->data_len);
			goto return__;
		}
#else
		if (write(trans->fd, resp_host->data, resp_host->data_len) !=
		    (ssize_t)resp_host->data_len) {
			fprintf(stderr, "rpc write failure: %s(errno: %d)\n",
				strerror(errno), errno);
			goto return__;
		}
#endif
		r_num += resp_host->bolck_num;
	}
	ret = 0;
return__:
	return ret;
}

int rpc_download_block_finish(trans_t t__)
{
	int ret = -1;
	mode_t mode = 0777;
	unsigned int gid = 0;
	unsigned int uid = 0;
	rpc_timespec_t atim = { 0 }; /* Time of last access.  */
	rpc_timespec_t mtim = { 0 }; /* Time of last modification.  */
	rpc_timespec_t ctim = { 0 }; /* Time of last status change.  */
	trans_handle *trans = dynamic_cast<trans_handle *>((trans_handle *)t__);
	if (!trans) {
		return 0;
	}
	msg_download_block_t *host = (msg_download_block_t *)trans->host_buf;
	msg_download_block_t *net = (msg_download_block_t *)trans->net_buf;
	msg_download_block_resp_t *resp_host =
		(msg_download_block_resp_t *)trans->host_resp_buf;
	msg_download_block_resp_t *resp_net =
		(msg_download_block_resp_t *)trans->net_resp_buf;
	trans->reset_buf();

	host->opt_type = 3; /**close only*/
	host->is_compress = trans->is_compress;
	host->is_encrypt = trans->is_encrypt;
	host->is_checksum = trans->is_checksum;
	host->bolck_num = 0;
	host->data_len = 0;
	msg_download_block_hton(host, net);
	if (rpc_send(trans->sockfd, net, host->uiLEN, 0) != (int)host->uiLEN) {
		ErrorLog(
			"rpc send download block finish failure: %s(errno: %d)",
			strerror(errno), errno);
		goto return__;
	}
	ret = read_is_ready(trans->sockfd, g_rpc_config->read_timeout);
	if (ret <= 0) {
		ErrorLog("recv request response time out.");
		ret = -1;
		goto return__;
	}
	if (rpc_recv(trans->sockfd, resp_net, MSG_BUFF_LEN, 0) < 0) {
		ErrorLog("rpc recv failure: %s(errno: %d)", strerror(errno),
			 errno);
		goto return__;
	}
	msg_download_block_resp_ntoh(resp_host, resp_net);
	if ((resp_host->uiResult != 0) ||
	    (resp_host->uiMT != (MT_EXECUTE_DOWNLOAD_BLOCK_RESP))) {
		ErrorLog("rpc download block finish request failure: %s ",
			 trans->remote_file);
		goto return__;
	}
	mode = trans->st.st_mode;
	gid = trans->st.st_gid;
	uid = trans->st.st_uid;
	atim.tv_sec = trans->st.st_atim.tv_sec;
	atim.tv_nsec = trans->st.st_atim.tv_nsec;
	mtim.tv_sec = trans->st.st_mtim.tv_sec;
	mtim.tv_nsec = trans->st.st_mtim.tv_nsec;
	ctim.tv_sec = trans->st.st_ctim.tv_sec;
	ctim.tv_nsec = trans->st.st_ctim.tv_nsec;
	if (FileStat::GetInstance()->UpdateFileStatTime(trans->fd, atim, mtim,
							ctim, mode, gid, uid)) {
		ErrorLog("download failure for update file: %s stat",
			 trans->remote_file);
		goto return__;
	}

	ret = 0;
return__:
	delete trans;
	return ret;
}

int rpc_upload_block_start(const upload_info_t *info__, trans_t *t__)
{
	int ret = -1;
	trans_handle *trans = new trans_handle();
	msg_upload_block_t *host = (msg_upload_block_t *)trans->host_buf;
	msg_upload_block_t *net = (msg_upload_block_t *)trans->net_buf;
	msg_upload_block_resp_t *resp_host =
		(msg_upload_block_resp_t *)trans->host_resp_buf;
	msg_upload_block_resp_t *resp_net =
		(msg_upload_block_resp_t *)trans->net_resp_buf;

	*t__ = NULL;
	if (stat(info__->local_file, &trans->st)) {
		ErrorLog("stat file:[%s] failure", info__->local_file);
		goto return__;
	}
	trans->fd = open(info__->local_file, O_RDONLY);
	if (trans->fd < 0) {
		ErrorLog("open:[%s] failure", info__->local_file);
		goto return__;
	}
	strcpy(trans->remote_file, info__->remote_file);

	trans->session = info__->session;
	trans->sockfd = info__->session->sockfd;

	host->opt_type = 1; /**open only*/
	trans->is_compress = host->is_compress = info__->is_compress;
	trans->is_encrypt = host->is_encrypt = info__->is_encrypt;
	trans->is_checksum = host->is_checksum = info__->is_checksum;
	host->bolck_num = 0;
	strcpy(host->data, info__->remote_file);
	host->data_len = strlen(host->data);
	msg_upload_block_hton(host, net);
	if (rpc_send(trans->sockfd, net, host->uiLEN, 0) != (int)host->uiLEN) {
		ErrorLog("rpc send failure: %s(errno: %d)", strerror(errno),
			 errno);
		goto return__;
	}

	ret = read_is_ready(trans->sockfd, g_rpc_config->read_timeout);
	if (ret <= 0) {
		ErrorLog("recv request response time out.");
		ret = -1;
		goto return__;
	}
	if (rpc_recv(trans->sockfd, resp_net, MSG_BUFF_LEN, 0) < 0) {
		ErrorLog("rpc recv failure: %s(errno: %d)", strerror(errno),
			 errno);
		goto return__;
	}
	msg_upload_block_resp_ntoh(resp_host, resp_net);
	if ((resp_host->uiResult != 0) ||
	    (resp_host->uiMT != MT_EXECUTE_UPLOAD_BLOCK_RESP)) {
		ErrorLog(
			"rpc upload block request failure: %s  [ret: %d, MT: 0x%x]",
			info__->remote_file, resp_host->uiResult,
			resp_host->uiMT);
		goto return__;
	}

	*t__ = trans;
	ret = 0;
return__:
	if (ret && trans) {
		delete trans;
	}
	return ret;
}
int rsync_upload_block(trans_t t__, block_info_t *blocks, const int num)
{
	int ret = -1;
	int bytes = 0;
	int offset = 0;
	int b_offet = 0;
	const int block_size = (MSG_BUFF_LEN - 2048);
	char *buf = NULL;
	data_block_t *block = NULL;
	trans_handle *trans = dynamic_cast<trans_handle *>((trans_handle *)t__);
	if (!trans) {
		ErrorLog("bad bolck trans handle.");
		return -10;
	} else if (num < 1) {
		ErrorLog("block num %d too short.", num);
		return -20;
	}

	const unsigned int is_compress = trans->is_compress;
	const unsigned int is_encrypt = trans->is_encrypt;
	const unsigned int is_checksum = trans->is_checksum;
	int connfd = trans->sockfd;
	int fd = trans->fd;
	msg_upload_block_t *host = (msg_upload_block_t *)trans->host_buf;
	msg_upload_block_t *net = (msg_upload_block_t *)trans->net_buf;
	trans->reset_buf();

	b_offet = 0;
	while (b_offet < num) {
		bytes = 0;
		offset = 0;
		host->bolck_num = 0;
		for (; b_offet < num && offset < block_size; ++b_offet) {
			if (block_size <=
			    (int)(offset + blocks[b_offet].size)) {
				break;
			}

			block = (data_block_t *)(host->data + offset);
			offset += sizeof(*block);

			buf = host->data + offset;
			block->offset = blocks[b_offet].offset;
			block->size = bytes = pread(fd, buf,
						    blocks[b_offet].size,
						    blocks[b_offet].offset);
			if (bytes < 0) {
				ret = -1;
				ErrorLog(
					"pread data failure %s(errno: %d) size: %lu offset: %lu",
					strerror(errno), errno,
					blocks[b_offet].size,
					blocks[b_offet].offset);
				goto return__;
			}
			offset += bytes;
			data_block_hton(block);
			++host->bolck_num;
		}

		host->opt_type = 2;
		host->original_len = host->data_len = offset;
		host->is_compress = is_compress;
		host->is_encrypt = is_encrypt;
		host->is_checksum = is_checksum;

		if (is_checksum) {
			host->checksum = 0;
			for (unsigned int i = 0; i < host->data_len; ++i) {
				host->checksum += host->data[i];
			}
		}

		/**compress*/
		if (is_compress) {
			host->data_len = LZ4_compress_default(
				host->data, net->data, host->original_len,
				block_size);
			if (host->data_len < 1) {
				ret = -1;
				ErrorLog(
					"compress data for %s failure data_len: %u, original_len: "
					"%u\n",
					trans->remote_file, host->data_len,
					host->original_len);
				goto return__;
			}
			memcpy(host->data, net->data, host->data_len);
		}

		if (is_encrypt) {
			data_encrypt((unsigned char *)host->data,
				     host->data_len);
		}

		if (!write_is_ready(connfd, 180000)) {
			ret = -1;
			ErrorLog(
				"send file %s block data failure for time out.",
				trans->remote_file);
			goto return__;
		}
		msg_upload_block_hton(host, net);
		if (rpc_send(connfd, net, host->uiLEN, 0) != (int)host->uiLEN) {
			ret = -1;
			ErrorLog(
				"send file %s block data failure %s(errno: %d)",
				trans->remote_file, strerror(errno), errno);
			goto return__;
		}
	}

	ret = 0;
return__:
	return ret;
}
int rpc_upload_block_finish(trans_t t__)
{
	int ret = -1;
	trans_handle *trans = dynamic_cast<trans_handle *>((trans_handle *)t__);
	if (!trans) {
		return -1;
	}
	msg_upload_block_t *host = (msg_upload_block_t *)trans->host_buf;
	msg_upload_block_t *net = (msg_upload_block_t *)trans->net_buf;
	msg_upload_block_resp_t *resp_host =
		(msg_upload_block_resp_t *)trans->host_resp_buf;
	msg_upload_block_resp_t *resp_net =
		(msg_upload_block_resp_t *)trans->net_resp_buf;
	trans->reset_buf();

	host->opt_type = 3; /**close only*/
	host->is_compress = trans->is_compress;
	host->is_encrypt = trans->is_encrypt;
	host->is_checksum = trans->is_checksum;
	host->bolck_num = 0;
	host->data_len = 0;
	file_stat_hton(host->data, &host->data_len, &trans->st);
	msg_upload_block_hton(host, net);
	if (rpc_send(trans->sockfd, net, host->uiLEN, 0) != (int)host->uiLEN) {
		ErrorLog("rpc send failure: %s(errno: %d)", strerror(errno),
			 errno);
		goto return__;
	}

	ret = read_is_ready(trans->sockfd, g_rpc_config->read_timeout);
	if (ret <= 0) {
		ErrorLog("recv request response time out.");
		ret = -1;
		goto return__;
	}
	if (rpc_recv(trans->sockfd, resp_net, MSG_BUFF_LEN, 0) < 0) {
		ErrorLog("rpc recv failure: %s(errno: %d)", strerror(errno),
			 errno);
		goto return__;
	}
	msg_upload_block_resp_ntoh(resp_host, resp_net);
	if ((resp_host->uiResult != 0) ||
	    (resp_host->uiMT != (MT_EXECUTE_UPLOAD_BLOCK_RESP))) {
		ErrorLog(
			"rpc upload block finish request failure: %s  [ret: %d, MT: 0x%x]",
			trans->remote_file, resp_host->uiResult,
			resp_host->uiMT);
		goto return__;
	}
	ret = 0;
return__:
	delete trans;
	return ret;
}

typedef struct get_stat__ {
	int sockfd;
	get_stat__()
	{
		sockfd = -1;
	}
} get_stat_t;

int rpc_file_stat_start(struct session_info *session, handlest_t *t__)
{
	int ret = -1;
	char *host_buf = new char[MSG_BUFF_LEN];
	char *net_buf = new char[MSG_BUFF_LEN];
	msg_file_stat_t *host = (msg_file_stat_t *)host_buf;
	msg_file_stat_t *net = (msg_file_stat_t *)net_buf;
	msg_file_stat_resp_t *resp_host = (msg_file_stat_resp_t *)host_buf;
	msg_file_stat_resp_t *resp_net = (msg_file_stat_resp_t *)net_buf;

	get_stat_t *gst = new get_stat_t();
	*t__ = NULL;

	memset(host_buf, 0x00, MSG_BUFF_LEN);
	memset(net_buf, 0x00, MSG_BUFF_LEN);
	host->file_name[0] = 0x00;
	host->name_len = 0;
	host->type = 1;
	msg_file_stat_hton(host, net);

	if (rpc_send(session->sockfd, net, host->uiLEN, 0) !=
	    (int)host->uiLEN) {
		ErrorLog("rpc send failure: %s(errno: %d)", strerror(errno),
			 errno);
		goto return__;
	}

	if (read_is_ready(session->sockfd, g_rpc_config->read_timeout) ==
	    false) {
		ErrorLog("recv request response time out.");
		goto return__;
	}
	memset(host_buf, 0x00, MSG_BUFF_LEN);
	memset(net_buf, 0x00, MSG_BUFF_LEN);
	if (rpc_recv(session->sockfd, net_buf, MSG_BUFF_LEN, 0) < 1) {
		ErrorLog("rpc recv failure: %s(errno: %d)", strerror(errno),
			 errno);
		goto return__;
	}

	msg_file_stat_resp_ntoh(resp_host, resp_net);
	if (resp_host->uiResult != 0x00 ||
	    resp_host->uiMT != MT_EXECUTE_FILE_STAT_RESP) {
		ErrorLog(
			"rpc file stat request failure: %s  [ret: %d, MT: 0x%x]",
			host->file_name, resp_host->uiResult, resp_host->uiMT);
		goto return__;
	}
	gst->sockfd = session->sockfd;
	*t__ = gst;
	ret = 0;
return__:
	if (ret) {
		delete gst;
		*t__ = NULL;
	}
	delete[] host_buf;
	delete[] net_buf;
	return ret;
}

int rpc_file_stat(handlest_t t__, const char *remote_file, struct stat *st)
{
	get_stat_t *gst = (get_stat_t *)t__;
	int ret = -1;
	int sockfd = gst->sockfd;
	char *host_buf = new char[MSG_BUFF_LEN];
	char *net_buf = new char[MSG_BUFF_LEN];
	msg_file_stat_t *host = (msg_file_stat_t *)host_buf;
	msg_file_stat_t *net = (msg_file_stat_t *)net_buf;
	msg_file_stat_resp_t *resp_host = (msg_file_stat_resp_t *)host_buf;
	msg_file_stat_resp_t *resp_net = (msg_file_stat_resp_t *)net_buf;

	memset(host_buf, 0x00, MSG_BUFF_LEN);
	memset(net_buf, 0x00, MSG_BUFF_LEN);
	strcpy(host->file_name, remote_file);
	host->name_len = strlen(remote_file);
	host->type = 2;
	msg_file_stat_hton(host, net);

	if (rpc_send(sockfd, net, host->uiLEN, 0) != (int)host->uiLEN) {
		ErrorLog("rpc send failure: %s(errno: %d)", strerror(errno),
			 errno);
		goto return__;
	}

	ret = read_is_ready(sockfd, g_rpc_config->read_timeout);
	if (ret <= 0) {
		ErrorLog("recv request response time out.");
		ret = -1;
		goto return__;
	}
	memset(host_buf, 0x00, MSG_BUFF_LEN);
	memset(net_buf, 0x00, MSG_BUFF_LEN);
	if (rpc_recv(sockfd, net_buf, MSG_BUFF_LEN, 0) < 1) {
		ErrorLog("rpc recv failure: %s(errno: %d)", strerror(errno),
			 errno);
		goto return__;
	}

	msg_file_stat_resp_ntoh(resp_host, resp_net);
	if (resp_host->uiResult != 0x00 ||
	    resp_host->uiMT != MT_EXECUTE_FILE_STAT_RESP) {
		ErrorLog(
			"rpc file stat request failure: %s  [ret: %d, MT: 0x%x]",
			host->file_name, resp_host->uiResult, resp_host->uiMT);
		goto return__;
	}
	file_stat_ntoh(resp_host->data, &resp_host->data_len, st);

	ret = 0;
return__:
	delete[] host_buf;
	delete[] net_buf;
	return ret;
}

int rpc_file_stat_batch(handlest_t t__, const std::set<std::string> &files,
			std::map<const std::string, struct stat> &files_stat)
{
	get_stat_t *gst = (get_stat_t *)t__;
	int ret = -1;
	int offset = 0;
	int sockfd = gst->sockfd;
	char *host_buf = new char[MSG_BUFF_LEN];
	char *net_buf = new char[MSG_BUFF_LEN];
	int name_len = 0;
	const int num = files.size();
	int lost_num = 0;
	const int buflen = MSG_BUFF_LEN - 1024;
	msg_file_stat_t *host = (msg_file_stat_t *)host_buf;
	msg_file_stat_t *net = (msg_file_stat_t *)net_buf;
	msg_file_stat_resp_t *resp_host = (msg_file_stat_resp_t *)host_buf;
	msg_file_stat_resp_t *resp_net = (msg_file_stat_resp_t *)net_buf;

	memset(host_buf, 0x00, MSG_BUFF_LEN);
	memset(net_buf, 0x00, MSG_BUFF_LEN);
	host->name_len = 0;

	for (std::set<std::string>::const_iterator iter = files.begin();
	     iter != files.end(); ++iter) {
		if (buflen <= (host->name_len + iter->size() + 4)) {
			ErrorLog(
				"request stat failure for too long file name :%s buflen:%d < "
				"(host->name_len + iter->size()):%d\n",
				iter->c_str(), buflen,
				(int)(host->name_len + iter->size()));
			goto return__;
		}
		name_len = snprintf(host->file_name + host->name_len,
				    buflen - host->name_len, "%s;",
				    iter->c_str());
		host->name_len += name_len;
	}
	host->type = 3;
	msg_file_stat_hton(host, net);

	if (rpc_send(sockfd, net, host->uiLEN, 0) != (int)host->uiLEN) {
		ErrorLog("rpc send failure: %s(errno: %d)", strerror(errno),
			 errno);
		goto return__;
	}

	lost_num = 0;
	while ((int)(files_stat.size() + lost_num) < num) {
		if (read_is_ready(sockfd, g_rpc_config->read_timeout) ==
		    false) {
			ErrorLog("recv request response time out.");
			goto return__;
		}
		memset(host_buf, 0x00, MSG_BUFF_LEN);
		memset(net_buf, 0x00, MSG_BUFF_LEN);
		if (rpc_recv(sockfd, net_buf, MSG_BUFF_LEN, 0) < 1) {
			ErrorLog("rpc recv failure: %s(errno: %d)",
				 strerror(errno), errno);
			goto return__;
		}

		msg_file_stat_resp_ntoh(resp_host, resp_net);
		if (resp_host->uiResult != 0x00 ||
		    resp_host->uiMT != MT_EXECUTE_FILE_STAT_RESP) {
			ErrorLog(
				"rpc file stat request failure: %s  [ret: %d, MT: 0x%x]",
				host->file_name, resp_host->uiResult,
				resp_host->uiMT);
			goto return__;
		}
		offset = 0;
		while (offset < (int)resp_host->data_len) {
			{
				file_stat_item_t file_stat_item;
				if (file_stat_item.Deserialize(
					    resp_host->data, offset,
					    resp_host->data_len)) {
					ErrorLog(
						"request sync stat failure for file stat item "
						"deserialize. offset:%d, data_len:%d",
						offset, resp_host->data_len);
					goto return__;
				}
				if (file_stat_item.st.st_size != -1) {
					files_stat[file_stat_item.f_name] =
						file_stat_item.st;
				} else {
					++lost_num;
					WarningLog(
						"[%s] not existed",
						file_stat_item.f_name.c_str());
				}
			}
		}
	}
	ret = 0;
return__:
	delete[] host_buf;
	delete[] net_buf;
	return ret;
}

int rpc_file_stat_finish(handlest_t t__)
{
	get_stat_t *gst = (get_stat_t *)t__;

	int ret = -1;
	int sockfd = gst->sockfd;
	char *host_buf = new char[MSG_BUFF_LEN];
	char *net_buf = new char[MSG_BUFF_LEN];
	msg_file_stat_t *host = (msg_file_stat_t *)host_buf;
	msg_file_stat_t *net = (msg_file_stat_t *)net_buf;

	memset(host_buf, 0x00, MSG_BUFF_LEN);
	memset(net_buf, 0x00, MSG_BUFF_LEN);
	host->file_name[0] = 0x00;
	host->name_len = 0;
	host->type = 3333;
	msg_file_stat_hton(host, net);

	if (rpc_send(sockfd, net, host->uiLEN, 0) != (int)host->uiLEN) {
		ErrorLog("request sync file stat finish failure");
		goto return__;
	}
	ret = 0;
return__:
	delete gst;
	delete[] host_buf;
	delete[] net_buf;
	return ret;
}

int rpc_file_stat_single(struct session_info *session, const char *remote_file,
			 struct stat *st)
{
	int ret = -1;
	int sockfd = session->sockfd;
	char *host_buf = new char[MSG_BUFF_LEN];
	char *net_buf = new char[MSG_BUFF_LEN];
	msg_file_stat_t *host = (msg_file_stat_t *)host_buf;
	msg_file_stat_t *net = (msg_file_stat_t *)net_buf;
	msg_file_stat_resp_t *resp_host = (msg_file_stat_resp_t *)host_buf;
	msg_file_stat_resp_t *resp_net = (msg_file_stat_resp_t *)net_buf;

	memset(host_buf, 0x00, MSG_BUFF_LEN);
	memset(net_buf, 0x00, MSG_BUFF_LEN);
	strcpy(host->file_name, remote_file);
	host->name_len = strlen(remote_file);
	host->type = 0;
	msg_file_stat_hton(host, net);

	if (rpc_send(sockfd, net, host->uiLEN, 0) != (int)host->uiLEN) {
		ErrorLog("request sync file 1 :[%s] stat failure",
			 host->file_name);
		errno = EIO;
		goto return__;
	}

	ret = read_is_ready(sockfd, g_rpc_config->read_timeout);
	if (ret <= 0) {
		ErrorLog("request sync file 2 :[%s] stat failure time out",
			 host->file_name);
		errno = EIO;
		ret = -1;
		goto return__;
	}
	memset(host_buf, 0x00, MSG_BUFF_LEN);
	memset(net_buf, 0x00, MSG_BUFF_LEN);
	if (rpc_recv(sockfd, net_buf, MSG_BUFF_LEN, 0) < 1) {
		ErrorLog("request sync file 3 :[%s] stat failure", remote_file);
		errno = EIO;
		goto return__;
	}

	msg_file_stat_resp_ntoh(resp_host, resp_net);
	if (resp_host->uiResult != 0x00 ||
	    resp_host->uiMT != MT_EXECUTE_FILE_STAT_RESP) {
		ErrorLog("request sync file 4 :[%s] stat failure", remote_file);
		goto return__;
	}
	file_stat_ntoh(resp_host->data, &resp_host->data_len, st);

	ret = resp_host->existed;
return__:
	delete[] host_buf;
	delete[] net_buf;
	return ret;
}

int rpc_file_existed(const char *srv_ip, const int srv_port,
		     const char *remote_file)
{
	int existed = 0;
	int ret = -1;
	int sockfd = -1;
	char *host_buf = new char[MSG_BUFF_LEN];
	char *net_buf = new char[MSG_BUFF_LEN];
	msg_file_existed_t *host = (msg_file_existed_t *)host_buf;
	msg_file_existed_t *net = (msg_file_existed_t *)net_buf;
	msg_file_existed_resp_t *resp_host =
		(msg_file_existed_resp_t *)host_buf;
	msg_file_existed_resp_t *resp_net = (msg_file_existed_resp_t *)net_buf;

	memset(host_buf, 0x00, MSG_BUFF_LEN);
	memset(net_buf, 0x00, MSG_BUFF_LEN);
	strcpy(host->file_name, remote_file);
	host->name_len = strlen(remote_file);
	msg_file_existed_hton(host, net);

	sockfd = connect_server2(srv_ip, srv_port);
	if (sockfd < 0) {
		ErrorLog("connect to:[%s:%d] failure", srv_ip, srv_port);
		goto return__;
	}
	if (rpc_send(sockfd, net, host->uiLEN, 0) != (int)host->uiLEN) {
		ErrorLog("request file existed 1 :[%s] stat failure",
			 host->file_name);
		goto return__;
	}

	ret = read_is_ready(sockfd, g_rpc_config->read_timeout);
	if (ret <= 0) {
		ErrorLog("request file existed 2 :[%s] stat failure time out",
			 host->file_name);
		ret = -1;
		goto return__;
	}
	memset(host_buf, 0x00, MSG_BUFF_LEN);
	memset(net_buf, 0x00, MSG_BUFF_LEN);
	if (rpc_recv(sockfd, net_buf, MSG_BUFF_LEN, 0) < 1) {
		ErrorLog("request file existed 3 :[%s] stat failure",
			 remote_file);
		goto return__;
	}

	msg_file_existed_resp_ntoh(resp_host, resp_net);
	if (resp_host->uiResult != 0x00 ||
	    resp_host->uiMT != MT_EXECUTE_FILE_EXISTED_RESP) {
		ErrorLog("request file existed 4 :[%s] stat failure",
			 remote_file);
		goto return__;
	}
	existed = resp_host->existed;
return__:
	close(sockfd);
	delete[] host_buf;
	delete[] net_buf;
	return existed;
}

int rpc_sync_file_stat(handlest_t t__, const char *local_file,
		       const char *remote_file)
{
	int fd = -1;
	int ret = -1;
	mode_t mode = 0777;
	unsigned int gid = 0;
	unsigned int uid = 0;
	rpc_timespec_t atim = { 0 }; /* Time of last access.  */
	rpc_timespec_t mtim = { 0 }; /* Time of last modification.  */
	rpc_timespec_t ctim = { 0 }; /* Time of last status change.  */
	struct stat st;

	fd = open(local_file, O_RDONLY);
	if (fd < 0) {
		fprintf(stderr, "oepn file [%s] failure: %s(errno: %d)\n",
			local_file, strerror(errno), errno);
		goto return__;
	}

	if (rpc_file_stat(t__, remote_file, &st)) {
		ErrorLog("rpc get file [%s] stat failure.", remote_file);
		goto return__;
	}

	mode = st.st_mode;
	gid = st.st_gid;
	uid = st.st_uid;
	atim.tv_sec = st.st_atim.tv_sec;
	atim.tv_nsec = st.st_atim.tv_nsec;
	mtim.tv_sec = st.st_mtim.tv_sec;
	mtim.tv_nsec = st.st_mtim.tv_nsec;
	ctim.tv_sec = st.st_ctim.tv_sec;
	ctim.tv_nsec = st.st_ctim.tv_nsec;
	if (FileStat::GetInstance()->UpdateFileStatTime(fd, atim, mtim, ctim,
							mode, gid, uid)) {
		ErrorLog("sync file: %s stat failure.", local_file);
		goto return__;
	}
	ret = 0;
return__:
	close(fd);
	return ret;
}
int rpc_sync_file_stat_finish(handlest_t t__)
{
	return rpc_file_stat_finish(t__);
}

int do_fsbacup_dev_ioctl(int sockfd, const int opt_type, char *buf,
			 const int buflen)
{
	int ret = -1;
	int bytes = 0;
	const int buf_len = MSG_BUFF_LEN;
	char *host_buf = new char[MSG_BUFF_LEN];
	char *net_buf = new char[MSG_BUFF_LEN];
	char *resp_host_buf = new char[MSG_BUFF_LEN];
	char *resp_net_buf = new char[MSG_BUFF_LEN];
	msg_ioctl_fsbackup_t *host = (msg_ioctl_fsbackup_t *)host_buf;
	msg_ioctl_fsbackup_t *net = (msg_ioctl_fsbackup_t *)net_buf;
	msg_ioctl_fsbackup_resp_t *resp_host =
		(msg_ioctl_fsbackup_resp_t *)resp_host_buf;
	msg_ioctl_fsbackup_resp_t *resp_net =
		(msg_ioctl_fsbackup_resp_t *)resp_net_buf;
	std::string msg;

	memset(host_buf, 0x00, MSG_BUFF_LEN);
	memset(resp_host_buf, 0x00, MSG_BUFF_LEN);

	// 数据填充
	host->opt_type = opt_type;
	if (opt_type == FSBACKUP_IIOCTL_SET_BACKUP_PATH ||
	    opt_type == FSBACKUP_IIOCTL_DEL_BACKUP_PATH ||
	    opt_type == FSBACKUP_IIOCTL_SET_EXCLUDE_PATH ||
	    opt_type == FSBACKUP_IIOCTL_DEL_EXCLUDE_PATH) {
		host->data_len = sizeof(ioctl_dir_path);
		memcpy(host->data, buf, host->data_len);
	} else if (opt_type == FSBACKUP_IIOCTL_UPDATE_LOG_DIR) {
		host->data_len = sizeof(ioctl_dir_path);
		memcpy(host->data, buf, host->data_len);
	} else if (opt_type == FSBACKUP_IIOCTL_META_SYNC) {
		host->data_len = sizeof(ioctl_dir_path);
		memcpy(host->data, buf, host->data_len);
	} else if (opt_type == FSBACKUP_IIOCTL_LOG_SWITCH) {
		host->data_len = sizeof(ioctl_dir_path);
		memcpy(host->data, buf, host->data_len);
	} else {
		ErrorLog("bad ioctl type: %d", opt_type);
		snprintf(buf, buflen, "bad ioctl type: %d", opt_type);
		goto return__;
	}
	msg_ioctl_fsbackup_hton(host, net);

	// 发送数据
	if (rpc_send(sockfd, net, host->uiLEN, 0) != (int)host->uiLEN) {
		msg = "rpc send failure";
		ErrorLog("rpc send failure: %s(errno: %d)", strerror(errno),
			 errno);
		errno = EIO;
		goto return__;
	}

	// 接收数据
	memset((char *)net_buf, 0x00, buf_len);
	bytes = rpc_recv(sockfd, (char *)resp_net_buf, buf_len, 0);
	if (bytes < 0) {
		msg = "recv failure";
		ErrorLog("recv failure %d", bytes);
		errno = EIO;
		goto return__;
	}
	msg_ioctl_fsbackup_resp_ntoh(resp_host, resp_net);

	// 数据解析
	if (opt_type == FSBACKUP_IIOCTL_SET_BACKUP_PATH ||
	    opt_type == FSBACKUP_IIOCTL_DEL_BACKUP_PATH ||
	    opt_type == FSBACKUP_IIOCTL_SET_EXCLUDE_PATH ||
	    opt_type == FSBACKUP_IIOCTL_DEL_EXCLUDE_PATH) {
		if (resp_host->uiResult != 0x00) {
			ret = -resp_host->err_no;
			snprintf(buf, buflen, "%s, errno:%d",
				 strerror(resp_host->err_no),
				 resp_host->err_no);
			goto return__;
		}
	} else if (opt_type == FSBACKUP_IIOCTL_UPDATE_LOG_DIR) {
		if (resp_host->uiResult == 0x00 &&
		    resp_host->data_len == sizeof(fsbackup_kernel_stat)) {
			memcpy(buf, resp_host->data, resp_host->data_len);
		} else {
			ret = -resp_host->err_no;
			snprintf(buf, buflen, "%s, errno:%d",
				 strerror(resp_host->err_no),
				 resp_host->err_no);
			goto return__;
		}
	} else if (opt_type == FSBACKUP_IIOCTL_META_SYNC) {
		if (resp_host->uiResult == 0x00 &&
		    resp_host->data_len == sizeof(fsbackup_kernel_stat)) {
			memcpy(buf, resp_host->data, resp_host->data_len);
		} else {
			ret = -resp_host->err_no;
			snprintf(buf, buflen, "%s, errno:%d",
				 strerror(resp_host->err_no),
				 resp_host->err_no);
			goto return__;
		}
	} else if (opt_type == FSBACKUP_IIOCTL_LOG_SWITCH) {
		if (resp_host->uiResult == 0x00 &&
		    resp_host->data_len == sizeof(ioctl_dir_path)) {
			memcpy(buf, resp_host->data, resp_host->data_len);
		} else {
			ret = -resp_host->err_no;
			snprintf(buf, buflen, "%s, errno:%d",
				 strerror(resp_host->err_no),
				 resp_host->err_no);
			goto return__;
		}

	} else {
		ErrorLog("bad ioctl type: %d", opt_type);
		snprintf(buf, buflen, "bad ioctl type: %d", opt_type);
		goto return__;
	}
	ret = 0;
return__:

	delete[] host_buf;
	delete[] net_buf;
	delete[] resp_host_buf;
	delete[] resp_net_buf;

	return ret;
}

int fsbacup_dev_ioctl(const char *svr_ip, const int svr_port,
		      const int opt_type, char *buf, const int buflen)
{
	int ret = -1;
	int sockfd = -1;
	sockfd = connect_server2(svr_ip, svr_port);
	if (sockfd < 0) {
		snprintf(buf, buflen, "connect to:[%s:%d] failure", svr_ip,
			 svr_port);
		ErrorLog("connect to:[%s:%d] failure", svr_ip, svr_port);
		goto return__;
	}

	ret = do_fsbacup_dev_ioctl(sockfd, opt_type, buf, buflen);

return__:
	if (sockfd != -1) {
		close(sockfd);
	}

	return ret;
}

int parse_file_to_set(const char *file_path, std::set<std::string> &files_list)
{
	int ret = 0;
	int fd = -1;
	int read_len = 0;
	int i = 0;
	int j = 0;
	char buf[PATH_MAX + 1] = { 0 };
	char line[PATH_MAX] = { 0 };

	if (file_path == NULL || file_path[0] == '\0') {
		ret = -1;
		goto return__;
	}

	fd = open(file_path, O_RDONLY);
	if (fd < 0) {
		ErrorLog("open file [%s] failure: %s(errno: %d)", file_path,
			 strerror(errno), errno);
		ret = -1;
		goto return__;
	}

	while (true) {
		read_len = read(fd, buf, PATH_MAX);
		if (read_len <= 0) {
			break;
		}
		buf[read_len] = '\0';
		for (i = 0; buf[i]; i++) {
			if (buf[i] != ';' && buf[i] != '\n' && buf[i] != '\r') {
				line[j] = buf[i];
				j++;
			} else if (buf[i] == ';') {
				files_list.insert(line);
				memset(line, 0, sizeof(line));
				j = 0;
			}
		}
		memset(buf, 0, sizeof(buf));
	}
	if (strlen(line) > 1) {
		files_list.insert(line);
	}

	ret = 0;
	close(fd);

return__:
	return ret;
}

void set_rpc_check_data(bool enable)
{
	g_rpc_config->check_data = enable;
}

void set_rpc_keepalive_interval(int interval)
{
	g_rpc_config->keepalive = interval;
}

void set_rpc_read_timeout(int read_timeout)
{
	g_rpc_config->read_timeout = read_timeout;
}

void set_rpc_retry(int retry)
{
	g_rpc_config->retry = retry;
}

void set_rpc_parallel(int parallel)
{
	g_rpc_config->parallel = parallel;
}

int set_rpc_init_config(const char *config_file, char *err_msg, int len)
{
	return rpc_init_config(config_file, err_msg, len);
}

int do_remote_mkdir(int connfd, const char *remote_file)
{
	int ret = -1;
	char *host_buf = new char[MSG_BUFF_LEN];
	char *net_buf = new char[MSG_BUFF_LEN];
	char *resp_host_buf = new char[MSG_BUFF_LEN];
	char *resp_net_buf = new char[MSG_BUFF_LEN];
	const int buflen = MSG_BUFF_LEN - 2048;

	msg_mkdir_t *host = (msg_mkdir_t *)host_buf;
	msg_mkdir_t *net = (msg_mkdir_t *)net_buf;
	msg_mkdir_resp_t *resp_host = (msg_mkdir_resp_t *)resp_host_buf;
	msg_mkdir_resp_t *resp_net = (msg_mkdir_resp_t *)resp_net_buf;

	host->path_len = snprintf(host->path, buflen, "%s", remote_file);
	msg_mkdir_hton(host, net);
	if (rpc_send(connfd, net, host->uiLEN, 0) != (int)host->uiLEN) {
		ErrorLog("rpc send failure. %s failure. %s(errno: %d)",
			 remote_file, strerror(errno), errno);
		goto return__;
	}
	ret = read_is_ready(connfd, g_rpc_config->read_timeout);
	if (ret > 0) {
		if (rpc_recv(connfd, resp_net, buflen, 0) < 0) {
			ErrorLog("rpc recv failure. %s failure. %s(errno: %d)",
				 remote_file, strerror(errno), errno);
			goto return__;
		}
		msg_mkdir_resp_ntoh(resp_host, resp_net);
		if (resp_host->uiResult != 0) {
			errno = -resp_host->uiResult;
			ErrorLog("mkdir %s failure: %s(errno: %d)", remote_file,
				 strerror(errno), errno);
			goto return__;
		} else {
			InfoLog("mkdir %s success", remote_file);
		}
	} else {
		WarningLog("mkdir %s time out", remote_file);
		goto return__;
	}
	ret = 0;
return__:
	delete[] host_buf;
	delete[] net_buf;
	delete[] resp_host_buf;
	delete[] resp_net_buf;
	return ret;
}

int do_remote_unlink(int connfd, const char *remote_file)
{
	int ret = -1;
	char *host_buf = new char[MSG_BUFF_LEN];
	char *net_buf = new char[MSG_BUFF_LEN];
	char *resp_host_buf = new char[MSG_BUFF_LEN];
	char *resp_net_buf = new char[MSG_BUFF_LEN];
	const int buflen = MSG_BUFF_LEN - 2048;

	msg_unlink_t *host = (msg_unlink_t *)host_buf;
	msg_unlink_t *net = (msg_unlink_t *)net_buf;
	msg_unlink_resp_t *resp_host = (msg_unlink_resp_t *)resp_host_buf;
	msg_unlink_resp_t *resp_net = (msg_unlink_resp_t *)resp_net_buf;

	host->path_len = snprintf(host->path, buflen, "%s", remote_file);
	msg_unlink_hton(host, net);
	if (rpc_send(connfd, net, host->uiLEN, 0) != (int)host->uiLEN) {
		ErrorLog("rpc send failure. %s failure. %s(errno: %d)",
			 remote_file, strerror(errno), errno);
		errno = EIO;
		goto return__;
	}
	ret = read_is_ready(connfd, g_rpc_config->read_timeout);
	if (ret > 0) {
		if (rpc_recv(connfd, resp_net, buflen, 0) < 0) {
			ErrorLog("rpc recv failure. %s failure. %s(errno: %d)",
				 remote_file, strerror(errno), errno);
			errno = EIO;
			goto return__;
		}
		msg_unlink_resp_ntoh(resp_host, resp_net);
		if (resp_host->uiResult != 0) {
			errno = -resp_host->uiResult;
			ErrorLog("unlink %s failure: %s(errno: %d)",
				 remote_file, strerror(errno), errno);
			goto return__;
		} else {
			InfoLog("unlink %s success", remote_file);
		}
	} else {
		WarningLog("unlink %s time out", remote_file);
		goto return__;
	}
	ret = 0;
return__:
	delete[] host_buf;
	delete[] net_buf;
	delete[] resp_host_buf;
	delete[] resp_net_buf;
	return ret;
}

int rpc_conn_cli_lstat(struct rpc_conn *conn, const char *remote_path,
		       struct stat *st)
{
	struct buf *msgw = conn->msgw;
	struct buf *msgr = conn->msgr;

	int ret = -1;
	int rc = -1;

	if ((ret = buf_put_u8(msgw, NEW_CONN_TMP_LSTAT)) != 0 ||
	    (ret = buf_put_cstring(msgw, remote_path)) != 0) {
		ErrorLog("put_cstring failure. %s failure. %s(errno: %d)",
			 remote_path, strerror(errno), errno);
		goto return__;
	}

	ret = rpc_conn_reconn_send_msg(conn);
	if (ret != 0) {
		ErrorLog(
			"rpc_conn_reconn_send_msg failure. %s failure. %s(errno: %d)",
			remote_path, strerror(errno), errno);
		goto return__;
	}

	ret = rpc_conn_is_ready_recv_msg(conn);
	if (ret != 0) {
		ErrorLog(
			"rpc_conn_is_ready_recv_msg failure. %s failure. %s(errno: %d)",
			remote_path, strerror(errno), errno);
		goto return__;
	}

	if ((ret = buf_get_u32(msgr, (uint32_t *)&rc)) != 0 ||
	    (ret = buf_get_u32(msgr, (uint32_t *)&errno)) != 0) {
		ErrorLog("get_u32 failure. %s failure. %s(errno: %d)",
			 remote_path, strerror(errno), errno);
		goto return__;
	}

	ret = rc;
	if (rc != 0) {
		ErrorLog("lstat %s failure. %s(errno: %d)", remote_path,
			 strerror(errno), errno);
		goto return__;
	}

	ret = decode_attrib(msgr, st);
	if (ret != 0) {
		ErrorLog("decode_attrib failure. %s failure. %s(errno: %d)",
			 remote_path, strerror(errno), errno);
		goto return__;
	}

	ret = 0;
return__:
	return ret;
}

int rpc_conn_cli_readdir(struct rpc_conn *conn, const char *remote_path,
			 directory_walk_func func, void *priv)
{
	int ret = 0;
	int rc = 0;
	// uint8_t remote_flags = READDIR_FLAG_WITH_LINK | READDIR_FLAG_WITH_STAT;
	uint8_t remote_flags = READDIR_FLAG_WITH_STAT;
	uint32_t chunk_size = READDIR_CHUNK_SIZE;
	struct buf *buf_tmp = NULL;
	struct buf *msgw = conn->msgw;
	struct buf *msgr = conn->msgr;

	char *name = NULL;
	char *link_path = NULL;

	if ((ret = buf_put_u8(msgw, NEW_CONN_TMP_READDIR)) != 0 ||
	    (ret = buf_put_u8(msgw, remote_flags)) != 0 ||
	    (ret = buf_put_u32(msgw, chunk_size)) != 0 ||
	    (ret = buf_put_cstring(msgw, remote_path)) != 0) {
		ErrorLog("put_cstring failure. %s failure. %s(errno: %d)",
			 remote_path, strerror(errno), errno);
		goto return__;
	}

	ret = rpc_conn_reconn_send_msg(conn);
	if (ret != 0) {
		ErrorLog(
			"rpc_conn_reconn_send_msg failure. %s failure. %s(errno: %d)",
			remote_path, strerror(errno), errno);
		goto return__;
	}

	ret = rpc_conn_is_ready_recv_msg(conn);
	if (ret != 0) {
		ErrorLog(
			"rpc_conn_is_ready_recv_msg failure. %s failure. %s(errno: %d)",
			remote_path, strerror(errno), errno);
		goto return__;
	}

	if ((ret = buf_get_u32(msgr, (uint32_t *)&rc)) != 0 ||
	    (ret = buf_get_u32(msgr, (uint32_t *)&errno)) != 0) {
		ErrorLog("get_u32 failure. %s failure. %s(errno: %d)",
			 remote_path, strerror(errno), errno);
		goto return__;
	}

	ret = rc;
	if (rc != 0) {
		ErrorLog("opendir %s failure. %s(errno: %d)", remote_path,
			 strerror(errno), errno);
		goto return__;
	}

	buf_tmp = buf_new();
	if (buf_tmp == NULL) {
		ErrorLog("buf_new failure. %s failure. %s(errno: %d)",
			 remote_path, strerror(errno), errno);
		errno = ENOMEM;
		goto return__;
	}

	while (1) {
		uint32_t count = 0;
		uint8_t type = 0;
		struct stat st;

		ret = rpc_conn_is_ready_recv_msg(conn);
		if (ret != 0) {
			ErrorLog(
				"rpc_conn_is_ready_recv_msg failure. %s failure. %s(errno: %d)",
				remote_path, strerror(errno), errno);
			goto return__;
		}

		if ((ret = buf_get_u32(msgr, (uint32_t *)&count)) != 0) {
			ErrorLog("get_u32 failure. %s failure. %s(errno: %d)",
				 remote_path, strerror(errno), errno);
			goto return__;
		}

		if (count <= 0) {
			break;
		}

		if ((ret = buf_get_stringb(msgr, buf_tmp)) != 0) {
			ErrorLog(
				"get_stringb failure. %s failure. %s(errno: %d)",
				remote_path, strerror(errno), errno);
			goto return__;
		}

		for (uint32_t i = 0; i < count; i++) {
			if (buf_get_cstring(buf_tmp, &name, 0) != 0 ||
			    buf_get_u8(buf_tmp, &type) != 0) {
				ErrorLog(
					"get_cstring failure. %s failure. %s(errno: %d)",
					remote_path, strerror(errno), errno);
				goto return__;
			}
			if (remote_flags & READDIR_FLAG_WITH_STAT) {
				if ((ret = decode_attrib(buf_tmp, &st)) != 0) {
					ErrorLog(
						"decode_attrib failure. %s failure. %s(errno: %d)",
						remote_path, strerror(errno),
						errno);
					goto return__;
				}
			}
			if (type == DT_LNK &&
			    (remote_flags & READDIR_FLAG_WITH_LINK)) {
				if (buf_get_cstring(buf_tmp, &link_path, 0) !=
				    0) {
					ErrorLog(
						"get_cstring failure. %s failure. %s(errno: %d)",
						remote_path, strerror(errno),
						errno);
					goto return__;
				}
			}

			if ((ret = func(priv, name, &st)) != 0) {
				ErrorLog(
					"directory_walk_func failure. %s failure. %s(errno: %d)",
					remote_path, strerror(errno), errno);
				rpc_conn_close(conn);
				goto return__;
			}

			free(name);
			name = NULL;
			if (link_path != NULL) {
				free(link_path);
				link_path = NULL;
			}
		}
		buf_clear(buf_tmp);
		if (count < chunk_size) {
			break;
		}
	}

	ret = 0;
return__:
	if (name != NULL) {
		free(name);
	}
	if (link_path != NULL) {
		free(link_path);
	}
	if (buf_tmp != NULL) {
		buf_free(buf_tmp);
	}
	return ret;
}

int rpc_conn_cli_readdir_tree(struct rpc_conn *conn, const char *remote_path,
			      directory_walk_func func, void *priv)
{
	int ret = 0;
	int rc = 0;
	uint8_t remote_flags = READDIR_FLAG_WITH_STAT;
	uint32_t chunk_size = READDIR_CHUNK_SIZE;
	struct buf *buf_tmp = NULL;
	struct buf *msgw = conn->msgw;
	struct buf *msgr = conn->msgr;
	char *name = NULL;

	if ((ret = buf_put_u8(msgw, NEW_CONN_TMP_READDIR_TREE)) != 0 ||
	    (ret = buf_put_u8(msgw, remote_flags)) != 0 ||
	    (ret = buf_put_u32(msgw, chunk_size)) != 0 ||
	    (ret = buf_put_cstring(msgw, remote_path)) != 0) {
		ErrorLog("put request failure. %s(errno: %d)", strerror(errno),
			 errno);
		goto return__;
	}

	ret = rpc_conn_reconn_send_msg(conn);
	if (ret != 0) {
		ErrorLog("send request failure. %s(errno: %d)", strerror(errno),
			 errno);
		goto return__;
	}

	ret = rpc_conn_is_ready_recv_msg(conn);
	if (ret != 0) {
		if (ret == -3) {
			ErrorLog("recv response failure. IO_EOF(ret=%d)",
				 ret);
		} else {
			ErrorLog("recv response failure. %s(errno: %d)",
				 strerror(errno), errno);
		}
		goto return__;
	}

	if ((ret = buf_get_u32(msgr, (uint32_t *)&rc)) != 0 ||
	    (ret = buf_get_u32(msgr, (uint32_t *)&errno)) != 0) {
		ErrorLog("get response failure. %s(errno: %d)", strerror(errno),
			 errno);
		goto return__;
	}
	if (rc != 0) {
		ErrorLog("readdir_tree %s failure. %s(errno: %d)", remote_path,
			 strerror(errno), errno);
		ret = rc;
		goto return__;
	}

	buf_tmp = buf_new();
	if (buf_tmp == NULL) {
		ErrorLog("buf_new failure. %s(errno: %d)", strerror(errno),
			 errno);
		errno = ENOMEM;
		goto return__;
	}

	while (1) {
		uint32_t count = 0;
		uint8_t type = 0;
		struct stat st;

		ret = rpc_conn_is_ready_recv_msg(conn);
		if (ret != 0) {
			if (ret == -3) {
				ErrorLog("recv chunk failure. IO_EOF(ret=%d)",
					 ret);
			} else {
				ErrorLog("recv chunk failure. %s(errno: %d)",
					 strerror(errno), errno);
			}
			goto return__;
		}

		if ((ret = buf_get_u32(msgr, (uint32_t *)&count)) != 0) {
			ErrorLog("get count failure. %s(errno: %d)",
				 strerror(errno), errno);
			goto return__;
		}

		if (count <= 0) {
			break;
		}

		if ((ret = buf_get_stringb(msgr, buf_tmp)) != 0) {
			ErrorLog("get stringb failure. %s(errno: %d)",
				 strerror(errno), errno);
			goto return__;
		}

		for (uint32_t i = 0; i < count; i++) {
			if (buf_get_cstring(buf_tmp, &name, 0) != 0 ||
			    buf_get_u8(buf_tmp, &type) != 0) {
				ErrorLog("get entry failure. %s(errno: %d)",
					 strerror(errno), errno);
				goto return__;
			}
			if (remote_flags & READDIR_FLAG_WITH_STAT) {
				if ((ret = decode_attrib(buf_tmp, &st)) != 0) {
					ErrorLog(
						"decode_attrib failure. %s(errno: %d)",
						strerror(errno), errno);
					goto return__;
				}
			}
			if ((ret = func(priv, name, &st)) != 0) {
				rpc_conn_close(conn);
				goto return__;
			}
			free(name);
			name = NULL;
		}
		buf_clear(buf_tmp);
		if (count < chunk_size) {
			break;
		}
	}

	ret = 0;
return__:
	if (name != NULL) {
		free(name);
	}
	if (buf_tmp != NULL) {
		buf_free(buf_tmp);
	}
	return ret;
}

int rpc_conn_cli_pread(struct rpc_conn *conn, const char *remote_path,
		       const char *local_path, uint64_t size, uint64_t offset)
{
	int ret = 0;
	int rc = 0;
	int rc_tmp = 0;
	struct buf *msgw = conn->msgw;
	struct buf *msgr = conn->msgr;
	size_t recv_len = 0;

	rc = open(local_path, O_WRONLY | O_CREAT | O_TRUNC, 0644);
	if (rc < 0) {
		ErrorLog("open %s failure. %s(errno: %d)", local_path,
			 strerror(errno), errno);
		ret = -1;
		goto return__;
	}

	if (offset != 0 && (ret = lseek(rc, offset, SEEK_SET)) == -1) {
		ErrorLog("lseek %s failure. %s(errno: %d)", local_path,
			 strerror(errno), errno);
		goto return__;
	}

	if ((ret = buf_put_u8(msgw, NEW_CONN_TMP_PREAD)) != 0 ||
	    (ret = buf_put_u64(msgw, offset)) != 0 ||
	    (ret = buf_put_u64(msgw, size)) != 0 ||
	    (ret = buf_put_cstring(msgw, remote_path)) != 0) {
		ErrorLog("put_cstring failure. %s failure. %s(errno: %d)",
			 remote_path, strerror(errno), errno);
		goto return__;
	}

	ret = rpc_conn_reconn_send_msg(conn);
	if (ret != 0) {
		ErrorLog(
			"rpc_conn_reconn_send_msg failure. %s failure. %s(errno: %d)",
			remote_path, strerror(errno), errno);
		goto return__;
	}

	while (1) {
		const char *data = NULL;
		size_t len = 0;

		ret = rpc_conn_is_ready_recv_msg(conn);
		if (ret != 0) {
			ErrorLog(
				"rpc_conn_is_ready_recv_msg failure. %s failure. %s(errno: %d)",
				remote_path, strerror(errno), errno);
			goto return__;
		}

		if ((ret = buf_get_u32(msgr, (uint32_t *)&rc_tmp)) != 0) {
			ErrorLog("get_u32 failure. %s failure. %s(errno: %d)",
				 remote_path, strerror(errno), errno);
			goto return__;
		}

		if (rc_tmp < 0) {
			if ((ret = buf_get_u32(msgr, (uint32_t *)&errno)) !=
			    0) {
				ErrorLog(
					"get_u32 failure. %s failure. %s(errno: %d)",
					remote_path, strerror(errno), errno);
				goto return__;
			}
			ret = -1;
			ErrorLog("pread %s failure. %s(errno: %d)", remote_path,
				 strerror(errno), errno);
			goto return__;
		} else if (rc_tmp > 0) {
			if ((ret = buf_get_string_direct(msgr,
							 (const u_char **)&data,
							 &len)) != 0) {
				ErrorLog(
					"get_string_direct failure. %s failure. %s(errno: %d)",
					remote_path, strerror(errno), errno);
				goto return__;
			}
			if (write(rc, data, len) != (ssize_t)len) {
				ret = -1;
				ErrorLog("write %s failure. %s(errno: %d)",
					 local_path, strerror(errno), errno);
				rpc_conn_close(conn);
				goto return__;
			}
			recv_len += len;
			if (recv_len >= size) {
				if (g_rpc_config->debug) {
					InfoLog("pread %s done. %d/%d bytes received.",
						remote_path, recv_len, size);
				}
				break;
			}
		} else {
			if (g_rpc_config->debug) {
				InfoLog("pread %s done. %d/%d bytes received.",
					remote_path, recv_len, size);
			}
			break;
		}
	}

	ret = 0;

return__:
	if (rc > 0) {
		close(rc);
		if (ret != 0) {
			unlink(local_path);
		}
	}
	return ret;
}

int rpc_conn_cli_pwrite(struct rpc_conn *conn, const char *remote_path,
			const char *local_path, uint64_t size, uint64_t offset)
{
	int ret = 0;
	int rc = 0;
	int rc_tmp = 0;
	struct buf *msgw = conn->msgw;
	struct buf *msgr = conn->msgr;

	uint64_t local_offset = offset;
	uint64_t local_size = size;
	uint32_t chunk_len = PREAD_CHUNK_SIZE;
	char *chunk = NULL;

	rc = open(local_path, O_RDONLY);
	if (rc < 0) {
		ErrorLog("open %s failure. %s(errno: %d)", local_path,
			 strerror(errno), errno);
		ret = -1;
		goto return__;
	}

	if ((ret = buf_put_u8(msgw, NEW_CONN_TMP_PWRITE)) != 0 ||
	    (ret = buf_put_u64(msgw, offset)) != 0 ||
	    (ret = buf_put_u64(msgw, size)) != 0 ||
	    (ret = buf_put_cstring(msgw, remote_path)) != 0) {
		ErrorLog("put_cstring failure. %s failure. %s(errno: %d)",
			 remote_path, strerror(errno), errno);
		goto return__;
	}

	ret = rpc_conn_reconn_send_msg(conn);
	if (ret != 0) {
		ErrorLog(
			"rpc_conn_reconn_send_msg failure. %s failure. %s(errno: %d)",
			remote_path, strerror(errno), errno);
		goto return__;
	}

	chunk = (char *)malloc(chunk_len);
	if (chunk == NULL) {
		ErrorLog("malloc failure. %s failure. %s(errno: %d)",
			 remote_path, strerror(errno), errno);
		goto return__;
	}

	while (local_size >= 0) {
		uint64_t len = chunk_len;
		if (len > local_size) {
			len = local_size;
		}
		int n = pread(rc, chunk, len, local_offset);
		if (n < 0) {
			ErrorLog("pread %s failure. %s(errno: %d)", remote_path,
				 strerror(errno), errno);
			n = 0;
		}
		if ((ret = buf_put_string(msgw, chunk, n)) != 0) {
			ErrorLog("put_u32 failure. %s failure. %s(errno: %d)",
				 remote_path, strerror(errno), errno);
			goto return__;
		}
		if ((ret = rpc_conn_send_msg(conn)) != 0) {
			ErrorLog(
				"rpc_conn_reconn_send_msg failure. %s failure. %s(errno: %d)",
				remote_path, strerror(errno), errno);
			goto rpc_recv__;
		}

		local_offset += n;
		local_size -= n;

		if (n <= 0) {
			break;
		}
	}

rpc_recv__:
	ret = rpc_conn_recv_msg(conn);
	if (ret != 0) {
		ErrorLog("rpc_conn_recv_msg failure. %s failure. %s(errno: %d)",
			 remote_path, strerror(errno), errno);
		goto return__;
	}

	if ((ret = buf_get_u32(msgr, (uint32_t *)&rc_tmp)) != 0 ||
	    (ret = buf_get_u32(msgr, (uint32_t *)&errno)) != 0) {
		ErrorLog("get_u32 failure. %s failure. %s(errno: %d)",
			 remote_path, strerror(errno), errno);
		goto return__;
	} else {
		if (rc_tmp != 0) {
			ErrorLog("pwrite %s failure. %s(errno: %d)",
				 remote_path, strerror(errno), errno);
		} else {
			if (g_rpc_config->debug) {
				InfoLog("pwrite %s done.", remote_path);
			}
		}
	}

	ret = 0;
	if (rc_tmp != 0) {
		ret = -1;
	}

return__:
	if (chunk != NULL) {
		free(chunk);
	}
	if (rc > 0) {
		close(rc);
	}
	return ret;
}

int do_new_conn(int connfd, const rpc_conn_t *conn)
{
	int ret = -1;
	char *host_buf = new char[MSG_BUFF_LEN];
	char *net_buf = new char[MSG_BUFF_LEN];
	char *resp_host_buf = new char[MSG_BUFF_LEN];
	char *resp_net_buf = new char[MSG_BUFF_LEN];
	rpc_args *rpc = conn->rpc;

	msg_new_conn_t *host = (msg_new_conn_t *)host_buf;
	msg_new_conn_t *net = (msg_new_conn_t *)net_buf;
	msg_new_conn_resp_t *resp_host = (msg_new_conn_resp_t *)resp_host_buf;
	msg_new_conn_resp_t *resp_net = (msg_new_conn_resp_t *)resp_net_buf;
	const int buflen = MSG_BUFF_LEN - 2048;

	host->flags = 0;
	if (rpc->is_checksum) {
		host->flags |= RPC_CONN_FLAGS_COMPRESS;
	}

	if (rpc->is_encrypt) {
		host->flags |= RPC_CONN_FLAGS_ENCRYPT;
	}

	msg_new_conn_hton(host, net);

	if (rpc_send(connfd, net, host->uiLEN, 0) != (int)host->uiLEN) {
		ErrorLog("rpc send failure. %d failure. %s(errno: %d)",
			 conn->conn_id, strerror(errno), errno);
		ret = -1;
		goto return__;
	}

	if ((ret = read_is_ready(connfd, g_rpc_config->read_timeout)) != 1) {
		ErrorLog("read_is_ready failure. %d failure. %s(errno: %d)",
			 conn->conn_id, strerror(errno), errno);
		goto return__;
	}
	if (rpc_recv(connfd, resp_net, buflen, 0) < 0) {
		ErrorLog("rpc recv failure. %d failure. %s(errno: %d)",
			 conn->conn_id, strerror(errno), errno);
		ret = -1;
		goto return__;
	}

	ret = 0;

	msg_new_conn_resp_ntoh(resp_host, resp_net);
	if (resp_host->uiResult != 0) {
		errno = resp_host->err;
		ErrorLog("new_conn failure. %d failure. %s(errno: %d)",
			 conn->conn_id, strerror(errno), errno);
		ret = -1;
		goto return__;
	} else {
		InfoLog("new_conn success. %d", conn->conn_id);
	}
return__:
	delete[] host_buf;
	delete[] net_buf;
	delete[] resp_host_buf;
	delete[] resp_net_buf;
	return ret;
}

rpc_conn_t *rpc_conn_start(rpc_args *rpc)
{
	int ret = 0;
	int sockfd = -1;
	rpc_conn_t *conn = NULL;

	sockfd = connect_server(rpc->svr_ip, rpc->svr_port, rpc->local_ip,
				rpc->local_port);
	if (sockfd < 0) {
		goto error__;
	}

	conn = new_rpc_conn(sockfd);
	if (conn == NULL) {
		goto error__;
	}
	conn->rpc = rpc;

	ret = do_new_conn(sockfd, conn);
	if (ret != 0) {
		goto error__;
	}

	conn->restart_conn_cb = rpc_conn_restart;
	conn->sockfd = sockfd;

	return conn;
error__:
	if (conn) {
		free(conn);
	}
	if (sockfd >= 0) {
		close(sockfd);
	}
	return NULL;
}

int rpc_conn_restart(rpc_conn_t *conn)
{
	int ret = -1;
	int sockfd = -1;
	rpc_args *rpc = conn->rpc;

	close(conn->sockfd);
	conn->sockfd = -1;

	sockfd = connect_server(rpc->svr_ip, rpc->svr_port, rpc->local_ip,
				rpc->local_port);
	if (sockfd < 0) {
		goto error__;
	}

	ret = do_new_conn(sockfd, conn);
	if (ret != 0) {
		goto error__;
	}

	conn->sockfd = sockfd;
	conn->remote_dir_path.clear();
	conn->remote_dir_fd = -1;
	return 0;
error__:
	if (sockfd >= 0) {
		close(sockfd);
	}
	return ret;
}

void rpc_conn_stop(rpc_conn_t *conn)
{
	rpc_conn_free(conn);
}

int rpc_conn_cli_mkdir(struct rpc_conn *conn, const char *remote_path,
		       uint32_t mode)
{
	int ret = 0;
	int rc = 0;
	struct buf *msgw = conn->msgw;
	struct buf *msgr = conn->msgr;

	if ((ret = buf_put_u8(msgw, NEW_CONN_TMP_MKDIR)) != 0 ||
	    (ret = buf_put_u32(msgw, mode)) != 0 ||
	    (ret = buf_put_cstring(msgw, remote_path)) != 0) {
		ErrorLog("put_cstring failure. %s failure. %s(errno: %d)",
			 remote_path, strerror(errno), errno);
		goto return__;
	}

	ret = rpc_conn_reconn_send_msg(conn);
	if (ret != 0) {
		ErrorLog(
			"rpc_conn_reconn_send_msg failure. %s failure. %s(errno: %d)",
			remote_path, strerror(errno), errno);
		goto return__;
	}

	ret = rpc_conn_is_ready_recv_msg(conn);
	if (ret != 0) {
		ErrorLog("rpc_conn_recv_msg failure. %s failure. %s(errno: %d)",
			 remote_path, strerror(errno), errno);
		goto return__;
	}

	if ((ret = buf_get_u32(msgr, (uint32_t *)&rc)) != 0 ||
	    (ret = buf_get_u32(msgr, (uint32_t *)&errno)) != 0) {
		ErrorLog("get_u32 failure. %s failure. %s(errno: %d)",
			 remote_path, strerror(errno), errno);
		goto return__;
	}

	ret = rc;
	if (ret != 0 && errno != EEXIST) {
		ErrorLog("mkdir %s failure. %s(errno: %d)", remote_path,
			 strerror(errno), errno);
		goto return__;
	} else {
		if (g_rpc_config->debug) {
			InfoLog("mkdir %s success.", remote_path);
		}
	}

return__:
	return ret;
}

int rpc_conn_cli_fchownats(struct rpc_conn *conn, const char *remote_path,
			   std::vector<fchownat_info> items)
{
	int ret = 0;
	int rc = 0;
	int rc_tmp = 0;
	struct buf *msgw = conn->msgw;
	struct buf *msgr = conn->msgr;
	uint32_t count = items.size();

	if ((ret = buf_put_u8(msgw, NEW_CONN_TMP_FCHOWNATS)) != 0 ||
	    (ret = buf_put_u32(msgw, count)) != 0 ||
	    (ret = buf_put_cstring(msgw, remote_path)) != 0) {
		ErrorLog("put_cstring failure. %s failure. %s(errno: %d)",
			 remote_path, strerror(errno), errno);
		goto return__;
	}

	for (auto item : items) {
		if ((ret = buf_put_u32(msgw, item.uid)) != 0 ||
		    (ret = buf_put_u32(msgw, item.gid)) != 0 ||
		    (ret = buf_put_cstring(msgw, item.path.c_str())) != 0) {
			ErrorLog("put_u32 failure. %s failure. %s(errno: %d)",
				 remote_path, strerror(errno), errno);
			goto return__;
		}
	}

	ret = rpc_conn_reconn_send_msg(conn);
	if (ret != 0) {
		ErrorLog(
			"rpc_conn_reconn_send_msg failure. %s failure. %s(errno: %d)",
			remote_path, strerror(errno), errno);
		goto return__;
	}

	ret = rpc_conn_is_ready_recv_msg(conn);
	if (ret != 0) {
		ErrorLog("rpc_conn_recv_msg failure. %s failure. %s(errno: %d)",
			 remote_path, strerror(errno), errno);
		goto return__;
	}

	if ((ret = buf_get_u32(msgr, (uint32_t *)&rc)) != 0 ||
	    (ret = buf_get_u32(msgr, (uint32_t *)&errno)) != 0) {
		ErrorLog("get_u32 failure. %s failure. %s(errno: %d)",
			 remote_path, strerror(errno), errno);
		goto return__;
	}

	ret = rc;
	if (ret != 0) {
		ErrorLog("fchownats %s failure. %s(errno: %d)", remote_path,
			 strerror(errno), errno);
		goto return__;
	}

	for (uint32_t i = 0; i < count; i++) {
		if ((ret = buf_get_u32(msgr, (uint32_t *)&rc)) != 0 ||
		    (ret = buf_get_u32(msgr, (uint32_t *)&errno)) != 0) {
			ErrorLog("get_u32 failure. %s failure. %s(errno: %d)",
				 remote_path, strerror(errno), errno);
			goto return__;
		}
		if (rc != 0) {
			ErrorLog("fchownat %s:%s failure. %s(errno: %d)",
				 remote_path, items[i].path.c_str(),
				 strerror(errno), errno);
			rc_tmp = -1;
		}
	}

	ret = rc_tmp;
	if (ret != 0) {
		ErrorLog("fchownats %s failure. %s(errno: %d)", remote_path,
			 strerror(errno), errno);
		goto return__;
	} else {
		if (g_rpc_config->debug) {
			InfoLog("fchownats %s success.", remote_path);
		}
	}
return__:
	return ret;
}

int rpc_conn_cli_fchmodats(struct rpc_conn *conn, const char *remote_path,
			   std::vector<fchmodat_info> items)
{
	int ret = 0;
	int rc = 0;
	int rc_tmp = 0;
	struct buf *msgw = conn->msgw;
	struct buf *msgr = conn->msgr;
	uint32_t count = items.size();

	if ((ret = buf_put_u8(msgw, NEW_CONN_TMP_FCHMODATS)) != 0 ||
	    (ret = buf_put_u32(msgw, count)) != 0 ||
	    (ret = buf_put_cstring(msgw, remote_path)) != 0) {
		ErrorLog("put_cstring failure. %s failure. %s(errno: %d)",
			 remote_path, strerror(errno), errno);
		goto return__;
	}

	for (auto item : items) {
		if ((ret = buf_put_u32(msgw, item.mode)) != 0 ||
		    (ret = buf_put_cstring(msgw, item.path.c_str())) != 0) {
			ErrorLog("put_u32 failure. %s failure. %s(errno: %d)",
				 remote_path, strerror(errno), errno);
			goto return__;
		}
	}

	ret = rpc_conn_reconn_send_msg(conn);
	if (ret != 0) {
		ErrorLog(
			"rpc_conn_reconn_send_msg failure. %s failure. %s(errno: %d)",
			remote_path, strerror(errno), errno);
		goto return__;
	}

	ret = rpc_conn_is_ready_recv_msg(conn);
	if (ret != 0) {
		ErrorLog("rpc_conn_recv_msg failure. %s failure. %s(errno: %d)",
			 remote_path, strerror(errno), errno);
		goto return__;
	}

	if ((ret = buf_get_u32(msgr, (uint32_t *)&rc)) != 0 ||
	    (ret = buf_get_u32(msgr, (uint32_t *)&errno)) != 0) {
		ErrorLog("get_u32 failure. %s failure. %s(errno: %d)",
			 remote_path, strerror(errno), errno);
		goto return__;
	}

	ret = rc;
	if (ret != 0) {
		ErrorLog("fchmodats %s failure. %s(errno: %d)", remote_path,
			 strerror(errno), errno);
		goto return__;
	}

	for (uint32_t i = 0; i < count; i++) {
		if ((ret = buf_get_u32(msgr, (uint32_t *)&rc)) != 0 ||
		    (ret = buf_get_u32(msgr, (uint32_t *)&errno)) != 0) {
			ErrorLog("get_u32 failure. %s failure. %s(errno: %d)",
				 remote_path, strerror(errno), errno);
			goto return__;
		}
		if (rc != 0) {
			ErrorLog("fchownat %s:%s failure. %s(errno: %d)",
				 remote_path, items[i].path.c_str(),
				 strerror(errno), errno);
			rc_tmp = -1;
		}
	}

	ret = rc_tmp;
	if (ret != 0) {
		ErrorLog("fchmodats %s failure. %s(errno: %d)", remote_path,
			 strerror(errno), errno);
		goto return__;
	} else {
		if (g_rpc_config->debug) {
			InfoLog("fchmodats %s success.", remote_path);
		}
	}
return__:
	return ret;
}

int rpc_conn_cli_download_fileats(struct rpc_conn *conn,
				  const char *remote_path,
				  const char *local_path,
				  std::vector<download_fileat_info> items)
{
	int ret = 0;
	int rc = 0;
	int rc_tmp = 0;
	int dirfd = -1;
	int fd = -1;
	struct buf *msgw = conn->msgw;
	struct buf *msgr = conn->msgr;
	uint32_t count = items.size();

	dirfd = open(local_path, O_DIRECTORY | O_RDONLY);
	if (dirfd < 0) {
		ErrorLog("open %s failure. %s(errno: %d)", local_path,
			 strerror(errno), errno);
		ret = -1;
		goto return__;
	}
	if ((ret = buf_put_u8(msgw, NEW_CONN_TMP_DOWNLOAD_FILEATS)) != 0 ||
	    (ret = buf_put_u32(msgw, count)) != 0 ||
	    (ret = buf_put_cstring(msgw, remote_path)) != 0) {
		ErrorLog("put_cstring failure. %s failure. %s(errno: %d)",
			 remote_path, strerror(errno), errno);
		goto return__;
	}

	for (auto item : items) {
		if ((ret = buf_put_cstring(msgw, item.path.c_str())) != 0) {
			ErrorLog("put_u32 failure. %s failure. %s(errno: %d)",
				 remote_path, strerror(errno), errno);
			goto return__;
		}
	}

	ret = rpc_conn_reconn_send_msg(conn);
	if (ret != 0) {
		ErrorLog(
			"rpc_conn_reconn_send_msg failure. %s failure. %s(errno: %d)",
			remote_path, strerror(errno), errno);
		goto return__;
	}

	ret = rpc_conn_is_ready_recv_msg(conn);
	if (ret != 0) {
		ErrorLog("rpc_conn_recv_msg failure. %s failure. %s(errno: %d)",
			 remote_path, strerror(errno), errno);
		goto return__;
	}

	if ((ret = buf_get_u32(msgr, (uint32_t *)&rc)) != 0 ||
	    (ret = buf_get_u32(msgr, (uint32_t *)&errno)) != 0) {
		ErrorLog("get_u32 failure. %s failure. %s(errno: %d)",
			 remote_path, strerror(errno), errno);
		goto return__;
	}

	ret = rc;
	if (ret != 0) {
		ErrorLog("download_fileats %s failure. %s(errno: %d)",
			 remote_path, strerror(errno), errno);
		goto return__;
	}

	for (uint32_t i = 0; i < count; i++) {
		ret = rpc_conn_is_ready_recv_msg(conn);
		if (ret != 0) {
			ErrorLog(
				"rpc_conn_recv_msg failure. %s failure. %s(errno: %d)",
				remote_path, strerror(errno), errno);
			goto return__;
		}

		if ((ret = buf_get_u32(msgr, (uint32_t *)&rc)) != 0 ||
		    (ret = buf_get_u32(msgr, (uint32_t *)&errno)) != 0) {
			ErrorLog(
				"get_u32 failure. %s:%s failure. %s(errno: %d)",
				remote_path, items[i].path.c_str(),
				strerror(errno), errno);
			goto return__;
		}
		if (rc != 0) {
			if (errno == ENOENT) {
				WarningLog(
					"download_fileat %s:%s failure. %s(errno: %d)",
					remote_path, items[i].path.c_str(),
					strerror(errno), errno);
			} else {
				ErrorLog(
					"download_fileat %s:%s failure. %s(errno: %d)",
					remote_path, items[i].path.c_str(),
					strerror(errno), errno);
				rc_tmp = -1;
			}
			continue;
		}

		fd = openat(dirfd, items[i].path.c_str(),
			    O_WRONLY | O_CREAT | O_TRUNC, 0644);
		if (fd < 0) {
			rpc_conn_close(conn);
			ErrorLog("openat %s failure. %s(errno: %d)", local_path,
				 strerror(errno), errno);
			ret = -1;
			goto return__;
		}

		while (true) {
			const char *data = NULL;
			size_t len = 0;

			if ((ret = buf_get_u32(msgr, (uint32_t *)&rc)) != 0 ||
			    (ret = buf_get_u32(msgr, (uint32_t *)&errno)) !=
				    0) {
				ErrorLog(
					"get_u32 failure. %s failure. %s(errno: %d)",
					remote_path, strerror(errno), errno);
				goto return__;
			}
			if (rc < 0) {
				ErrorLog(
					"download_fileat %s:%s failure. %s(errno: %d)",
					remote_path, items[i].path.c_str(),
					strerror(errno), errno);
				break;
			} else if (rc == 0) {
				InfoLog("download_fileat %s:%s success.",
					remote_path, items[i].path.c_str());
				break;
			}
			if ((ret = buf_get_string_direct(msgr,
							 (const u_char **)&data,
							 &len)) != 0) {
				ErrorLog(
					"get_string_direct failure. %s failure. %s(errno: %d)",
					remote_path, strerror(errno), errno);
				goto return__;
			}
			if (write(fd, data, len) != (ssize_t)len) {
				rpc_conn_close(conn);
				ErrorLog("write %s failure. %s(errno: %d)",
					 local_path, strerror(errno), errno);
				ret = -1;
				goto return__;
			}

			ret = rpc_conn_is_ready_recv_msg(conn);
			if (ret != 0) {
				ErrorLog(
					"rpc_conn_recv_msg failure. %s failure. %s(errno: %d)",
					remote_path, strerror(errno), errno);
				goto return__;
			}
		}
		close(fd);
		fd = -1;
	}

	ret = rc_tmp;

return__:
	if (fd >= 0) {
		close(fd);
	}
	if (dirfd >= 0) {
		close(dirfd);
	}
	return ret;
}

int rpc_conn_cli_upload_fileats(struct rpc_conn *conn, const char *local_path,
				const char *remote_path,
				std::vector<upload_fileat_info> items)
{
	int ret = 0;
	int rc = 0;
	int dirfd = -1;
	int fd = -1;
	struct buf *msgw = conn->msgw;
	struct buf *msgr = conn->msgr;
	uint32_t count = items.size();

	// TODO: buf size limit
	char read_buf[4096];

	dirfd = open(local_path, O_DIRECTORY | O_RDONLY);
	if (dirfd < 0) {
		ErrorLog("open %s failure. %s(errno: %d)", local_path,
			 strerror(errno), errno);
		ret = -1;
		goto return__;
	}
	if ((ret = buf_put_u8(msgw, NEW_CONN_TMP_UPLOAD_FILEATS)) != 0 ||
	    (ret = buf_put_u32(msgw, count)) != 0 ||
	    (ret = buf_put_cstring(msgw, remote_path)) != 0) {
		ErrorLog("put_cstring failure. %s failure. %s(errno: %d)",
			 remote_path, strerror(errno), errno);
		goto return__;
	}

	ret = rpc_conn_reconn_send_msg(conn);
	if (ret != 0) {
		ErrorLog(
			"rpc_conn_reconn_send_msg failure. %s failure. %s(errno: %d)",
			remote_path, strerror(errno), errno);
		goto return__;
	}

	ret = rpc_conn_is_ready_recv_msg(conn);
	if (ret != 0) {
		ErrorLog("rpc_conn_recv_msg failure. %s failure. %s(errno: %d)",
			 remote_path, strerror(errno), errno);
		goto return__;
	}

	if ((ret = buf_get_u32(msgr, (uint32_t *)&rc)) != 0 ||
	    (ret = buf_get_u32(msgr, (uint32_t *)&errno)) != 0) {
		ErrorLog("get_u32 failure. %s failure. %s(errno: %d)",
			 remote_path, strerror(errno), errno);
		goto return__;
	}

	if (rc != 0) {
		ErrorLog("upload_fileats %s failure. %s(errno: %d)",
			 remote_path, strerror(errno), errno);
		goto return__;
	}

	for (auto item : items) {
		fd = openat(dirfd, item.path.c_str(), O_RDONLY, 0644);
		if ((ret = buf_put_cstring(msgw, item.path.c_str())) != 0 ||
		    (ret = buf_put_u32(msgw, fd < 0 ? -1 : 0)) != 0 ||
		    (ret = buf_put_u32(msgw, errno)) != 0) {
			ErrorLog("put_u32 failure. %s failure. %s(errno: %d)",
				 remote_path, strerror(errno), errno);
			goto return__;
		}
		if (fd < 0) {
			ErrorLog("openat %s failure. %s(errno: %d)", local_path,
				 strerror(errno), errno);
			ret = rpc_conn_send_msg(conn);
			if (ret != 0) {
				ErrorLog(
					"rpc_conn_send_msg failure. %s failure. %s(errno: %d)",
					remote_path, strerror(errno), errno);
				goto return__;
			}
			if (errno == ENOENT) {
				continue;
			}
			ret = -1;
			goto return__;
		}

		while (true) {
			ssize_t len = read(fd, read_buf, sizeof(read_buf));
			if ((ret = buf_put_u32(msgw, len)) != 0 ||
			    (ret = buf_put_u32(msgw, errno)) != 0) {
				ErrorLog(
					"put_u32 failure. %s failure. %s(errno: %d)",
					remote_path, strerror(errno), errno);
				goto return__;
			}
			if (len < 0) {
				rpc_conn_close(conn);
				ErrorLog("read %s failure. %s(errno: %d)",
					 local_path, strerror(errno), errno);
				ret = -1;
				goto return__;
			} else if (len == 0) {
				InfoLog("upload_fileat %s:%s success.",
					remote_path, item.path.c_str());
				break;
			}
			if ((ret = buf_put_string(msgw, read_buf, len)) != 0) {
				ErrorLog(
					"put_string failure. %s failure. %s(errno: %d)",
					remote_path, strerror(errno), errno);
				goto return__;
			}
			ret = rpc_conn_send_msg(conn);
			if (ret != 0) {
				ErrorLog(
					"rpc_conn_send_msg failure. %s failure. %s(errno: %d)",
					remote_path, strerror(errno), errno);
				goto return__;
			}
		}
		if ((ret = rpc_conn_send_msg(conn)) != 0) {
			ErrorLog(
				"rpc_conn_send_msg failure. %s failure. %s(errno: %d)",
				remote_path, strerror(errno), errno);
			goto return__;
		}
		close(fd);
		fd = -1;
	}

	ret = rpc_conn_is_ready_recv_msg(conn);
	if (ret != 0) {
		ErrorLog("rpc_conn_recv_msg failure. %s failure. %s(errno: %d)",
			 remote_path, strerror(errno), errno);
		goto return__;
	}

	if ((ret = buf_get_u32(msgr, (uint32_t *)&rc)) != 0 ||
	    (ret = buf_get_u32(msgr, (uint32_t *)&errno)) != 0) {
		ErrorLog("get_u32 failure. %s failure. %s(errno: %d)",
			 remote_path, strerror(errno), errno);
		goto return__;
	}

	ret = rc;

return__:
	if (fd >= 0) {
		close(fd);
	}
	if (dirfd >= 0) {
		close(dirfd);
	}
	return ret;
}

int rpc_conn_cli_readlink(struct rpc_conn *conn, const char *remote_path,
			  const char *local_path)
{
	int ret = 0;
	int rc = 0;
	struct buf *msgw = conn->msgw;
	struct buf *msgr = conn->msgr;
	char *link_target = NULL;

	if ((ret = buf_put_u8(msgw, NEW_CONN_TMP_READLINK)) != 0 ||
	    (ret = buf_put_cstring(msgw, remote_path)) != 0) {
		ErrorLog("put_cstring failure. %s failure. %s(errno: %d)",
			 remote_path, strerror(errno), errno);
		goto return__;
	}

	ret = rpc_conn_reconn_send_msg(conn);
	if (ret != 0) {
		ErrorLog(
			"rpc_conn_reconn_send_msg failure. %s failure. %s(errno: %d)",
			remote_path, strerror(errno), errno);
		goto return__;
	}

	ret = rpc_conn_is_ready_recv_msg(conn);
	if (ret != 0) {
		ErrorLog("rpc_conn_recv_msg failure. %s failure. %s(errno: %d)",
			 remote_path, strerror(errno), errno);
		goto return__;
	}

	if ((ret = buf_get_u32(msgr, (uint32_t *)&rc)) != 0 ||
	    (ret = buf_get_u32(msgr, (uint32_t *)&errno)) != 0) {
		ErrorLog("get_u32 failure. %s failure. %s(errno: %d)",
			 remote_path, strerror(errno), errno);
		goto return__;
	}

	ret = rc;
	if (ret != 0) {
		ErrorLog("readlink %s failure. %s(errno: %d)", remote_path,
			 strerror(errno), errno);
		goto return__;
	}

	if ((ret = buf_get_cstring(msgr, &link_target, 0)) != 0) {
		ErrorLog("get_string failure. %s failure. %s(errno: %d)",
			 remote_path, strerror(errno), errno);
		goto return__;
	}

	if (symlink(link_target, local_path) != 0) {
		ErrorLog("symlink %s -> %s failure. %s(errno: %d)", local_path,
			 link_target, strerror(errno), errno);
		ret = -1;
		goto return__;
	} else {
		if (g_rpc_config->debug) {
			InfoLog("symlink %s -> %s success.", local_path,
				link_target);
		}
	}

return__:

	if (link_target) {
		free(link_target);
	}
	return ret;
}

int rpc_conn_cli_symlink(struct rpc_conn *conn, const char *local_path,
			 const char *remote_path)
{
	int ret = 0;
	int rc = 0;
	struct buf *msgw = conn->msgw;
	struct buf *msgr = conn->msgr;
	char link_target[PATH_MAX];

	if (readlink(local_path, link_target, sizeof(link_target)) < 0) {
		ErrorLog("readlink %s failure. %s(errno: %d)", local_path,
			 strerror(errno), errno);
		ret = -1;
		goto return__;
	}

	if ((ret = buf_put_u8(msgw, NEW_CONN_TMP_SYMLINK)) != 0 ||
	    (ret = buf_put_cstring(msgw, link_target)) != 0 ||
	    (ret = buf_put_cstring(msgw, remote_path)) != 0) {
		ErrorLog("put_cstring failure. %s failure. %s(errno: %d)",
			 remote_path, strerror(errno), errno);
		goto return__;
	}

	ret = rpc_conn_reconn_send_msg(conn);
	if (ret != 0) {
		ErrorLog(
			"rpc_conn_reconn_send_msg failure. %s failure. %s(errno: %d)",
			remote_path, strerror(errno), errno);
		goto return__;
	}

	ret = rpc_conn_is_ready_recv_msg(conn);
	if (ret != 0) {
		ErrorLog("rpc_conn_recv_msg failure. %s failure. %s(errno: %d)",
			 remote_path, strerror(errno), errno);
		goto return__;
	}

	if ((ret = buf_get_u32(msgr, (uint32_t *)&rc)) != 0 ||
	    (ret = buf_get_u32(msgr, (uint32_t *)&errno)) != 0) {
		ErrorLog("get_u32 failure. %s failure. %s(errno: %d)",
			 remote_path, strerror(errno), errno);
		goto return__;
	}

	ret = rc;
	if (ret != 0) {
		ErrorLog("symlink %s failure. %s(errno: %d)", remote_path,
			 strerror(errno), errno);
		goto return__;
	} else {
		if (g_rpc_config->debug) {
			InfoLog("symlink %s -> %s success.", local_path,
				link_target);
		}
	}

return__:

	return ret;
}

int rpc_conn_cli_access(struct rpc_conn *conn, const char *remote_path,
			int type)
{
	int ret = 0;
	int rc = 0;
	struct buf *msgw = conn->msgw;
	struct buf *msgr = conn->msgr;

	if ((ret = buf_put_u8(msgw, NEW_CONN_TMP_ACCESS)) != 0 ||
	    (ret = buf_put_u32(msgw, type)) != 0 ||
	    (ret = buf_put_cstring(msgw, remote_path)) != 0) {
		ErrorLog("put_cstring failure. %s failure. %s(errno: %d)",
			 remote_path, strerror(errno), errno);
		goto return__;
	}

	ret = rpc_conn_reconn_send_msg(conn);
	if (ret != 0) {
		ErrorLog(
			"rpc_conn_reconn_send_msg failure. %s failure. %s(errno: %d)",
			remote_path, strerror(errno), errno);
		goto return__;
	}

	ret = rpc_conn_is_ready_recv_msg(conn);
	if (ret != 0) {
		ErrorLog("rpc_conn_recv_msg failure. %s failure. %s(errno: %d)",
			 remote_path, strerror(errno), errno);
		goto return__;
	}

	if ((ret = buf_get_u32(msgr, (uint32_t *)&rc)) != 0 ||
	    (ret = buf_get_u32(msgr, (uint32_t *)&errno)) != 0) {
		ErrorLog("get_u32 failure. %s failure. %s(errno: %d)",
			 remote_path, strerror(errno), errno);
		goto return__;
	}

	ret = rc;
	if (ret != 0) {
		ErrorLog("access %s failure. %s(errno: %d)", remote_path,
			 strerror(errno), errno);
		goto return__;
	} else {
		if (g_rpc_config->debug) {
			InfoLog("access %s success.", remote_path);
		}
	}

return__:

	return ret;
}

int rpc_conn_cli_mkdirall(struct rpc_conn *conn, const char *remote_path)
{
	int ret = 0;
	int rc = 0;
	struct buf *msgw = conn->msgw;
	struct buf *msgr = conn->msgr;

	if ((ret = buf_put_u8(msgw, NEW_CONN_TMP_MKDIRALL)) != 0 ||
	    (ret = buf_put_cstring(msgw, remote_path)) != 0) {
		ErrorLog("put_cstring failure. %s failure. %s(errno: %d)",
			 remote_path, strerror(errno), errno);
		goto return__;
	}

	ret = rpc_conn_reconn_send_msg(conn);
	if (ret != 0) {
		ErrorLog(
			"rpc_conn_reconn_send_msg failure. %s failure. %s(errno: %d)",
			remote_path, strerror(errno), errno);
		goto return__;
	}

	ret = rpc_conn_is_ready_recv_msg(conn);
	if (ret != 0) {
		ErrorLog("rpc_conn_recv_msg failure. %s failure. %s(errno: %d)",
			 remote_path, strerror(errno), errno);
		goto return__;
	}

	if ((ret = buf_get_u32(msgr, (uint32_t *)&rc)) != 0 ||
	    (ret = buf_get_u32(msgr, (uint32_t *)&errno)) != 0) {
		ErrorLog("get_u32 failure. %s failure. %s(errno: %d)",
			 remote_path, strerror(errno), errno);
		goto return__;
	}

	ret = rc;
	if (ret != 0) {
		ErrorLog("mkdir %s failure. %s(errno: %d)", remote_path,
			 strerror(errno), errno);
		goto return__;
	} else {
		if (g_rpc_config->debug) {
			InfoLog("mkdir %s success.", remote_path);
		}
	}

return__:
	return ret;
}

int rpc_conn_cli_chmod(struct rpc_conn *conn, const char *remote_path,
		       mode_t mode)
{
	int ret = 0;
	int rc = 0;
	struct buf *msgw = conn->msgw;
	struct buf *msgr = conn->msgr;

	if ((ret = buf_put_u8(msgw, NEW_CONN_TMP_CHMOD)) != 0 ||
	    (ret = buf_put_u32(msgw, mode)) != 0 ||
	    (ret = buf_put_cstring(msgw, remote_path)) != 0) {
		ErrorLog("put_cstring failure. %s failure. %s(errno: %d)",
			 remote_path, strerror(errno), errno);
		goto return__;
	}

	ret = rpc_conn_reconn_send_msg(conn);
	if (ret != 0) {
		ErrorLog(
			"rpc_conn_reconn_send_msg failure. %s failure. %s(errno: %d)",
			remote_path, strerror(errno), errno);
		goto return__;
	}

	ret = rpc_conn_is_ready_recv_msg(conn);
	if (ret != 0) {
		ErrorLog("rpc_conn_recv_msg failure. %s failure. %s(errno: %d)",
			 remote_path, strerror(errno), errno);
		goto return__;
	}

	if ((ret = buf_get_u32(msgr, (uint32_t *)&rc)) != 0 ||
	    (ret = buf_get_u32(msgr, (uint32_t *)&errno)) != 0) {
		ErrorLog("get_u32 failure. %s failure. %s(errno: %d)",
			 remote_path, strerror(errno), errno);
		goto return__;
	}

	ret = rc;
	if (ret != 0) {
		ErrorLog("chmod %s failure. %s(errno: %d)", remote_path,
			 strerror(errno), errno);
		goto return__;
	} else {
		if (g_rpc_config->debug) {
			InfoLog("chmod %s success.", remote_path);
		}
	}

return__:
	return ret;
}

int rpc_conn_cli_chown(struct rpc_conn *conn, const char *remote_path,
		       uid_t uid, gid_t gid)
{
	int ret = 0;
	int rc = 0;
	struct buf *msgw = conn->msgw;
	struct buf *msgr = conn->msgr;

	if ((ret = buf_put_u8(msgw, NEW_CONN_TMP_CHOWN)) != 0 ||
	    (ret = buf_put_u32(msgw, uid)) != 0 ||
	    (ret = buf_put_u32(msgw, gid)) != 0 ||
	    (ret = buf_put_cstring(msgw, remote_path)) != 0) {
		ErrorLog("put_cstring failure. %s failure. %s(errno: %d)",
			 remote_path, strerror(errno), errno);
		goto return__;
	}

	ret = rpc_conn_reconn_send_msg(conn);
	if (ret != 0) {
		ErrorLog(
			"rpc_conn_reconn_send_msg failure. %s failure. %s(errno: %d)",
			remote_path, strerror(errno), errno);
		goto return__;
	}

	ret = rpc_conn_is_ready_recv_msg(conn);
	if (ret != 0) {
		ErrorLog("rpc_conn_recv_msg failure. %s failure. %s(errno: %d)",
			 remote_path, strerror(errno), errno);
		goto return__;
	}

	if ((ret = buf_get_u32(msgr, (uint32_t *)&rc)) != 0 ||
	    (ret = buf_get_u32(msgr, (uint32_t *)&errno)) != 0) {
		ErrorLog("get_u32 failure. %s failure. %s(errno: %d)",
			 remote_path, strerror(errno), errno);
		goto return__;
	}

	ret = rc;
	if (ret != 0) {
		ErrorLog("chown %s failure. %s(errno: %d)", remote_path,
			 strerror(errno), errno);
		goto return__;
	} else {
		if (g_rpc_config->debug) {
			InfoLog("chown %s success.", remote_path);
		}
	}

return__:
	return ret;
}

int rpc_conn_cli_openat(struct rpc_conn *conn, int fd, const char *remote_name,
			int flag, int mode)
{
	int ret = 0;
	int rc = 0;
	struct buf *msgw = conn->msgw;
	struct buf *msgr = conn->msgr;

	if ((ret = buf_put_u8(msgw, NEW_CONN_TMP_OPENAT)) != 0 ||
	    (ret = buf_put_u32(msgw, fd)) != 0 ||
	    (ret = buf_put_u32(msgw, flag)) != 0 ||
	    (ret = buf_put_u32(msgw, mode)) != 0 ||
	    (ret = buf_put_cstring(msgw, remote_name)) != 0) {
		ErrorLog("put_cstring failure. %s failure. %s(errno: %d)",
			 remote_name, strerror(errno), errno);
		goto return__;
	}

	ret = rpc_conn_reconn_send_msg(conn);
	if (ret != 0) {
		ErrorLog(
			"rpc_conn_reconn_send_msg failure. %s failure. %s(errno: %d)",
			remote_name, strerror(errno), errno);
		goto return__;
	}

	ret = rpc_conn_is_ready_recv_msg(conn);
	if (ret != 0) {
		ErrorLog("rpc_conn_recv_msg failure. %s failure. %s(errno: %d)",
			 remote_name, strerror(errno), errno);
		goto return__;
	}

	if ((ret = buf_get_u32(msgr, (uint32_t *)&rc)) != 0 ||
	    (ret = buf_get_u32(msgr, (uint32_t *)&errno)) != 0) {
		ErrorLog("get_u32 failure. %s failure. %s(errno: %d)",
			 remote_name, strerror(errno), errno);
		goto return__;
	}

	ret = rc;
	if (ret < 0) {
		ErrorLog("openat %s failure. %s(errno: %d)", remote_name,
			 strerror(errno), errno);
		goto return__;
	} else {
		if (g_rpc_config->debug) {
			InfoLog("openat %s success.", remote_name);
		}
	}

return__:
	return ret;
}

int rpc_conn_cli_download_fileat(struct rpc_conn *conn, int remote_fd,
				 int local_fd, const char *name)
{
	int ret = 0;
	int rc = 0;
	int rc_tmp = 0;
	// TODO: 连接创建时进行设置
	uint32_t chunk_len = PREAD_CHUNK_SIZE;
	struct buf *msgw = conn->msgw;
	struct buf *msgr = conn->msgr;
	size_t recv_len = 0;

	rc = openat(local_fd, name, O_WRONLY | O_CREAT | O_TRUNC, 0644);
	if (rc < 0) {
		ErrorLog("open %s failure. %s(errno: %d)", name,
			 strerror(errno), errno);
		ret = -1;
		goto return__;
	}

	if ((ret = buf_put_u8(msgw, NEW_CONN_TMP_DOWNLOAD_FILEAT)) != 0 ||
	    (ret = buf_put_u32(msgw, remote_fd)) != 0 ||
	    (ret = buf_put_cstring(msgw, name)) != 0) {
		ErrorLog("put_cstring failure. %s failure. %s(errno: %d)", name,
			 strerror(errno), errno);
		goto return__;
	}

	ret = rpc_conn_reconn_send_msg(conn);
	if (ret != 0) {
		ErrorLog(
			"rpc_conn_reconn_send_msg failure. %s failure. %s(errno: %d)",
			name, strerror(errno), errno);
		goto return__;
	}

	while (1) {
		const char *data = NULL;
		size_t len = 0;

		ret = rpc_conn_is_ready_recv_msg(conn);
		if (ret != 0) {
			ErrorLog(
				"rpc_conn_is_ready_recv_msg failure. %s failure. %s(errno: %d)",
				name, strerror(errno), errno);
			goto return__;
		}

		if ((ret = buf_get_u32(msgr, (uint32_t *)&rc_tmp)) != 0) {
			ErrorLog("get_u32 failure. %s failure. %s(errno: %d)",
				 name, strerror(errno), errno);
			goto return__;
		}

		if (rc_tmp < 0) {
			if ((ret = buf_get_u32(msgr, (uint32_t *)&errno)) !=
			    0) {
				ErrorLog(
					"get_u32 failure. %s failure. %s(errno: %d)",
					name, strerror(errno), errno);
				goto return__;
			}
			ret = -1;
			ErrorLog("read %s failure. %s(errno: %d)", name,
				 strerror(errno), errno);
			goto return__;
		} else if (rc_tmp > 0) {
			if ((ret = buf_get_string_direct(msgr,
							 (const u_char **)&data,
							 &len)) != 0) {
				ErrorLog(
					"get_string_direct failure. %s failure. %s(errno: %d)",
					name, strerror(errno), errno);
				goto return__;
			}
			if (write(rc, data, len) != (ssize_t)len) {
				ret = -1;
				ErrorLog("write %s failure. %s(errno: %d)",
					 name, strerror(errno), errno);
				rpc_conn_close(conn);
				goto return__;
			}
			recv_len += len;
			if (rc_tmp < (int)chunk_len) {
				if (g_rpc_config->debug) {
					InfoLog("%s done. %d bytes received.",
						name, recv_len);
				}
				break;
			}
		} else {
			if (g_rpc_config->debug) {
				InfoLog("%s done. %d bytes received.", name,
					recv_len);
			}
			break;
		}
	}

	ret = 0;

return__:
	if (rc > 0) {
		close(rc);
		if (ret != 0) {
			unlinkat(local_fd, name, 0);
		}
	}
	return ret;
}

int rpc_conn_cli_readlinkat(struct rpc_conn *conn, int remote_fd, int local_fd,
			    const char *name)
{
	int ret = 0;
	int rc = 0;
	struct buf *msgw = conn->msgw;
	struct buf *msgr = conn->msgr;
	char *link_target = NULL;

	if ((ret = buf_put_u8(msgw, NEW_CONN_TMP_READLINKAT)) != 0 ||
	    (ret = buf_put_u32(msgw, remote_fd)) != 0 ||
	    (ret = buf_put_cstring(msgw, name)) != 0) {
		ErrorLog("put_cstring failure. %s failure. %s(errno: %d)", name,
			 strerror(errno), errno);
		goto return__;
	}

	ret = rpc_conn_reconn_send_msg(conn);
	if (ret != 0) {
		ErrorLog(
			"rpc_conn_reconn_send_msg failure. %s failure. %s(errno: %d)",
			name, strerror(errno), errno);
		goto return__;
	}

	ret = rpc_conn_is_ready_recv_msg(conn);
	if (ret != 0) {
		ErrorLog("rpc_conn_recv_msg failure. %s failure. %s(errno: %d)",
			 name, strerror(errno), errno);
		goto return__;
	}

	if ((ret = buf_get_u32(msgr, (uint32_t *)&rc)) != 0 ||
	    (ret = buf_get_u32(msgr, (uint32_t *)&errno)) != 0) {
		ErrorLog("get_u32 failure. %s failure. %s(errno: %d)", name,
			 strerror(errno), errno);
		goto return__;
	}

	ret = rc;
	if (ret != 0) {
		ErrorLog("readlinkat %s failure. %s(errno: %d)", name,
			 strerror(errno), errno);
		goto return__;
	}

	if ((ret = buf_get_cstring(msgr, &link_target, 0)) != 0) {
		ErrorLog("get_string failure. %s failure. %s(errno: %d)", name,
			 strerror(errno), errno);
		goto return__;
	}

	if (symlinkat(link_target, local_fd, name) != 0) {
		ErrorLog("symlinkat %s -> %s failure. %s(errno: %d)", name,
			 link_target, strerror(errno), errno);
		ret = -1;
		goto return__;
	} else {
		if (g_rpc_config->debug) {
			InfoLog("symlinkat %s -> %s success.", name,
				link_target);
		}
	}

return__:

	if (link_target) {
		free(link_target);
	}
	return ret;
}

int rpc_conn_cli_download_file_dir(struct rpc_conn *conn,
				   const char *remote_dir, int local_fd,
				   const char *name)
{
	if (conn->remote_dir_path != remote_dir) {
		conn->remote_dir_fd = rpc_conn_cli_openat(
			conn, AT_FDCWD, remote_dir, O_DIRECTORY, 0);
		if (conn->remote_dir_fd < 0)
			return -1;
		conn->remote_dir_path = remote_dir;
	}

	return rpc_conn_cli_download_fileat(conn, conn->remote_dir_fd, local_fd,
					    name);
}

int rpc_conn_cli_readlink_dir(struct rpc_conn *conn, const char *remote_dir,
			      int local_fd, const char *name)
{
	if (conn->remote_dir_path != remote_dir) {
		conn->remote_dir_fd = rpc_conn_cli_openat(
			conn, AT_FDCWD, remote_dir, O_DIRECTORY, 0);
		if (conn->remote_dir_fd < 0)
			return -1;
		conn->remote_dir_path = remote_dir;
	}

	return rpc_conn_cli_readlinkat(conn, conn->remote_dir_fd, local_fd,
				       name);
}
