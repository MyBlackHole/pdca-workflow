#include "buf.h"
#include "rpc-command.h"
#include "rpc-common.h"
#include "rpc.h"
#include "utils.h"
#include "crc32.h"
#include "common.h"
#include "rpc-server.h"
#include "logger.h"
#include "rdb-config.h"
#include "thread.h"
#include "rpc-io.h"
#include "rpc-protocol.h"
#include "rpc-config.h"
#include "lz4.h"
#include "file-stat.h"
#include "dev_ioctl.h"
#include "rpc-public.h"
#include "rpc-conn.h"
#include "tls_cert.h"
#include "timed_key.h"
#include "crypt.h"
#include "rpc-negotiate.h"

#include <dirent.h>
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <unistd.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <sys/sendfile.h>
#include <signal.h>
#include <sys/time.h>
#include <sys/wait.h>
#include <sys/uio.h>
#include <sys/ioctl.h>
#include <string.h>

#include "dir_utils.h"

static int new_conn(int connfd, char *net_buf, char *host_buf,
		    char *resp_net_buf, char *resp_host_buf, const int buflen);

RpcService::RpcService()
{
}

RpcService::~RpcService()
{
}

int RpcService::StartRpcService()
{
	int ret = 0;
	ret = create_thread(RPCServiceThread, this);
	if (ret != 0) {
		ErrorLog(
			"create rpc service thread failed status: %s(errno: %d)",
			strerror(errno), errno);
		return -1;
	}
	return 0;
}

void *RpcService::RPCServiceThread(void *arg)
{
	int opt = 1;
	int listenfd = -1;
	int connfd = -1;
	int flags = 0;
	struct sockaddr_in servaddr;
	struct sockaddr_in clnt_addr;
	socklen_t clnt_addr_size = sizeof(clnt_addr);
	RpcService *host = (RpcService *)arg;

	while (true) {
		if ((listenfd = socket(AF_INET, SOCK_STREAM | SOCK_CLOEXEC,
				       0)) < 0) {
			ErrorLog("create socket failed status: %s(errno: %d)",
				 strerror(errno), errno);
			goto tryagain__;
		}

		opt = 1;
		if (setsockopt(listenfd, SOL_SOCKET, SO_REUSEADDR,
			       (const void *)&opt, sizeof(opt))) {
			WarningLog("setsockopt");
		}

		memset(&servaddr, 0, sizeof(servaddr));
		servaddr.sin_family = AF_INET;
		servaddr.sin_addr.s_addr = htonl(INADDR_ANY);
		servaddr.sin_port = htons(g_rpc_config->rpc_port);

		if (bind(listenfd, (struct sockaddr *)&servaddr,
			 sizeof(servaddr)) != 0) {
			ErrorLog("bind socket failed status: %s(errno: %d)",
				 strerror(errno), errno);
			goto tryagain__;
		}

		if (listen(listenfd, 10) != 0) {
			ErrorLog("listen socket failed status: %s(errno: %d)",
				 strerror(errno), errno);
			goto tryagain__;
		}
		InfoLog("service listen rpc port :%d success status: %s(errno: %d)",
			g_rpc_config->rpc_port, strerror(errno), errno);
		break;
tryagain__:
		close(listenfd);
		sleep(1);
	}

	InfoLog("======RPC service waiting for client's request======");
	int keepalive_interval = get_keepalive_interval();

	while (true) {
		if ((connfd = accept4(listenfd, (struct sockaddr *)&clnt_addr,
				      &clnt_addr_size, SOCK_CLOEXEC)) < 0) {
			ErrorLog(
				"accept[%s:%d] socket failed status: %s(errno: %d)",
				inet_ntoa(clnt_addr.sin_addr),
				ntohs(clnt_addr.sin_port), strerror(errno),
				errno);
			goto tryagain__;
		} else {
			InfoLog("accept[%s:%d] socket success status: %s(errno: %d)",
				inet_ntoa(clnt_addr.sin_addr),
				ntohs(clnt_addr.sin_port), strerror(errno),
				errno);
		}

		if (keepalive_interval > 0 &&
		    sock_keepalive(connfd, keepalive_interval) != 0) {
			ErrorLog("sock_keepalive failed");
		}

		flags = fcntl(connfd, F_GETFD, 0);
		fcntl(connfd, F_SETFD, flags | FD_CLOEXEC);

		if (host->RPCService(connfd) != 0) {
			ErrorLog("CLI operation failed.");
		}
	}
	close(connfd);
	close(listenfd);
	exit(0);
	return 0;
}

int RpcService::RPCService(int client)
{
	int ret = 0;
	rpc_service_woker_info *woker_info = new rpc_service_woker_info();
	socklen_t serv_len = sizeof(woker_info->serv);
	woker_info->buf_len = MSG_BUFF_LEN;
	woker_info->connfd = client;
	woker_info->host = this;

	getpeername(client, (struct sockaddr *)&woker_info->serv, &serv_len);

	// StartRPCServiceWoker(woker_info);
	ret = create_thread(StartRPCServiceWoker, woker_info);
	if (ret != 0) {
		ErrorLog("RPC service worker failed status: %s(errno: %d)",
			 strerror(errno), errno);
		delete woker_info;
		return -1;
	}
	return 0;
}

void *RpcService::StartRPCServiceWoker(void *arg)
{
	int ret = 0;

	rpc_service_woker_info *woker_info = (rpc_service_woker_info *)arg;
	int client = woker_info->connfd;
	struct sockaddr_in serv = woker_info->serv;

	char *host_buf = woker_info->host_buf;
	char *net_buf = woker_info->net_buf;
	char *resp_net_buf = woker_info->resp_net_buf;
	char *resp_host_buf = woker_info->resp_host_buf;

	msg_base_t *msg_base_host = (msg_base_t *)host_buf;
	msg_base_t *msg_base_net = (msg_base_t *)net_buf;

	int bytes = 0;

	InfoLog("client connection, addr: [%s:%d].", inet_ntoa(serv.sin_addr),
		ntohs(serv.sin_port));

	/* 单端口协商：accept 后先做独立协商头交换（见 PRD 单端口并存）：
	 * - 识别协商头 → 按双方能力判定（明文 / TLS 升级 / ENC-004 拒绝）；
	 * - 超时未收到（存量明文客户端）→ 配置要求加密则拒绝，否则按明文继续。 */
	{
		const int tls_enable = sec_tool_tls_enabled(
			"rpc_tls_enable", g_rpc_config->tls_enable_cli);
		uint8_t caps = rpc_capability_from_ciphersuites(
			sec_tool_tls_ciphersuites("rpc_tls_ciphersuites",
						  g_rpc_config
							  ->tls_ciphersuites_cli));
		int sm_ready = (caps & RPC_CAP_SM) ? 1 : 0;
		int tls_ready = (caps & RPC_CAP_TLS) ? 1 : 0;
		int upgrade = -1;
		int neg = rpc_negotiate_server(client, tls_enable, sm_ready,
					       tls_ready, &upgrade);
		if (neg == RPC_NEG_ERR_TIMEOUT) {
			if (tls_enable) {
				ErrorLog(
					"legacy plaintext client but TLS required, reject (ENC-004)");
				goto return__;
			}
			/* 开关关闭：存量明文客户端，按明文继续 */
		} else if (neg == RPC_NEG_ERR_GENERIC ||
			   neg == RPC_NEG_ERR_VER) {
			/* 协商头损坏/版本不符：无论开关状态都拒绝——
			 * 非存量明文（存量客户端不发送协商字节），
			 * 且协商失败后帧边界不可信。 */
			ErrorLog(
				"negotiation header corrupt/version mismatch (ENC-004) for connfd %d",
				client);
			goto return__;
		} else if (neg == RPC_TRANSPORT_REJECT) {
			ErrorLog("negotiation rejected (ENC-004) for connfd %d",
				 client);
			goto return__;
		} else if (upgrade == RPC_TRANSPORT_TLS_SM ||
			   upgrade == RPC_TRANSPORT_TLS_GENERIC) {
			SSL *ssl = tls_cert_server_handshake(client, NULL);
			if (!ssl) {
				ErrorLog("TLS handshake failed for connfd %d",
					 client);
				goto return__;
			}
			if (rpc_ssl_bind(client, ssl) != 0) {
				ErrorLog("ssl bind failed for connfd %d", client);
				SSL_free(ssl);
				goto return__;
			}
		}
	}

	while (true) {
		ret = read_is_ready(client, g_rpc_config->read_timeout);
		if (ret <= 0) {
			ErrorLog("recv request time out or error.");
			goto return__;
		}
		bytes = rpc_recv(client, net_buf, MSG_BUFF_LEN - 1, 0);
		if (bytes == (int)IO_EOF) {
			goto return__;
		}
		if (bytes < 0) {
			ErrorLog(
				"recv request failure for bad network. bytes: %d",
				bytes);
			goto return__;
		}
		net_buf[bytes] = 0x00;
		msg_base_ntoh((msg_base_t *)msg_base_host,
			      (msg_base_t *)msg_base_net);

		InfoLog("process request start, type [%x], addr: [%s:%d].",
			msg_base_host->uiMT, inet_ntoa(serv.sin_addr),
			ntohs(serv.sin_port));

		if (msg_base_host->uiMT == MT_EXECUTE_SCP_DOWNLOAD) {
			if (rpc_scp_download(woker_info) != 0) {
				ErrorLog("scp file failure.");
				goto return__;
			}
		} else if (msg_base_host->uiMT == MT_EXECUTE_SCP_DOWNLOAD_LINK) {
			if (rpc_scp_download_link(woker_info) != 0) {
				ErrorLog("scp download link failure.");
				goto return__;
			}
		} else if (msg_base_host->uiMT == MT_EXECUTE_DIR_TREE) {
			if (rpc_dir_tree(woker_info) != 0) {
				ErrorLog("dir tree file failure.");
				goto return__;
			}
		} else if (msg_base_host->uiMT ==
			   MT_EXECUTE_BATCH_LIST_DIR_TREE) {
			if (rpc_list_batch_dir_tree(woker_info) != 0) {
				ErrorLog("dir tree file failure.");
				goto return__;
			}
		} else if (msg_base_host->uiMT == MT_EXECUTE_IS_DIR) {
			if (OnMsgIsDir(woker_info) != 0) {
				ErrorLog("test is dir failure.");
				goto return__;
			}

		} else if (msg_base_host->uiMT == MT_EXECUTE_SCP_UPLOAD) {
			if (OnMsgScpUpload(woker_info) != 0) {
				ErrorLog("upload file failure.");
				goto return__;
			}
		} else if (msg_base_host->uiMT == MT_EXECUTE_DOWNLOAD_BLOCK) {
			if (OnMsgDownloadBlock(woker_info) != 0) {
				ErrorLog("download block failure.");
				goto return__;
			}
		} else if (msg_base_host->uiMT == MT_EXECUTE_UPLOAD_BLOCK) {
			if (OnMsgUploadBlock(woker_info) != 0) {
				ErrorLog("download block failure.");
				goto return__;
			}
		} else if (msg_base_host->uiMT == MT_EXECUTE_FILE_STAT) {
			if (OnMsgFileStat(woker_info) != 0) {
				ErrorLog("file stat failure.");
				goto return__;
			}
		} else if (msg_base_host->uiMT == MT_EXECUTE_FILE_EXISTED) {
			if (OnMsgFileExisted(woker_info) != 0) {
				ErrorLog("file existed failure.");
				goto return__;
			}
		} else if (msg_base_host->uiMT == MT_EXECUTE_IOCTL_FSBACKUP) {
			if (OnIOCTLFsbackupDev(woker_info) != 0) {
				ErrorLog("ioctl fsbackup dev failure.");
				goto return__;
			}
		} else if (msg_base_host->uiMT == MT_EXECUTE_NC_EXTEND) {
			nc_extend(woker_info);
			goto return__;
		} else if (msg_base_host->uiMT == MT_EXECUTE_SHELL_SCRIPT) {
			execute_cmd(woker_info);
			goto return__;
		} else if (msg_base_host->uiMT == MT_EXECUTE_MKDIR) {
			if (remote_mkdir(woker_info) != 0) {
				ErrorLog("mkdir failure.");
				goto return__;
			}
		} else if (msg_base_host->uiMT == MT_EXECUTE_UNLINK) {
			if (remote_unlink(woker_info) != 0) {
				ErrorLog("unline failure.");
				goto return__;
			}
		} else if (msg_base_host->uiMT == MT_EXECUTE_NEW_DIR_TREE) {
			if (on_dir_tree(client, net_buf, host_buf, resp_net_buf,
					resp_host_buf,
					MSG_BUFF_LEN - 1024) != 0) {
				ErrorLog("on dir tree failure.");
				goto return__;
			}

		} else if (msg_base_host->uiMT == MT_EXECUTE_NEW_CONN) {
			WarningLog("new_conn=%d.",
				   new_conn(client, net_buf, host_buf,
					    resp_net_buf, resp_host_buf,
					    MSG_BUFF_LEN - 1024));
			goto exit__;

		} else if (msg_base_host->uiMT == MT_KEY_VERIFY) {
			msg_key_verify_t *msg_req =
				(msg_key_verify_t *)host_buf;
			msg_key_verify_resp_t *msg_resp =
				(msg_key_verify_resp_t *)resp_host_buf;

			msg_key_verify_ntoh(msg_req,
					    (msg_key_verify_t *)net_buf);

			char key_buf[256] = { 0 };
			if (msg_req->key_len > 0 &&
			    msg_req->key_len < sizeof(key_buf)) {
				memcpy(key_buf, msg_req->key, msg_req->key_len);
				data_dencrypt((unsigned char *)key_buf,
					      msg_req->key_len);
			}

			char *user = woker_info->user;
			int ret = timed_key_verify(key_buf, user);
			if (sec_audit_enabled()) {
				char client_info[128] = { 0 };
				char ip_str[INET_ADDRSTRLEN] = { 0 };
				inet_ntop(AF_INET, &serv.sin_addr, ip_str,
					  sizeof(ip_str));
				snprintf(client_info, sizeof(client_info),
					 "%s:%d",
					 ip_str[0] ? ip_str : "unknown",
					 ntohs(serv.sin_port));
				if (ret != TIMED_KEY_OK) {
					AuditErrorLog(
						"user=%s client=%s action=\"key_verify\" result=failed",
						user, client_info);
				} else {
					if (strcmp(user, RDBUSER) != 0) {
						AuditLog(
							"user=%s client=%s action=\"key_verify\" result=success",
							user, client_info);
					}
				}
			}
			if (ret != TIMED_KEY_OK) {
				ErrorLog("key verification failed for key: %s",
					 msg_req->key);
				msg_resp->err = 1;
			} else {
				InfoLog("key verification ok for user: %s",
					user);
				msg_resp->err = 0;
			}

			msg_key_verify_resp_hton(
				msg_resp,
				(msg_key_verify_resp_t *)resp_net_buf);
			rpc_send(client, resp_net_buf,
				 sizeof(msg_key_verify_resp_t), 0);

			if (ret != TIMED_KEY_OK) {
				goto return__;
			}

		} else if (msg_base_host->uiMT == MT_GET_TIME) {
			msg_get_time_resp_t *msg_resp =
				(msg_get_time_resp_t *)resp_host_buf;

			msg_get_time_ntoh((msg_get_time_t *)host_buf,
					  (msg_get_time_t *)net_buf);

			uint64_t now = time(NULL);
			msg_resp->timestamp = now;

			msg_get_time_resp_hton(
				msg_resp, (msg_get_time_resp_t *)resp_net_buf);
			rpc_send(client, resp_net_buf,
				 sizeof(msg_get_time_resp_t), 0);

			InfoLog("get time, timestamp: %lu", now);

		} else {
			ErrorLog("bad message: 0x%x.", msg_base_host->uiMT);
			goto return__;
		}

		InfoLog("process request end, type [%x], addr: [%s:%d].",
			msg_base_host->uiMT, inet_ntoa(serv.sin_addr),
			ntohs(serv.sin_port));
	}
return__:
	shutdown(client, SHUT_RDWR);
	close(client);

exit__:
	InfoLog("close client connection, type [%x], addr: [%s:%d].",
		msg_base_host->uiMT, inet_ntoa(serv.sin_addr),
		ntohs(serv.sin_port));

	delete woker_info;
	return 0;
}

int remote_mkdir(rpc_service_woker_info *conn)
{
	int connfd = conn->connfd;
	char *net_buf = conn->net_buf;
	char *host_buf = conn->host_buf;
	char *resp_net_buf = conn->resp_net_buf;
	char *resp_host_buf = conn->resp_host_buf;

	int ret = 0;
	msg_mkdir_t *mkdir_host = (msg_mkdir_t *)host_buf;
	msg_mkdir_t *mkdir_net = (msg_mkdir_t *)net_buf;

	msg_mkdir_resp_t *mkdir_resp_host = (msg_mkdir_resp_t *)resp_host_buf;
	msg_mkdir_resp_t *mkdir_resp_net = (msg_mkdir_resp_t *)resp_net_buf;

	msg_mkdir_ntoh(mkdir_host, mkdir_net);
	mkdir_host->path[mkdir_host->path_len] = 0x00;

	InfoLog("mkdir:[path:%s]", mkdir_host->path);

	ret = rpc_mkdir_path(mkdir_host->path);
	mkdir_resp_host->uiResult = ret;

	msg_mkdir_resp_hton(mkdir_resp_host, mkdir_resp_net);
	if (rpc_send(connfd, mkdir_resp_net, mkdir_resp_host->uiLEN, 0) !=
	    (int)mkdir_resp_host->uiLEN) {
		ret = -1;
	}
	return ret;
}

int remote_unlink(rpc_service_woker_info *conn)
{
	int connfd = conn->connfd;
	char *net_buf = conn->net_buf;
	char *host_buf = conn->host_buf;
	char *resp_net_buf = conn->resp_net_buf;
	char *resp_host_buf = conn->resp_host_buf;

	int ret = 0;
	msg_unlink_t *unlink_host = (msg_unlink_t *)host_buf;
	msg_unlink_t *unlink_net = (msg_unlink_t *)net_buf;

	msg_unlink_resp_t *unlink_resp_host =
		(msg_unlink_resp_t *)resp_host_buf;
	msg_unlink_resp_t *unlink_resp_net = (msg_unlink_resp_t *)resp_net_buf;

	msg_unlink_ntoh(unlink_host, unlink_net);
	unlink_host->path[unlink_host->path_len] = 0x00;

	InfoLog("unlink:[path:%s]", unlink_host->path);

	ret = unlink(unlink_host->path);
	unlink_resp_host->uiResult = ret;

	msg_unlink_resp_hton(unlink_resp_host, unlink_resp_net);
	if (rpc_send(connfd, unlink_resp_net, unlink_resp_host->uiLEN, 0) !=
	    (int)unlink_resp_host->uiLEN) {
		ret = -1;
	}
	return ret;
}

// #define DEBUG_LOG() WarningLog("readdir ret:%d", ret);

static int new_conn(int connfd, char *net_buf, char *host_buf,
		    char *resp_net_buf, char *resp_host_buf, const int buflen)
{
	int ret = 0;
	msg_new_conn_t *new_conn_host = (msg_new_conn_t *)host_buf;
	msg_new_conn_t *new_conn_net = (msg_new_conn_t *)net_buf;

	msg_new_conn_resp_t *new_conn_resp_host =
		(msg_new_conn_resp_t *)resp_host_buf;
	msg_new_conn_resp_t *new_conn_resp_net =
		(msg_new_conn_resp_t *)resp_net_buf;

	rpc_conn_t *conn = NULL;
	struct buf *msgr;
	// struct buf *msgw;
	uint8_t type = 0;

	msg_new_conn_ntoh(new_conn_host, new_conn_net);

	InfoLog("new_conn:[flags:%d]", new_conn_host->flags);

	conn = new_rpc_conn(connfd);
	if (conn == NULL) {
		ErrorLog("new_conn failure");
		close(connfd);
		return -1;
	}

	new_conn_resp_host->uiResult = ret;
	new_conn_resp_host->err = errno;

	msg_new_conn_resp_hton(new_conn_resp_host, new_conn_resp_net);
	if (rpc_send(connfd, new_conn_resp_net, new_conn_resp_host->uiLEN, 0) !=
	    (int)new_conn_resp_host->uiLEN) {
		ErrorLog("network failure");
		ret = -1;
		goto fail;
	}

	msgr = conn->msgr;
	conn->flags = new_conn_host->flags;
	// msgw = conn->msgw;

	while (ret == 0 && rpc_conn_recv_msg(conn) == 0) {
		if ((ret = buf_get_u8(msgr, &type)) != 0) {
			ErrorLog("recv type failure");
			goto fail;
		}
		switch (type) {
		case NEW_CONN_TMP_READDIR:
			ret = rpc_conn_srv_readdir(conn);
			if (g_rpc_config->debug) {
				WarningLog("readdir ret:%d", ret);
			}
			break;
		case NEW_CONN_TMP_READDIR_TREE:
			ret = rpc_conn_srv_readdir_tree(conn);
			if (g_rpc_config->debug) {
				WarningLog("readdir_tree ret:%d", ret);
			}
			break;
		case NEW_CONN_TMP_LSTAT:
			ret = rpc_conn_srv_lstat(conn);
			if (g_rpc_config->debug) {
				WarningLog("lstat ret:%d", ret);
			}
			break;
		case NEW_CONN_TMP_PREAD:
			ret = rpc_conn_srv_pread(conn);
			if (g_rpc_config->debug) {
				WarningLog("pread ret:%d", ret);
			}
			break;
		case NEW_CONN_TMP_PWRITE:
			ret = rpc_conn_srv_pwrite(conn);
			if (g_rpc_config->debug) {
				WarningLog("pwrite ret:%d", ret);
			}
			break;
		case NEW_CONN_TMP_MKDIR:
			ret = rpc_conn_srv_mkdir(conn);
			if (g_rpc_config->debug) {
				WarningLog("mkdir ret:%d", ret);
			}
			break;
		case NEW_CONN_TMP_FCHOWNATS:
			ret = rpc_conn_srv_fchownats(conn);
			if (g_rpc_config->debug) {
				WarningLog("fchownats ret:%d", ret);
			}
			break;
		case NEW_CONN_TMP_FCHMODATS:
			ret = rpc_conn_srv_fchmodats(conn);
			if (g_rpc_config->debug) {
				WarningLog("fchmodats ret:%d", ret);
			}
			break;
		case NEW_CONN_TMP_DOWNLOAD_FILEATS:
			ret = rpc_conn_srv_download_fileats(conn);
			if (g_rpc_config->debug) {
				WarningLog("download fileats ret:%d", ret);
			}
			break;
		case NEW_CONN_TMP_UPLOAD_FILEATS:
			ret = rpc_conn_srv_upload_fileats(conn);
			if (g_rpc_config->debug) {
				WarningLog("upload fileats ret:%d", ret);
			}
			break;
		case NEW_CONN_TMP_READLINK:
			ret = rpc_conn_srv_readlink(conn);
			if (g_rpc_config->debug) {
				WarningLog("readlink ret:%d", ret);
			}
			break;
		case NEW_CONN_TMP_SYMLINK:
			ret = rpc_conn_srv_symlink(conn);
			if (g_rpc_config->debug) {
				WarningLog("symlink ret:%d", ret);
			}
			break;
		case NEW_CONN_TMP_ACCESS:
			ret = rpc_conn_srv_access(conn);
			if (g_rpc_config->debug) {
				WarningLog("symlink ret:%d", ret);
			}
			break;
		case NEW_CONN_TMP_MKDIRALL:
			ret = rpc_conn_srv_mkdirall(conn);
			if (g_rpc_config->debug) {
				WarningLog("symlink ret:%d", ret);
			}
			break;
		case NEW_CONN_TMP_CHMOD:
			ret = rpc_conn_srv_chmod(conn);
			if (g_rpc_config->debug) {
				WarningLog("chmod ret:%d", ret);
			}
			break;
		case NEW_CONN_TMP_CHOWN:
			ret = rpc_conn_srv_chown(conn);
			if (g_rpc_config->debug) {
				WarningLog("chown ret:%d", ret);
			}
			break;
		case NEW_CONN_TMP_OPENAT:
			ret = rpc_conn_srv_openat(conn);
			if (g_rpc_config->debug) {
				WarningLog("openat ret:%d", ret);
			}
			break;
		case NEW_CONN_TMP_DOWNLOAD_FILEAT:
			ret = rpc_conn_srv_download_fileat(conn);
			if (g_rpc_config->debug) {
				WarningLog("download fileat ret:%d", ret);
			}
			break;
		case NEW_CONN_TMP_READLINKAT:
			ret = rpc_conn_srv_readlinkat(conn);
			if (g_rpc_config->debug) {
				WarningLog("readlinkat ret:%d", ret);
			}
			break;
		default:
			ret = -1;
			ErrorLog("bad message type: %d", type);
			break;
		}
	}

fail:
	if (conn != NULL) {
		rpc_conn_free(conn);
	}
	return ret;
}

static FILE *my_popen(const char *command, const char *type, pid_t *chpid);
static int my_pclose(FILE *fp, pid_t pid);

void execute_cmd(rpc_service_woker_info *conn)
{
	int connfd = conn->connfd;
	char *net_buf = conn->net_buf;
	char *host_buf = conn->host_buf;
	char *resp_net_buf = conn->resp_net_buf;
	char *resp_host_buf = conn->resp_host_buf;
	const int buf_len = conn->buf_len;

	int ret = 0;
	int cmd_len = 0;
	pid_t chpid = -1;
	int64_t nbytes = 0;
	FILE *fptr_pipe = NULL;
	unsigned int shell_opt = 0;
	msg_cmd_t *cmd_host = (msg_cmd_t *)host_buf;
	msg_cmd_t *cmd_net = (msg_cmd_t *)net_buf;
	int outfd = 0;

	msg_cmd_resp_t *cmd_resp_host = (msg_cmd_resp_t *)resp_host_buf;
	msg_cmd_resp_t *cmd_resp_net = (msg_cmd_resp_t *)resp_net_buf;
	char *command = cmd_host->command;
	char *buff = cmd_resp_host->buff;

	msg_cmd_ntoh(cmd_host, cmd_net);

	cmd_len = MIN(cmd_host->cmd_len, MSG_BUFF_LEN - 1);
	command[cmd_len] = 0x00;
	shell_opt = cmd_host->opt;
	InfoLog("execute:[cmd_len:%d, command:%s]", cmd_host->cmd_len, command);

	fptr_pipe = my_popen(command, "r", &chpid);
	if (fptr_pipe == NULL) {
		ret = errno;
		buff[0] = 0x00;
		nbytes = sprintf(buff, "execute [%s]: %s(errno: %d)\n", command,
				 strerror(errno), errno);
		ErrorLog("execute [%s]: %s(errno: %d)", command,
			 strerror(errno), errno);
		buff[nbytes] = 0x00;
		goto fail;
	}

	InfoLog("generate subprocess: %d", chpid);

	outfd = fileno(fptr_pipe);
	while (true) {
		struct pollfd fds[2];
		fds[0].fd = connfd;
		fds[0].events = POLLIN | POLLRDHUP | POLLHUP;
		fds[1].fd = outfd;
		fds[1].events = POLLIN | POLLRDHUP | POLLHUP;

		int ret = poll(fds, 2, g_rpc_config->read_timeout);
		if (ret < 0) {
			ErrorLog("poll error. kill signal");
			kill(chpid, 9);
			break;
		}
		if (ret == 0) {
			// 超时，无数据，可继续循环或做其他工作
			buff[0] = 0x00;
			cmd_resp_host->msg_len = 0;
			cmd_resp_host->uiResult = 0;
			cmd_resp_host->opt_resp = shell_opt;
			cmd_resp_host->stat = SHELL_COMMAND_CONTINUE;
			msg_cmd_resp_hton(cmd_resp_host, cmd_resp_net);
			if (rpc_send(connfd, cmd_resp_net, cmd_resp_host->uiLEN,
				     0) != (int)cmd_resp_host->uiLEN) {
				ErrorLog("network failure");
				ret = -1;
				kill(chpid, 9);
				break;
			}
			continue;
		}

		// 先处理 connfd（如果需要优先）
		if (fds[0].revents & (POLLIN | POLLRDHUP | POLLHUP)) {
			// 读 connfd 并处理
			// 如果读到关闭信号，则 break
			ErrorLog("connection error. kill signal");
			kill(chpid, 9);
			break;
		}
		// 再处理 outfd
		if (fds[1].revents & (POLLIN | POLLRDHUP | POLLHUP)) {
			// 读 outfd
			nbytes = read(outfd, buff, (buf_len - 1));
			if (nbytes == 0) {
				break;
			}
			if (nbytes < 1) {
				WarningLog(
					"outfd: %d read failure nbytes %d [errno:%d, %s]",
					outfd, nbytes, errno, strerror(errno));
				break;
			}
			buff[nbytes] = 0x00;
			cmd_resp_host->msg_len = nbytes;
			cmd_resp_host->uiResult = 0;
			cmd_resp_host->opt_resp = shell_opt;
			cmd_resp_host->stat = SHELL_COMMAND_CONTINUE;
			msg_cmd_resp_hton(cmd_resp_host, cmd_resp_net);
			WarningLog("%s", buff);
			if (rpc_send(connfd, cmd_resp_net, cmd_resp_host->uiLEN,
				     0) != (int)cmd_resp_host->uiLEN) {
				ErrorLog("network failure");
				ret = -1;
				kill(chpid, 9);
				break;
			}
		}
	}

	ret = my_pclose(fptr_pipe, chpid);
	fptr_pipe = NULL;
	nbytes = 0;
	buff[0] = 0x00;

	if (WIFEXITED(ret)) {
		ret = WEXITSTATUS(ret);

		buff[0] = 0;
		nbytes = 0;
		InfoLog("[%s] completed, return value:%d", command, ret);
	} else if (WIFSIGNALED(ret)) {
		ret = WTERMSIG(ret);
		nbytes = sprintf(buff, "killed %d\n", ret);
		ErrorLog("[%s] killed, return value:%d", command, ret);
	} else if (WIFSTOPPED(ret)) {
		ret = WSTOPSIG(ret);
		nbytes = sprintf(buff, "signal %d\n", ret);
		ErrorLog("[%s] signal abort, signal No.:%d", command, ret);
	} else {
		ret = WEXITSTATUS(ret);
		ErrorLog("[%s] unknown reason return value:%d", command, ret);
	}
	buff[nbytes] = 0x00;

	if (sec_audit_enabled()) {
		char client_info[128] = { 0 };
		struct sockaddr_in *addr = (struct sockaddr_in *)&conn->serv;
		char ip_str[INET_ADDRSTRLEN] = { 0 };
		inet_ntop(AF_INET, &addr->sin_addr, ip_str, sizeof(ip_str));
		snprintf(client_info, sizeof(client_info), "%s:%d",
			 ip_str[0] ? ip_str : "unknown", ntohs(addr->sin_port));

		if (strcmp(conn->user, RDBUSER) != 0) {
			AuditLog("user=%s client=%s cmd=\"%s\" result=%d",
				 conn->user[0] ? conn->user : "unknown",
				 client_info, command, ret);
		}
	}

fail:
	cmd_resp_host->msg_len = strlen(cmd_resp_host->buff);
	cmd_resp_host->opt_resp = shell_opt;
	cmd_resp_host->stat = SHELL_COMMAND_COMPLETED;
	cmd_resp_host->uiResult = ret;
	msg_cmd_resp_hton(cmd_resp_host, cmd_resp_net);
	if (rpc_send(connfd, cmd_resp_net, cmd_resp_host->uiLEN, 0) !=
	    (int)cmd_resp_host->uiLEN) {
		ErrorLog("send response failure for bad network.");
	}
}

#define SHELL "/bin/sh"
static FILE *my_popen(const char *command, const char *type, pid_t *chpid)
{
	FILE *fp = NULL;
	pid_t pid = -1;
	int pfd[2] = { -1, -1 };

	*chpid = -1;

	if ((type[0] != 'r' && type[0] != 'w') || type[1] != 0x00) {
		errno = EINVAL;
		ErrorLog("cmd %s type error %s", command, type);
		return (NULL);
	}

	if (pipe2(pfd, O_CLOEXEC) < 0) {
		ErrorLog("cmd %s pipe2 %s(%d)", command, strerror(errno),
			 errno);
		return NULL;
	}
	InfoLog("cmd %s pipe[0]:%d, pipe[1]:%d", command, pfd[0], pfd[1]);

	if ((pid = fork()) < 0) {
		ErrorLog("cmd %s fork %s(%d)", command, strerror(errno), errno);
		goto failure__;
	} else if (pid == 0) {
		if (type[0] == 'r') {
			close(pfd[0]);
			dup2(pfd[1], STDOUT_FILENO);
			dup2(pfd[1], STDERR_FILENO);
			close(pfd[1]);
		} else {
			close(pfd[1]);
			if (pfd[0] != STDIN_FILENO) {
				dup2(pfd[0], STDIN_FILENO);
				close(pfd[0]);
			}
		}

		close_from(STDERR_FILENO + 1);

		int ret = execl(SHELL, "sh", "-c", command, (char *)0);
		printf("execl failed: %d %s (errno=%d)", ret, strerror(errno),
		       errno);
		_exit(127);
	}
	if (type[0] == 'r') {
		close(pfd[1]);
		pfd[1] = -1;

		if ((fp = fdopen(pfd[0], type)) == NULL) {
			ErrorLog("my popen execl %s(%d)", strerror(errno),
				 errno);
			goto failure__;
		}
	} else {
		close(pfd[0]);
		pfd[0] = -1;
		if ((fp = fdopen(pfd[1], type)) == NULL) {
			ErrorLog("my popen execl %s(%d)", strerror(errno),
				 errno);
			goto failure__;
		}
	}

	*chpid = pid;
	return (fp);
failure__:
	if (pid > 0) {
		kill(pid, 9);
		waitpid(pid, NULL, 0);
	}
	if (0 <= pfd[0]) {
		close(pfd[0]);
		pfd[0] = -1;
	}
	if (0 <= pfd[1]) {
		close(pfd[1]);
		pfd[1] = -1;
	}
	return NULL;
}

static int my_pclose(FILE *fp, pid_t pid)
{
	int ret = -1;
	int status = -1;
	int fd = fileno(fp);
	if (fclose(fp) == EOF) {
		int err = errno;
		ErrorLog("fclose fd:%d failed: %s (errno=%d)", fd,
			 strerror(err), err);
	}

	ret = waitpid(pid, &status, 0);
	if (ret < 0) {
		int err = errno;
		WarningLog("waitpid(%d) failed: %s (errno=%d)", pid,
			   strerror(err), err);
		return -1;
	}

	if (status < 0) {
		int err = errno;
		WarningLog("waitpid(%d) status: %d, %s(errno: %d)", pid, status,
			   strerror(err), err);
	}

	return status;
}

int rpc_scp_download(rpc_service_woker_info *conn)
{
	int connfd = conn->connfd;
	char *net_buf = conn->net_buf;
	char *host_buf = conn->host_buf;
	char *resp_net_buf = conn->resp_net_buf;
	char *resp_host_buf = conn->resp_host_buf;
	const int buf_len = conn->buf_len;

	int ret = -1;
	int fd = -1;
	int block_id = 0;
	int bytes = 0;
	int nread = 0;
	int64_t f_size = 0;
	char local_file[1024] = { 0 };
	const int block_size = buf_len - 8192;
	msg_scp_download_t *host = (msg_scp_download_t *)host_buf;
	msg_scp_download_t *net = (msg_scp_download_t *)net_buf;
	msg_scp_download_resp_t *resp_host =
		(msg_scp_download_resp_t *)resp_host_buf;
	msg_scp_download_resp_t *resp_net =
		(msg_scp_download_resp_t *)resp_net_buf;
	int64_t send_bytes = 0;

	memset(host_buf, 0x00, buf_len);
	memset(resp_host_buf, 0x00, buf_len);
	msg_scp_download_ntoh(host, net);
	struct stat sss;
	const unsigned int api_stat = host->api_stat;
	const unsigned int is_compress = host->is_compress;
	const unsigned int is_encrypt = host->is_encrypt;
	const unsigned int is_checksum = host->is_checksum;

	snprintf(local_file, sizeof(local_file), "%s", host->file_name);

	InfoLog("begin download file [%s]", local_file);

	resp_host->file_name_checksum = crc_32((unsigned char *)host->file_name,
					       strlen(host->file_name));

	if (resp_host->file_name_checksum != host->file_name_checksum) {
		resp_host->uiResult = -1U;
		msg_scp_download_resp_hton(resp_host, resp_net);
		if (rpc_send(connfd, resp_net, resp_host->uiLEN, 0) !=
		    (int)resp_host->uiLEN) {
			ErrorLog("send data failure %s(errno: %d)\n",
				 strerror(errno), errno);
		}
		goto return__;
	}

	fd = open(local_file, O_RDONLY);
	if (fd < 0) {
		if (errno == ENOENT) {
			WarningLog("local_file: [%s] not existed, errno:%d)",
				   local_file, errno);
			resp_host->mode = 0755;
			if (api_stat == 0) {
				resp_host->block_id = LAST_BLOCK;
			} else {
				resp_host->uiResult = -1U;
			}
			msg_scp_download_resp_hton(resp_host, resp_net);
			if (rpc_send(connfd, resp_net, resp_host->uiLEN, 0) !=
			    (int)resp_host->uiLEN) {
				ErrorLog("send data failure %s(errno: %d)\n",
					 strerror(errno), errno);
				goto return__;
			}
			if (api_stat == 0) {
				WarningLog("local_file: [%s] not existed.",
					   local_file);
				resp_host->uiResult = 0x00;
				goto completed__;
			} else {
				ErrorLog("local_file: [%s] not existed.",
					 local_file,
					 strerror(errno), errno);
				goto return__;
			}
		}
		resp_host->uiResult = -1;
		if (errno) {
			resp_host->uiResult = errno;
		}
		ErrorLog("open file: [%s] failure. %s(errno: %d)", local_file,
			 strerror(errno), errno);
		resp_host->data_len = sprintf(
			resp_host->data, "open file:[%s] failure.", local_file);
		msg_scp_download_resp_hton(resp_host, resp_net);
		if (rpc_send(connfd, resp_net, resp_host->uiLEN, 0) !=
		    (int)resp_host->uiLEN) {
		}
		goto error__;
	}

	if (fstat(fd, &sss)) {
		ErrorLog("fstat file: [%s] failure. %s(errno: %d)", local_file,
			 strerror(errno), errno);
		resp_host->uiResult = errno;
		msg_scp_download_resp_hton(resp_host, resp_net);
		if (rpc_send(connfd, resp_net, resp_host->uiLEN, 0) !=
		    (int)resp_host->uiLEN) {
		}
		goto error__;
	}

	f_size = sss.st_size;

	if (f_size == 0) {
		resp_host->uiResult = 0x00;
		resp_host->mode = sss.st_mode;
		resp_host->atim.tv_sec = sss.st_atim.tv_sec;
		resp_host->atim.tv_nsec = sss.st_atim.tv_nsec;
		resp_host->mtim.tv_sec = sss.st_mtim.tv_sec;
		resp_host->mtim.tv_nsec = sss.st_mtim.tv_nsec;
		resp_host->ctim.tv_sec = sss.st_ctim.tv_sec;
		resp_host->ctim.tv_nsec = sss.st_ctim.tv_nsec;
		resp_host->block_id = LAST_BLOCK;
		msg_scp_download_resp_hton(resp_host, resp_net);
		if (rpc_send(connfd, resp_net, resp_host->uiLEN, 0) !=
		    (int)resp_host->uiLEN) {
			ErrorLog("send data failure %s(errno: %d)\n",
				 strerror(errno), errno);
		}
		InfoLog("send file: %s, size 0\n", local_file);
		goto completed__;
	}

	resp_host->mode = sss.st_mode;
	int64_split_to_int32(f_size, &resp_host->total_size_high,
			     &resp_host->total_size_low);

	do {
		bytes = 0;
		while (bytes < block_size) {
			nread = read(fd, resp_host->data + bytes,
				     block_size - bytes);
			if (nread < 1) {
				break;
			}
			bytes += nread;
		}
		if (bytes < block_size) {
			resp_host->block_id = LAST_BLOCK;
		} else {
			resp_host->block_id = ++block_id;
		}
		int64_split_to_int32(f_size,
				     &resp_host->total_size_high,
				     &resp_host->total_size_low);

		resp_host->original_len = bytes;
		resp_host->data_len = resp_host->original_len;
		resp_host->uiResult = 0x00;
		resp_host->is_compress = is_compress;
		resp_host->is_encrypt = is_encrypt;
		resp_host->is_checksum = is_checksum;

		if (is_checksum) {
			resp_host->checksum = 0;
			for (unsigned int i = 0;
			     i < resp_host->data_len; ++i) {
				resp_host->checksum +=
					resp_host->data[i];
			}
		}

		if (is_compress) {
			resp_host->data_len = LZ4_compress_default(
				resp_host->data, resp_net->data, bytes,
				buf_len - 1024);
			if ((int)resp_host->data_len < 1) {
				ErrorLog(
					"compress data for %s failure data_len: %u, "
					"original_len: %u\n",
					local_file, resp_host->data_len,
					resp_host->original_len);
				goto return__;
			}
			memcpy(resp_host->data, resp_net->data,
			       resp_host->data_len);
		}

		if (is_encrypt) {
			data_encrypt((unsigned char *)resp_host->data,
				     resp_host->data_len);
		}

		resp_host->mode = sss.st_mode;
		resp_host->atim.tv_sec = sss.st_atim.tv_sec;
		resp_host->atim.tv_nsec = sss.st_atim.tv_nsec;
		resp_host->mtim.tv_sec = sss.st_mtim.tv_sec;
		resp_host->mtim.tv_nsec = sss.st_mtim.tv_nsec;
		resp_host->ctim.tv_sec = sss.st_ctim.tv_sec;
		resp_host->ctim.tv_nsec = sss.st_ctim.tv_nsec;

		msg_scp_download_resp_hton(resp_host, resp_net);

		if (rpc_send(connfd, resp_net, resp_host->uiLEN, 0) !=
		    (int)resp_host->uiLEN) {
			ErrorLog("send data failure %s(errno: %d)\n",
				 strerror(errno), errno);
			goto return__;
		}

		send_bytes += resp_host->original_len;
		if (resp_host->block_id == LAST_BLOCK) {
			break;
		}
	} while (0 < bytes);

	if (send_bytes != f_size) {
		ErrorLog(
			"send file: %s failure. send_bytes:%ld != f_size:%ld\n",
			local_file, send_bytes, f_size);
	}

completed__:
	InfoLog("download file [%s] complete success, send_bytes: %ld, f_size: %ld",
		local_file, send_bytes, f_size);
	ret = 0;
return__:
	close(fd);
error__:
	return ret;
}

int rpc_scp_download_link(rpc_service_woker_info *conn)
{
	int connfd = conn->connfd;
	char *net_buf = conn->net_buf;
	char *host_buf = conn->host_buf;
	char *resp_net_buf = conn->resp_net_buf;
	char *resp_host_buf = conn->resp_host_buf;
	const int buf_len = conn->buf_len;

	int ret = -1;
	char link_target[PATH_MAX];
	char *remote_path = NULL;
	msg_scp_download_link_t *host = (msg_scp_download_link_t *)host_buf;
	msg_scp_download_link_t *net = (msg_scp_download_link_t *)net_buf;
	msg_scp_download_link_resp_t *resp_host =
		(msg_scp_download_link_resp_t *)resp_host_buf;
	msg_scp_download_link_resp_t *resp_net =
		(msg_scp_download_link_resp_t *)resp_net_buf;

	memset(host_buf, 0x00, buf_len);
	memset(resp_host_buf, 0x00, buf_len);
	msg_scp_download_link_ntoh(host, net);

	host->file_name[host->name_len] = '\0';
	remote_path = host->file_name;

	ssize_t link_len = readlink(remote_path, link_target,
				    sizeof(link_target) - 1);
	if (link_len < 0) {
		ErrorLog("readlink %s failure. %s(errno: %d)", remote_path,
			 strerror(errno), errno);
		resp_host->uiResult = errno;
		msg_scp_download_link_resp_hton(resp_host, resp_net);
		if (rpc_send(connfd, resp_net, resp_host->uiLEN, 0) !=
		    (int)resp_host->uiLEN) {
			ErrorLog("send response failure %s(errno: %d)",
				 strerror(errno), errno);
		}
		goto return__;
	}
	link_target[link_len] = '\0';

	resp_host->uiResult = 0;
	resp_host->data_len = link_len;
	// copy link target into data
	memcpy(resp_host->data, link_target, link_len);

	msg_scp_download_link_resp_hton(resp_host, resp_net);
	if (rpc_send(connfd, resp_net, resp_host->uiLEN, 0) !=
	    (int)resp_host->uiLEN) {
		ErrorLog("send response failure %s(errno: %d)",
			 strerror(errno), errno);
		goto return__;
	}

	ret = 0;
return__:
	return ret;
}

int rpc_dir_tree(rpc_service_woker_info *conn)
{
	int connfd = conn->connfd;
	char *net_buf = conn->net_buf;
	char *host_buf = conn->host_buf;
	char *resp_net_buf = conn->resp_net_buf;
	char *resp_host_buf = conn->resp_host_buf;
	const int buf_len = conn->buf_len;

	int ret = -1;
	set<string> files;
	set<link_item_t> links;
	int max_buflen = buf_len - 2048;
	msg_dir_tree_t *host = (msg_dir_tree_t *)host_buf;
	msg_dir_tree_t *net = (msg_dir_tree_t *)net_buf;
	msg_dir_tree_resp_t *resp_host = (msg_dir_tree_resp_t *)resp_host_buf;
	msg_dir_tree_resp_t *resp_net = (msg_dir_tree_resp_t *)resp_net_buf;

	msg_dir_tree_ntoh(host, net);
	const int dir_only = host->dir_only;
	if (dir_only == 1) {
		ret = dir_traversal_only(host->dir_name, &files, 1);
		if (ret != 0) {
			ErrorLog("dir tree:[%s] failure. ret: %d",
				 host->dir_name, ret);
			goto return__;
		}
	} else {
		ret = dir_traversal_2(host->dir_name, &files, &links, 1);
		if (ret != 0) {
			ErrorLog("dir tree:[%s] failure. ret: %d",
				 host->dir_name, ret);
			goto return__;
		}
	}

	resp_host->data_len = 0;
	resp_host->item_num = 0;
	resp_host->stat = 0;

	for (set<string>::iterator iter = files.begin(); iter != files.end();
	     ++iter) {
		if (max_buflen <
		    (int)(resp_host->data_len + iter->size() + 4)) {
			resp_host->data[resp_host->data_len] = 0x00;
			++resp_host->data_len;

			msg_dir_tree_resp_hton(resp_host, resp_net);
			if (rpc_send(connfd, resp_net, resp_host->uiLEN, 0) !=
			    (int)resp_host->uiLEN) {
				ret = -1;
				ErrorLog("send data failure %s(errno: %d)\n",
					 strerror(errno), errno);
				goto return__;
			}

			resp_host->data_len = 0;
			resp_host->item_num = 0;
		}

		memcpy(resp_host->data + resp_host->data_len, iter->c_str(),
		       iter->size());
		resp_host->data_len += iter->size();
		++resp_host->item_num;
		resp_host->data[resp_host->data_len] = ';';
		++resp_host->data_len;
	}

	resp_host->stat = 1;
	resp_host->data[resp_host->data_len] = 0x00;
	++resp_host->data_len;
	msg_dir_tree_resp_hton(resp_host, resp_net);
	if (rpc_send(connfd, resp_net, resp_host->uiLEN, 0) !=
	    (int)resp_host->uiLEN) {
		ret = -1;
		ErrorLog("send data failure %s(errno: %d)\n", strerror(errno),
			 errno);
		goto return__;
	}

	resp_host->data_len = 0;
	resp_host->item_num = 0;
	resp_host->stat = 1;

	for (set<link_item_t>::iterator iter = links.begin();
	     iter != links.end(); ++iter) {
		if (max_buflen <
		    (int)(resp_host->data_len + sizeof(link_item_t) + 4)) {
			resp_host->data[resp_host->data_len] = 0x00;
			++resp_host->data_len;

			msg_dir_tree_resp_hton(resp_host, resp_net);
			if (rpc_send(connfd, resp_net, resp_host->uiLEN, 0) !=
			    (int)resp_host->uiLEN) {
				ret = -1;
				ErrorLog("send data failure %s(errno: %d)\n",
					 strerror(errno), errno);
				goto return__;
			}

			resp_host->data_len = 0;
			resp_host->item_num = 0;
		}

		memcpy(resp_host->data + resp_host->data_len, &(*iter),
		       sizeof(link_item_t));
		resp_host->data_len += sizeof(link_item_t);
		++resp_host->item_num;
	}
	resp_host->data[resp_host->data_len] = 0x00;
	++resp_host->data_len;

	resp_host->stat = 2;
	msg_dir_tree_resp_hton(resp_host, resp_net);
	if (rpc_send(connfd, resp_net, resp_host->uiLEN, 0) !=
	    (int)resp_host->uiLEN) {
		ret = -1;
		ErrorLog("send data failure %s(errno: %d)\n", strerror(errno),
			 errno);
		goto return__;
	}
	ret = 0;
return__:
	return ret;
}

int rpc_list_batch_dir_tree(rpc_service_woker_info *conn)
{
	int connfd = conn->connfd;
	char *net_buf = conn->net_buf;
	char *host_buf = conn->host_buf;
	char *resp_net_buf = conn->resp_net_buf;
	char *resp_host_buf = conn->resp_host_buf;
	const int buf_len = conn->buf_len;

	int ret = -1;
	set<string> files;
	const int max_buflen = buf_len - 2048;
	msg_batch_list_dir_tree_t *host = (msg_batch_list_dir_tree_t *)host_buf;
	msg_batch_list_dir_tree_t *net = (msg_batch_list_dir_tree_t *)net_buf;
	msg_batch_list_dir_tree_resp_t *resp_host =
		(msg_batch_list_dir_tree_resp_t *)resp_host_buf;
	msg_batch_list_dir_tree_resp_t *resp_net =
		(msg_batch_list_dir_tree_resp_t *)resp_net_buf;

	memset(host_buf, 0x00, buf_len);
	memset(resp_host_buf, 0x00, buf_len);
	msg_batch_list_dir_tree_ntoh(host, net);
	const int dir_only = host->dir_only;
	if (dir_only == 1) {
		if (dir_traversal_only(host->dir_name, &files, 1) != 0) {
			ErrorLog("dir tree:[%s] failure.", host->dir_name);
			goto return__;
		}
	} else {
		if (dir_traversal_3(host->dir_name, &files, 1) != 0) {
			ErrorLog("dir tree:[%s] failure.", host->dir_name);
			goto return__;
		}
	}

	for (set<string>::iterator iter = files.begin(); iter != files.end();
	     ++iter) {
		if (max_buflen <
		    (int)(resp_host->data_len + iter->size() + 4)) {
			resp_host->data[resp_host->data_len] = 0x00;
			++resp_host->data_len;
			resp_host->list_completed = 0;

			msg_batch_list_dir_tree_resp_hton(resp_host, resp_net);
			if (rpc_send(connfd, resp_net, resp_host->uiLEN, 0) !=
			    (int)resp_host->uiLEN) {
				ret = -1;
				ErrorLog("send data failure %s(errno: %d)\n",
					 strerror(errno), errno);
				goto return__;
			}

			memset(resp_host, 0x00, buf_len);
		}

		memcpy(resp_host->data + resp_host->data_len, iter->c_str(),
		       iter->size());
		resp_host->data_len += iter->size();
		++resp_host->item_num;
		{
			resp_host->data[resp_host->data_len] = ';';
			++resp_host->data_len;
		}
	}

	resp_host->data[resp_host->data_len] = 0x00;
	++resp_host->data_len;
	resp_host->list_completed = 1;

	msg_batch_list_dir_tree_resp_hton(resp_host, resp_net);
	if (rpc_send(connfd, resp_net, resp_host->uiLEN, 0) !=
	    (int)resp_host->uiLEN) {
		ret = -1;
		ErrorLog("send data failure %s(errno: %d)\n", strerror(errno),
			 errno);
		goto return__;
	}
	ret = 0;
return__:
	return ret;
}

int OnMsgIsDir(rpc_service_woker_info *conn)
{
	int connfd = conn->connfd;
	char *net_buf = conn->net_buf;
	char *host_buf = conn->host_buf;
	char *resp_net_buf = conn->resp_net_buf;
	char *resp_host_buf = conn->resp_host_buf;
	const int buf_len = conn->buf_len;

	msg_is_dir_t *host = (msg_is_dir_t *)host_buf;
	msg_is_dir_t *net = (msg_is_dir_t *)net_buf;
	msg_is_dir_resp_t *resp_host = (msg_is_dir_resp_t *)resp_host_buf;
	msg_is_dir_resp_t *resp_net = (msg_is_dir_resp_t *)resp_net_buf;

	memset(host_buf, 0x00, buf_len);
	memset(resp_host_buf, 0x00, buf_len);
	msg_is_dir_ntoh(host, net);

	resp_host->is_dir = TestIsDir(host->dir_name);

	msg_is_dir_resp_hton(resp_host, resp_net);
	if (rpc_send(connfd, resp_net, resp_host->uiLEN, 0) !=
	    (int)resp_host->uiLEN) {
		ErrorLog("rpc send %s is dir failure: %s(errno: %d)",
			 host->dir_name, strerror(errno), errno);
		return -1;
	}

	return 0;
}

int OnMsgScpUpload(rpc_service_woker_info *conn)
{
	int connfd = conn->connfd;
	char *net_buf = conn->net_buf;
	char *host_buf = conn->host_buf;
	char *resp_net_buf = conn->resp_net_buf;
	char *resp_host_buf = conn->resp_host_buf;
	const int buf_len = conn->buf_len;

	int ret = -1;
	int fd = -1;
	char *pos = NULL;
	////unsigned int block_count = 0;
	mode_t mode = 0777;
	unsigned int gid = 0;
	unsigned int uid = 0;
	rpc_timespec_t atim = { 0 }; /* Time of last access.  */
	rpc_timespec_t mtim = { 0 }; /* Time of last modification.  */
	rpc_timespec_t ctim = { 0 }; /* Time of last status change.  */
	int bytes = 0;
	int64_t recv_bytes = 0;
	int64_t f_size = 0;
	char local_path[1024] = { 0 };
	char local_file[1024] = { 0 };
	msg_scp_upload_t *host = (msg_scp_upload_t *)host_buf;
	msg_scp_upload_t *net = (msg_scp_upload_t *)net_buf;
	msg_scp_upload_resp_t *resp_host =
		(msg_scp_upload_resp_t *)resp_host_buf;
	msg_scp_upload_resp_t *resp_net = (msg_scp_upload_resp_t *)resp_net_buf;

	memset(host_buf, 0x00, buf_len);
	memset(resp_host_buf, 0x00, buf_len);
	msg_scp_upload_ntoh(host, net);

	if (host->is_link) {
		link_item_t *item = (link_item_t *)host->data;
		InfoLog("begin upload file [%s -> %s]", item->dst_name,
			item->src_name);
		snprintf(local_path, sizeof(local_path), item->dst_name);
		pos = strrchr(local_path, '/');
		if (pos != NULL) {
			*pos = 0x00;
			create_dir(local_path, 0755);
		}

		if (symlink(item->src_name, item->dst_name) != 0) {
			if (EEXIST == errno) {
				WarningLog(
					"link %s -> %s failed status: %s(errno: %d)",
					item->dst_name, item->src_name,
					strerror(errno), errno);
			} else {
				ErrorLog(
					"link %s -> %s failed status: %s(errno: %d)",
					item->dst_name, item->src_name,
					strerror(errno), errno);
				resp_host->uiResult = errno;
				goto return__;
			}
		}
		ret = 0;
		resp_host->uiResult = 0x00;
		goto return__;
	}

	memcpy(local_path, host->data, host->data_len);
	memcpy(local_file, host->data, host->data_len);
	InfoLog("begin upload file [%s]", local_file);
	resp_host->uiResult = -1;
	if (host->block_id != 0) {
		ErrorLog("upload file [%s] failure: %s(errno: %d)", local_file,
			 strerror(errno), errno);
		goto return__;
	}
	pos = strrchr(local_path, '/');
	if (pos != NULL) {
		*pos = 0x00;
		create_dir(local_path, 0755);
	}

	mode = host->mode;
	gid = host->gid;
	uid = host->uid;
	atim = host->atim;
	mtim = host->mtim;
	ctim = host->ctim;
	fd = open(local_file, O_CREAT | O_WRONLY | O_TRUNC, mode);
	if (fd < 0) {
		resp_host->uiResult = -1;
		if (errno) {
			resp_host->uiResult = errno;
		}
		ErrorLog("upload open file [%s] failure: %s(errno: %d)",
			 local_file, strerror(errno), errno);
		goto return__;
	}
	if (ftruncate(fd, 0) != 0) {
		////resp_host->uiResult = errno;
		WarningLog("upload file [%s] ftruncate failure: %s(errno: %d)",
			   local_file, strerror(errno), errno);
	}

	while (true) {
		ret = read_is_ready(connfd, g_rpc_config->read_timeout);
		if (ret <= 0) {
			ErrorLog(
				"upload file [%s] recv request time out or error.",
				local_file);
			ret = -1;
			goto return__;
		}
		bytes = rpc_recv(connfd, (char *)net, buf_len, 0);
		if (bytes < 0) {
			ret = -1;
			ErrorLog(
				"upload file [%s] rpc recv failure: %s(errno: %d) ret:%d",
				local_file, strerror(errno), errno, bytes);
			goto return__;
		}
		msg_scp_upload_ntoh(host, net);
		if (host->uiMT != MT_EXECUTE_SCP_UPLOAD) {
			ErrorLog("upload file [%s] unkown msg:%x", local_file,
				 host->uiMT);
			goto return__;
		}
		if (host->is_encrypt) {
			if (host->is_compress) {
				data_dencrypt((unsigned char *)net->data,
					      host->data_len);
			} else {
				data_dencrypt((unsigned char *)host->data,
					      host->data_len);
			}
		}
		if (host->is_compress) {
			host->data_len = LZ4_decompress_safe(net->data,
							     host->data,
							     host->data_len,
							     MSG_BUFF_LEN);
			if (host->data_len != host->original_len) {
				ErrorLog(
					"decompress data for %s failure data_len: %u != "
					"original_len: %u",
					local_file, host->data_len,
					host->original_len);
				fprintf(stderr,
					"decompress data for %s failure data_len: %u != "
					"original_len: %u\n",
					local_file, host->data_len,
					host->original_len);
				goto return__;
			}
		}
		if (host->is_checksum) {
			unsigned int checksum = 0;
			for (unsigned int i = 0; i < host->data_len; ++i) {
				checksum += host->data[i];
			}
			if (checksum != host->checksum) {
				ErrorLog(
					"upload file [%s] write failure for [checksum: %u != "
					"host->checksum :%u]",
					local_file, checksum, host->checksum);
				goto return__;
			}
		}
		if (write(fd, host->data, host->data_len) != host->data_len) {
			resp_host->uiResult = errno;
			ErrorLog(
				"upload file [%s] write failure: %s(errno: %d)",
				local_file, strerror(errno), errno);
			goto return__;
		}
		recv_bytes += host->data_len;
		if (host->block_id == LAST_BLOCK) {
			f_size = int32_aggregate_to_int64(host->total_size_high,
							  host->total_size_low);
			break;
		}
	} /** completed data trans**/

	if (recv_bytes < f_size) {
		resp_host->uiResult = -1;
		ErrorLog(
			"upload file [%s] rpc recv failure: %s(errno: %d) recv_bytes:%ld "
			"!= f_size:%ld",
			local_file, strerror(errno), errno, recv_bytes, f_size);
		goto return__;
	}
	InfoLog("upload file [%s] complete success", local_file);
	////fchmod(fd, mode);
	if (FileStat::GetInstance()->UpdateFileStatTime(fd, atim, mtim, ctim,
							mode, gid, uid)) {
		ErrorLog("scp upload failure for update file: %s stat",
			 local_file);
		fprintf(stderr, "scp upload failure for update file: %s stat\n",
			local_file);
		goto return__;
	}
	ret = 0;
return__:
	resp_host->uiResult = ret;
	msg_scp_upload_resp_hton(resp_host, resp_net);
	if ((bytes = rpc_send(connfd, resp_net, resp_host->uiLEN, 0)) !=
	    (int)resp_host->uiLEN) {
		WarningLog(
			"upload file [%s] ret: %d, [bytes: %d, uiLEN: %u,] rpc recv "
			"failure: %s(errno: %d)",
			local_file, ret, bytes, resp_host->uiLEN,
			strerror(errno), errno);
		////ret = -1;
	}
	if (0 < fd) {
		close(fd);
		if (ret) {
			remove(local_file);
		}
	}
	return ret;
}

int OnMsgDownloadBlock(rpc_service_woker_info *conn)
{
	int connfd = conn->connfd;
	char *net_buf = conn->net_buf;
	char *host_buf = conn->host_buf;
	char *resp_net_buf = conn->resp_net_buf;
	char *resp_host_buf = conn->resp_host_buf;
	const int buf_len = conn->buf_len;

	int ret = -1;
	int fd = 0;
	int bytes = 0;
	int offset = 0;
	int b_offet = 0;
	int not_existed = 0;
	data_block_t *block = NULL;
	data_block_t *blocks = NULL;
	char *buf = NULL;
	char local_file[1024] = { 0 };
	const int block_size = buf_len - 2048;
	msg_download_block_t *host = (msg_download_block_t *)host_buf;
	msg_download_block_t *net = (msg_download_block_t *)net_buf;
	msg_download_block_resp_t *resp_host =
		(msg_download_block_resp_t *)resp_host_buf;
	msg_download_block_resp_t *resp_net =
		(msg_download_block_resp_t *)resp_net_buf;
	struct stat sss;
	int64_t begin_st_size = 0;
	int64_t total_send_size = 0;

	memset(host_buf, 0x00, buf_len);
	memset(resp_host_buf, 0x00, buf_len);
	msg_download_block_ntoh(host, net);
	const unsigned int is_compress = host->is_compress;
	const unsigned int is_encrypt = host->is_encrypt;
	const unsigned int is_checksum = host->is_checksum;
	////stat(host->file_name, &sss);
	snprintf(local_file, sizeof(local_file), "%s", host->data);
	if (stat(local_file, &sss)) {
		not_existed = 1;
		WarningLog("stat file: [%s] failure. %s(errno: %d)", local_file,
			   strerror(errno), errno);
	}
	begin_st_size = sss.st_size;
	InfoLog("begin download file [%s %u]", local_file, host->data_len);
	fd = open(local_file, O_RDONLY);
	if (fd < 0 || host->opt_type != 1 || host->bolck_num != 0) {
		if (fd < 0) {
			ErrorLog("open file: [%s] failure. %s(errno: %d)",
				 local_file, strerror(errno), errno);
		} else {
			ErrorLog(
				"download file: [%s] block failure. [fd: %d, opt_type: %u, "
				"bolck_num: %u]",
				local_file, fd, host->opt_type,
				host->bolck_num);
		}

		resp_host->uiResult = -1;
		if (not_existed || !file_existed(local_file) ||
		    TestIsDir(local_file) != 1) {
			resp_host->uiResult = 2222;
		}
		resp_host->opt_type = 1; /**open only*/
		resp_host->data_len =
			snprintf(resp_host->data, sizeof(resp_host->data),
				 "open file:[%s] failure.", local_file);
		msg_download_block_resp_hton(resp_host, resp_net);
		if (rpc_send(connfd, resp_net, resp_host->uiLEN, 0) !=
		    (int)resp_host->uiLEN) {
			////ret = -1;
		}
		goto return__;
	} else {
		memset(resp_host, 0x00, sizeof(*resp_host));
		resp_host->opt_type = 1; /**open only*/
		resp_host->data_len = 0;

		file_stat_hton(resp_host->data, &resp_host->data_len, &sss);
		msg_download_block_resp_hton(resp_host, resp_net);
		if (rpc_send(connfd, resp_net, resp_host->uiLEN, 0) !=
		    (int)resp_host->uiLEN) {
			ret = -1;
			ErrorLog(
				"send response for download file %s block failure. %s(errno: "
				"%d)",
				local_file, strerror(errno), errno);
			goto return__;
		}

		while (true) {
			ret = read_is_ready(connfd, g_rpc_config->read_timeout);
			if (ret > 0) {
				ret = rpc_recv(connfd, (char *)net, buf_len, 0);
				if (ret < 0) {
					// ret = -1;
					ErrorLog(
						"download file:%s failure. ret: %d",
						local_file, ret);
					goto return__;
				}
				net_buf[ret] = 0x00;
				msg_download_block_ntoh(host, net);
				if (host->uiMT != MT_EXECUTE_DOWNLOAD_BLOCK) {
					ErrorLog(
						"download file [%s] block unkown msg:%x",
						local_file, host->uiMT);
					goto return__;
				}
			} else {
				ErrorLog("download file [%s] block time out",
					 local_file);
				goto return__;
			}

			if (host->opt_type == 3) /**close only*/
			{
				memset(resp_host, 0x00, sizeof(*resp_host));
				resp_host->opt_type = 3; /** close only*/
				msg_download_block_resp_hton(resp_host,
							     resp_net);
				if (rpc_send(connfd, resp_net, resp_host->uiLEN,
					     0) != (int)resp_host->uiLEN) {
				}
				goto completed__;
			}

			b_offet = 0;
			blocks = (data_block_t *)host->data;
			WarningLog("[%s] host->bolck_num: %d", local_file,
				   host->bolck_num);
			while (b_offet < (int)host->bolck_num) {
				bytes = 0;
				offset = 0;
				resp_host->bolck_num = 0;
				for (/** b_offet = 0; **/;
				     b_offet < (int)host->bolck_num &&
				     offset < block_size;
				     ++b_offet) {
					data_block_ntoh(&blocks[b_offet]);
					if (block_size <=
					    (int)(offset +
						  blocks[b_offet].size)) {
						data_block_hton(
							&blocks[b_offet]);
						break;
					}

					block = (data_block_t *)(resp_host->data +
								 offset);
					offset += sizeof(*block);

					buf = resp_host->data + offset;
					block->offset = blocks[b_offet].offset;
					block->size = bytes = pread(
						fd, buf, blocks[b_offet].size,
						blocks[b_offet].offset);
					if (bytes < 0) {
						ret = -1;
						ErrorLog(
							"pread data failure %s(errno: %d) size: %lu "
							"offset: %lu",
							strerror(errno), errno,
							blocks[b_offet].size,
							blocks[b_offet].offset);
						goto return__;
					}
					offset += bytes;
					data_block_hton(block);
					++resp_host->bolck_num;
					total_send_size += bytes;
				}

				resp_host->opt_type = host->opt_type;
				resp_host->original_len = resp_host->data_len =
					offset;
				resp_host->uiResult = 0x00;
				resp_host->is_compress = is_compress;
				resp_host->is_encrypt = is_encrypt;
				resp_host->is_checksum = is_checksum;

				if (is_checksum) {
					resp_host->checksum = 0;
					for (unsigned int i = 0;
					     i < resp_host->data_len; ++i) {
						resp_host->checksum +=
							resp_host->data[i];
					}
				}

				/**compress*/
				if (is_compress) {
					resp_host->data_len =
						LZ4_compress_default(
							resp_host->data,
							resp_net->data,
							resp_host->original_len,
							buf_len - 1024);
					if (resp_host->data_len < 1) {
						ret = -1;
						ErrorLog(
							"compress data for %s failure data_len: %u, "
							"original_len: %u\n",
							local_file,
							resp_host->data_len,
							resp_host->original_len);
						goto return__;
					}
					memcpy(resp_host->data, resp_net->data,
					       resp_host->data_len);
				}

				if (is_encrypt) {
					data_encrypt((unsigned char *)
							     resp_host->data,
						     resp_host->data_len);
				}

				if (!write_is_ready(
					    connfd,
					    g_rpc_config->read_timeout)) {
					ret = -1;
					ErrorLog(
						"send file %s block data failure for time out.",
						local_file);
					goto return__;
				}
				msg_download_block_resp_hton(resp_host,
							     resp_net);
				if (rpc_send(connfd, resp_net, resp_host->uiLEN,
					     0) != (int)resp_host->uiLEN) {
					ret = -1;
					ErrorLog(
						"send file %s block data failure %s(errno: %d)",
						local_file, strerror(errno),
						errno);
					goto return__;
				}
			}
		}
	}
completed__:
	memset(&sss, 0x00, sizeof(sss));
	if (stat(local_file, &sss)) {
		WarningLog("stat file: [%s] failure. %s(errno: %d)", local_file,
			   strerror(errno), errno);
	}
	InfoLog("download data block of file [%s] complete success [begin: %ld, last: "
		"%ld, send: %ld]",
		local_file, begin_st_size, sss.st_size, total_send_size);
	ret = 0;
return__:
	close(fd);
	return ret;
}

int OnMsgUploadBlock(rpc_service_woker_info *conn)
{
	int connfd = conn->connfd;
	char *net_buf = conn->net_buf;
	char *host_buf = conn->host_buf;
	char *resp_net_buf = conn->resp_net_buf;
	char *resp_host_buf = conn->resp_host_buf;
	const int buf_len = conn->buf_len;

	int ret = -1;
	char *buf = NULL;
	int offset = 0;
	int fd = -1;
	int64_t bytes = 0;
	int64_t total_write = 0;
	int try_times = 0;
	data_block_t *block = NULL;
	char local_file[2048] = { 0 };

	mode_t mode = 0777;
	unsigned int gid = 0;
	unsigned int uid = 0;
	rpc_timespec_t atim = { 0 }; /* Time of last access.  */
	rpc_timespec_t mtim = { 0 }; /* Time of last modification.  */
	rpc_timespec_t ctim = { 0 }; /* Time of last status change.  */
	struct stat st = { 0 };

	msg_upload_block_t *host = (msg_upload_block_t *)host_buf;
	msg_upload_block_t *net = (msg_upload_block_t *)net_buf;
	msg_upload_block_resp_t *resp_host =
		(msg_upload_block_resp_t *)resp_host_buf;
	msg_upload_block_resp_t *resp_net =
		(msg_upload_block_resp_t *)resp_net_buf;

	memset(host_buf, 0x00, buf_len);
	memset(resp_host_buf, 0x00, buf_len);
	msg_upload_block_ntoh(host, net);
	const unsigned int is_compress = host->is_compress;
	const unsigned int is_encrypt = host->is_encrypt;
	const unsigned int is_checksum = host->is_checksum;
	////stat(host->file_name, &sss);
	snprintf(local_file, sizeof(local_file), "%s", host->data);
	InfoLog("begin upload file [%s %u]", local_file, host->data_len);
	fd = open(local_file, O_WRONLY | O_CREAT);
	if (fd < 0 || host->opt_type != 1 || host->bolck_num != 0) {
		if (fd < 0) {
			ErrorLog("open file: [%s] failure. %s(errno: %d)",
				 local_file, strerror(errno), errno);
		} else {
			ErrorLog(
				"upload file: [%s] block failure. [fd: %d, opt_type: %u, "
				"bolck_num: %u]",
				local_file, fd, host->opt_type,
				host->bolck_num);
		}

		resp_host->uiResult = -1;
		if (errno) {
			resp_host->uiResult = errno;
		}
		resp_host->opt_type = 1; /**open only*/
		resp_host->data_len =
			snprintf(resp_host->data, sizeof(resp_host->data),
				 "open file:[%s] failure.", local_file);
		msg_upload_block_resp_hton(resp_host, resp_net);
		if (rpc_send(connfd, resp_net, resp_host->uiLEN, 0) !=
		    (int)resp_host->uiLEN) {
			////ret = -1;
		}
		goto return__;
	} else {
		memset(resp_host, 0x00, sizeof(*resp_host));
		resp_host->opt_type = 1; /**open only*/
		resp_host->data_len = 0;
		msg_upload_block_resp_hton(resp_host, resp_net);
		if (rpc_send(connfd, resp_net, resp_host->uiLEN, 0) !=
		    (int)resp_host->uiLEN) {
			ret = -1;
			ErrorLog(
				"send response for upload file %s block failure. %s(errno: %d)",
				local_file, strerror(errno), errno);
			goto return__;
		}

		while (true) {
			ret = read_is_ready(connfd, g_rpc_config->read_timeout);
			if (ret <= 0) {
				ErrorLog(
					"recv request response time out or error.");
				ret = -1;
				goto return__;
			}
			if (rpc_recv(connfd, net, MSG_BUFF_LEN, 0) < 0) {
				ErrorLog("rpc recv failure: %s(errno: %d)",
					 strerror(errno), errno);
				goto return__;
			}
			msg_upload_block_ntoh(host, net);
			if (host->uiMT != MT_EXECUTE_UPLOAD_BLOCK) {
				ErrorLog("rpc upload block request failure: %s",
					 local_file);
				goto return__;
			}

			if (host->opt_type == 3) {
				memset(resp_host, 0x00, sizeof(*resp_host));
				resp_host->opt_type = 3; /** close only*/
				msg_upload_block_resp_hton(resp_host, resp_net);
				if (rpc_send(connfd, resp_net, resp_host->uiLEN,
					     0) != (int)resp_host->uiLEN) {
				}
				file_stat_ntoh(host->data, &host->data_len,
					       &st);
				goto completed__;
			}

			if (is_encrypt) {
				if (is_compress) {
					data_dencrypt(
						(unsigned char *)net->data,
						host->data_len);
				} else {
					data_dencrypt(
						(unsigned char *)host->data,
						host->data_len);
				}
			}

			/** decompress */
			if (is_compress) {
				host->data_len = LZ4_decompress_safe(
					net->data, host->data, host->data_len,
					MSG_BUFF_LEN);
				if (host->data_len != host->original_len) {
					ErrorLog(
						"decompress data for %s failure data_len: %u != "
						"original_len: %u",
						local_file, host->data_len,
						host->original_len);
					goto return__;
				}
			}

			if (is_checksum) {
				unsigned int checksum = 0;
				for (unsigned int i = 0; i < host->data_len;
				     ++i) {
					checksum += host->data[i];
				}
				if (checksum != host->checksum) {
					ErrorLog(
						"upload file [%s] write failure for [checksum: %u != "
						"host->checksum :%u]",
						local_file, checksum,
						host->checksum);
					goto return__;
				}
			}

			offset = 0;
			for (int i = 0; i < (int)host->bolck_num &&
					offset < (int)host->data_len;
			     ++i) {
				block = (data_block_t *)(host->data + offset);
				data_block_ntoh(block);
				offset += sizeof(*block);

				buf = host->data + offset;
				offset += block->size;
				if (0 < block->size) {
					try_times = 0;
					total_write = 0;
					do {
						bytes = pwrite(
							fd, buf + total_write,
							block->size -
								total_write,
							block->offset +
								total_write);
						if (0 <= bytes) {
							total_write += bytes;
						} else {
							ErrorLog(
								"rpc write bytes: %ld failure: %s(errno: %d)",
								bytes,
								strerror(errno),
								errno);
							break;
						}
						/* code */
					} while (total_write <
							 (ssize_t)block->size &&
						 ++try_times < 10);

					if (total_write !=
					    (ssize_t)block->size) {
						ErrorLog(
							"rpc write failure: %s(errno: %d)",
							strerror(errno), errno);
						goto return__;
					}
				}
			}
			if (offset != (int)host->data_len) {
				ErrorLog(
					"rpc upload block request failure for offset: %d != "
					"host->data_len: %u",
					offset, host->data_len);
				goto return__;
			}
		}
	}
completed__:
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
		ErrorLog("upload failure for update file: %s stat", local_file);
		goto return__;
	}
	if (ftruncate(fd, st.st_size)) {
		ErrorLog("upload failure for update file: %s st.st_size: %ld",
			 local_file, st.st_size);
		goto return__;
	}
	InfoLog("upload data block of file [%s] complete success", local_file);
	ret = 0;
return__:
	if (-1 < fd) {
		close(fd);
	}
	if (ret) {
		remove(local_file);
		ErrorLog("rpc upload %s failure. remove", local_file);
	}
	return ret;
}

int OnMsgFileStat(rpc_service_woker_info *conn)
{
	int connfd = conn->connfd;
	char *net_buf = conn->net_buf;
	char *host_buf = conn->host_buf;
	char *resp_net_buf = conn->resp_net_buf;
	char *resp_host_buf = conn->resp_host_buf;
	const int buf_len = conn->buf_len;

	int ret = -1;
	int type = 0;
	char *data_tmp = NULL;
	const int try_again = 111111;
	struct stat sss;
	msg_file_stat_t *host = (msg_file_stat_t *)host_buf;
	msg_file_stat_t *net = (msg_file_stat_t *)net_buf;
	msg_file_stat_resp_t *resp_host = (msg_file_stat_resp_t *)resp_host_buf;
	msg_file_stat_resp_t *resp_net = (msg_file_stat_resp_t *)resp_net_buf;
	char local_file[1024] = { 0 };
	const int buflen = buf_len - 2048;

	memset(host_buf, 0x00, buf_len);
	memset(resp_host_buf, 0x00, buf_len);
	msg_file_stat_ntoh(host, net);

	resp_host->existed = 0;

	type = host->type;
	if (type == 0) {
		snprintf(local_file, sizeof(local_file), "%s", host->file_name);
		if (stat(local_file, &sss)) {
			WarningLog("stat file: [%s] failure. %s(errno: %d)",
				   local_file, strerror(errno), errno);
			resp_host->existed = 1;
		}

		file_stat_hton(resp_host->data, &resp_host->data_len, &sss);

		msg_file_stat_resp_hton(resp_host, resp_net);
		if (rpc_send(connfd, resp_net, resp_host->uiLEN, 0) !=
		    (int)resp_host->uiLEN) {
			ErrorLog("rpc send chdir failure: %s(errno: %d)",
				 strerror(errno), errno);
			goto return__;
		}
	} else {
		while (true) {
			if (type == 1) {
				InfoLog("batch get file stat start");
				msg_file_stat_resp_hton(resp_host, resp_net);
				if (rpc_send(connfd, resp_net, resp_host->uiLEN,
					     0) != (int)resp_host->uiLEN) {
					ErrorLog(
						"rpc send get file stat failure: %s(errno: %d)",
						strerror(errno), errno);
					goto return__;
				}
			} else if (type == 2) {
				snprintf(local_file, sizeof(local_file), "%s",
					 host->file_name);
				memset(&sss, 0x00, sizeof(sss));
				if (stat(local_file, &sss)) {
					WarningLog(
						"stat file: [%s] failure. %s(errno: %d)",
						local_file, strerror(errno),
						errno);
				}
				file_stat_hton(resp_host->data,
					       &resp_host->data_len, &sss);
				msg_file_stat_resp_hton(resp_host, resp_net);
				if (rpc_send(connfd, resp_net, resp_host->uiLEN,
					     0) != (int)resp_host->uiLEN) {
					ErrorLog(
						"rpc send get file stat failure: %s(errno: %d)",
						strerror(errno), errno);
					goto return__;
				}
			} else if (type == 3) {
				int offset = 0;
				char *f_name = NULL;
				const char *flag = ";";
				resp_host->data_len = 0;
				f_name = strtok_r(host->file_name, flag,
						  &data_tmp);
				while (f_name != NULL) {
					{
						file_stat_item_t file_stat_item;
						file_stat_item.f_name = f_name;
						if (stat(f_name,
							 &file_stat_item.st)) {
							file_stat_item.st
								.st_size = -1;
							WarningLog(
								"stat file: [%s] failure. %s(errno: %d)",
								f_name,
								strerror(errno),
								errno);
						}

						if (buflen <=
						    (int)(offset +
							  file_stat_item
								  .Size())) {
							resp_host->data_len =
								offset;
							msg_file_stat_resp_hton(
								resp_host,
								resp_net);
							if (rpc_send(
								    connfd,
								    resp_net,
								    resp_host->uiLEN,
								    0) !=
							    (int)resp_host
								    ->uiLEN) {
								ErrorLog(
									"rpc send get file stat failure: %s(errno: "
									"%d)",
									strerror(
										errno),
									errno);
								goto return__;
							}

							offset = 0;
						}
						if (file_stat_item.Serialize(
							    resp_host->data,
							    offset, buflen)) {
							ErrorLog(
								"rpc send get file %s stat failure for bad "
								"serialize.",
								f_name);
							goto return__;
						}
						resp_host->data_len = offset;
					}

					f_name =
						strtok_r(NULL, flag, &data_tmp);
				}
				resp_host->data_len = offset;
				msg_file_stat_resp_hton(resp_host, resp_net);
				if (rpc_send(connfd, resp_net, resp_host->uiLEN,
					     0) != (int)resp_host->uiLEN) {
					ErrorLog(
						"rpc send get file stat failure: %s(errno: %d)",
						strerror(errno), errno);
					goto return__;
				}
				offset = 0;
			} else if (type == try_again) {
				// do nothing
			} else {
				InfoLog("batch get file stat completed");
				break;
			}
			ret = read_is_ready(connfd, g_rpc_config->read_timeout);
			if (ret > 0) {
				ret = rpc_recv(connfd, (char *)net, buf_len, 0);
				if (ret < 0) {
					ErrorLog(
						"recv for batch get file stat failure %d",
						ret);
					goto return__;
				}
				net_buf[ret] = 0x00;
				msg_file_stat_ntoh(host, net);
				type = host->type;
			} else {
				type = try_again;
			}
		}
	}
	ret = 0;
return__:

	return ret;
}

int OnMsgFileExisted(rpc_service_woker_info *conn)
{
	int connfd = conn->connfd;
	char *net_buf = conn->net_buf;
	char *host_buf = conn->host_buf;
	char *resp_net_buf = conn->resp_net_buf;
	char *resp_host_buf = conn->resp_host_buf;
	const int buf_len = conn->buf_len;

	int ret = -1;
	msg_file_existed_t *host = (msg_file_existed_t *)host_buf;
	msg_file_existed_t *net = (msg_file_existed_t *)net_buf;
	msg_file_existed_resp_t *resp_host =
		(msg_file_existed_resp_t *)resp_host_buf;
	msg_file_existed_resp_t *resp_net =
		(msg_file_existed_resp_t *)resp_net_buf;
	char local_file[1024] = { 0 };

	memset(host_buf, 0x00, buf_len);
	memset(resp_host_buf, 0x00, buf_len);
	msg_file_existed_ntoh(host, net);

	snprintf(local_file, sizeof(local_file), "%s", host->file_name);

	resp_host->existed = file_existed(local_file);
	InfoLog("%s existed: %u", local_file, resp_host->existed);

	msg_file_existed_resp_hton(resp_host, resp_net);
	if (rpc_send(connfd, resp_net, resp_host->uiLEN, 0) !=
	    (int)resp_host->uiLEN) {
		ErrorLog("rpc send chdir failure: %s(errno: %d)",
			 strerror(errno), errno);
		goto return__;
	}

	ret = 0;
return__:
	return ret;
}

void nc_extend(rpc_service_woker_info *conn)
{
	int connfd = conn->connfd;
	char *net_buf = conn->net_buf;
	char *host_buf = conn->host_buf;
	char *resp_net_buf = conn->resp_net_buf;
	char *resp_host_buf = conn->resp_host_buf;
	const int buf_len = conn->buf_len;

	int ret = -1;
	int type = 0;
	FILE *fptr = NULL;
	int outfd = 0;
	int offset = 0;
	int bytes_write = 0;
	int64_t total_write = 0;
	msg_nc_extend_t *host = (msg_nc_extend_t *)host_buf;
	msg_nc_extend_t *net = (msg_nc_extend_t *)net_buf;
	msg_nc_extend_resp_t *resp_host = (msg_nc_extend_resp_t *)resp_host_buf;
	msg_nc_extend_resp_t *resp_net = (msg_nc_extend_resp_t *)resp_net_buf;
	char command[4096] = { 0 };
	memset(host_buf, 0x00, buf_len);
	memset(resp_host_buf, 0x00, buf_len);
	msg_nc_extend_ntoh(host, net);

	total_write = 0;
	type = host->type;
	if (type == 0) {
		snprintf(command, sizeof(command), "%s", host->data);
		fptr = popen(command, "w");
		if (fptr == NULL) {
			ErrorLog(
				"rpc send nc extend %s popen failure: %s(errno: %d)",
				command, strerror(errno), errno);
			goto return__;
		}

		outfd = fileno(fptr);

		InfoLog("begin nc extend [%s]", command);
		type = 1;
	}

	while (type == 1 && fptr != NULL) {
		ret = read_is_ready(connfd, g_rpc_config->read_timeout);
		if (ret < 0) {
			ErrorLog("recv request failure for connection error.");
			goto return__;
		}

		if (ret == 0) {
			continue;
		}

		ret = rpc_recv(connfd, (char *)net, buf_len, 0);
		if (ret < 0) {
			ErrorLog("recv for nc extend [%s] failure %d", command,
				 ret);
			goto return__;
		}
		net_buf[ret] = 0x00;
		msg_nc_extend_ntoh(host, net);
		type = host->type;

		if (host->is_encrypt) {
			if (host->is_compress) {
				data_dencrypt((unsigned char *)net->data,
					      host->data_len);
			} else {
				data_dencrypt((unsigned char *)host->data,
					      host->data_len);
			}
		}
		if (host->is_compress) {
			host->data_len = LZ4_decompress_safe(net->data,
							     host->data,
							     host->data_len,
							     MSG_BUFF_LEN);
			if (host->data_len != host->original_len) {
				ErrorLog(
					"decompress data failure data_len: %u != original_len: %u",
					host->data_len, host->original_len);
				goto return__;
			}
		}
		if (host->is_checksum) {
			unsigned int checksum = 0;
			for (unsigned int i = 0; i < host->data_len; ++i) {
				checksum += host->data[i];
			}
			if (checksum != host->checksum) {
				ErrorLog(
					"write failure for [checksum: %u != host->checksum :%u]",
					checksum, host->checksum);
				goto return__;
			}
		}

		if (type == 1) {
			offset = 0;
			while (offset < (int)host->data_len) {
				bytes_write = write(outfd,
						    (host->data + offset),
						    (host->data_len - offset));
				if (bytes_write <= 0) {
					ErrorLog(
						"rpc nc extend %s write failure offset: %d, "
						"bytes_write:%d != (int)host->data_len:%d: %s(errno: "
						"%d)",
						command, offset, bytes_write,
						(int)host->data_len,
						strerror(errno), errno);
					goto return__;
				}
				offset += bytes_write;
			}
			if (offset != (int)host->data_len) {
				ErrorLog(
					"rpc nc extend %s write failure offset: %d, bytes_write:%d "
					"!= (int)host->data_len:%d: %s(errno: %d)",
					command, offset, bytes_write,
					(int)host->data_len, strerror(errno),
					errno);
				goto return__;
			}
			total_write += offset;
		} else if (type == 2) {
			InfoLog("nc extend [%s] completed total write: %ld",
				command, total_write);
			break;
		} else {
			ErrorLog("nc extend [%s] failure. type:%d", command,
				 type);
			break;
		}
	}

	ret = 0;
return__:
	if (fptr) {
		ret = pclose(fptr);

		if (WIFEXITED(ret)) {
			ret = WEXITSTATUS(ret);
			InfoLog("nc extend [%s] completed success, ret: %d",
				command, ret);
		} else if (WIFSIGNALED(ret)) {
			ret = -WTERMSIG(ret);
			ErrorLog("nc extend [%s] completed failure, ret: %d",
				 command, ret);
		} else {
			ret = -1;
		}
	}

	memset(resp_host, 0x00, buf_len);
	resp_host->uiResult = ret;
	msg_nc_extend_resp_hton(resp_host, resp_net);
	if (rpc_send(connfd, resp_net, resp_host->uiLEN, 0) !=
	    (int)resp_host->uiLEN) {
		ErrorLog("rpc send get file stat failure: %s(errno: %d)",
			 strerror(errno), errno);
	}
}

int OnIOCTLFsbackupDev(rpc_service_woker_info *conn)
{
	int connfd = conn->connfd;
	char *net_buf = conn->net_buf;
	char *host_buf = conn->host_buf;
	char *resp_net_buf = conn->resp_net_buf;
	char *resp_host_buf = conn->resp_host_buf;
	const int buf_len = conn->buf_len;

	int ret = -1;
	int fd = -1;
	const char *pathname = g_rpc_config->dev_path;
	msg_ioctl_fsbackup_t *host = (msg_ioctl_fsbackup_t *)host_buf;
	msg_ioctl_fsbackup_t *net = (msg_ioctl_fsbackup_t *)net_buf;
	msg_ioctl_fsbackup_resp_t *resp_host =
		(msg_ioctl_fsbackup_resp_t *)resp_host_buf;
	msg_ioctl_fsbackup_resp_t *resp_net =
		(msg_ioctl_fsbackup_resp_t *)resp_net_buf;

	memset(host_buf, 0x00, buf_len);
	memset(resp_host_buf, 0x00, buf_len);
	msg_ioctl_fsbackup_ntoh(host, net);
	resp_host->uiResult = 0x01;

	fd = open(pathname, O_RDWR | O_NOCTTY, 0600);
	if (fd < 0) {
		resp_host->err_no = errno;
		ErrorLog("open: %s, %d status(%s, errno: %d)", pathname, fd,
			 strerror(errno), errno);
		goto return__;
	} else if (g_rpc_config->debug) {
		InfoLog("open: %s, %d status(%s, errno: %d)", pathname, fd,
			strerror(errno), errno);
	}

	if (host->opt_type == FSBACKUP_IIOCTL_UPDATE_LOG_DIR) {
		if (host->data_len != sizeof(ioctl_dir_path)) {
			ErrorLog(
				"ioctl: %s, %d data_len(%d) not match sizeof(ioctl_dir_path)",
				pathname, fd, host->data_len);
			resp_host->data_len = 0;
			resp_host->err_no = EINVAL;
			goto return__;
		}
		ret = ioctl(fd, host->opt_type, host->data);
		if (ret) {
			resp_host->data_len = 0;
			resp_host->err_no = errno;
			ErrorLog("ioctl: %s, %d status(%s, errno: %d) ret: %d",
				 pathname, fd, strerror(errno), errno, ret);
			goto return__;
		} else {
			resp_host->data_len = sizeof(fsbackup_kernel_stat);
			memcpy(resp_host->data, host->data,
			       resp_host->data_len);
			resp_host->uiResult = 0x00;
		}
	} else if (host->opt_type == FSBACKUP_IIOCTL_META_SYNC) {
		if (host->data_len != sizeof(ioctl_dir_path)) {
			ErrorLog(
				"ioctl: %s, %d data_len(%d) not match sizeof(ioctl_dir_path)",
				pathname, fd, host->data_len);
			resp_host->data_len = 0;
			resp_host->err_no = EINVAL;
			goto return__;
		}
		ret = ioctl(fd, host->opt_type, host->data);
		if (ret) {
			resp_host->data_len = 0;
			resp_host->err_no = errno;
			ErrorLog("ioctl: %s, %d status(%s, errno: %d) ret: %d",
				 pathname, fd, strerror(errno), errno, ret);
			goto return__;
		} else {
			resp_host->data_len = sizeof(fsbackup_kernel_stat);
			memcpy(resp_host->data, host->data,
			       resp_host->data_len);
			resp_host->uiResult = 0x00;
		}
	} else if (host->opt_type == FSBACKUP_IIOCTL_LOG_SWITCH) {
		if (host->data_len != sizeof(ioctl_dir_path)) {
			ErrorLog(
				"ioctl: %s, %d data_len(%d) not match sizeof(ioctl_dir_path)",
				pathname, fd, host->data_len);
			resp_host->data_len = 0;
			resp_host->err_no = EINVAL;
			goto return__;
		}
		InfoLog("info: ioctl_dir_path path:%s, app_name:%s, start_time:%lld\n",
			((ioctl_dir_path *)(host->data))->path,
			((ioctl_dir_path *)(host->data))->app_name,
			((ioctl_dir_path *)(host->data))->start_time);
		ret = ioctl(fd, host->opt_type, host->data);
		if (ret) {
			resp_host->data_len = 0;
			resp_host->err_no = errno;
			ErrorLog("ioctl: %s, %d status(%s, errno: %d) ret: %d",
				 pathname, fd, strerror(errno), errno, ret);
			goto return__;
		} else {
			resp_host->data_len = sizeof(ioctl_dir_path);
			memcpy(resp_host->data, host->data,
			       resp_host->data_len);
			resp_host->uiResult = 0x00;
		}
	} else if (host->opt_type == FSBACKUP_IIOCTL_SET_BACKUP_PATH ||
		   host->opt_type == FSBACKUP_IIOCTL_DEL_BACKUP_PATH ||
		   host->opt_type == FSBACKUP_IIOCTL_SET_EXCLUDE_PATH ||
		   host->opt_type == FSBACKUP_IIOCTL_DEL_EXCLUDE_PATH) {
		if (host->data_len != sizeof(ioctl_dir_path)) {
			ErrorLog(
				"ioctl: %s, %d data_len(%d) not match sizeof(ioctl_dir_path)",
				pathname, fd, host->data_len);
			resp_host->data_len = 0;
			resp_host->err_no = EINVAL;
			goto return__;
		}
		ret = ioctl(fd, host->opt_type, host->data);
		if (ret) {
			resp_host->data_len = 0;
			resp_host->err_no = errno;
			ErrorLog("ioctl: %s, %d status(%s, errno: %d) ret: %d",
				 pathname, fd, strerror(errno), errno, ret);
			goto return__;
		} else {
			resp_host->data_len = 0;
			resp_host->uiResult = 0x00;
		}
	} else {
		ErrorLog("bad ioctl type: %d, %d status(%s, errno: %d) ret: %d",
			 host->opt_type, fd, strerror(errno), errno, ret);
		resp_host->data_len = 0;
		resp_host->err_no = EINVAL;
	}
	ret = 0;
return__:
	msg_ioctl_fsbackup_resp_hton(resp_host, resp_net);

	if (rpc_send(connfd, resp_net, resp_host->uiLEN, 0) !=
	    (int)resp_host->uiLEN) {
		ErrorLog("rpc send chdir failure: %s(errno: %d)",
			 strerror(errno), errno);
	}
	if (0 < fd) {
		if (g_rpc_config->debug) {
			InfoLog("close %s success. FD: %d.", pathname, fd);
		}
		close(fd);
	}
	return ret;
}

int rpc_conn_srv_lstat(struct rpc_conn *conn)
{
	int ret = 0;
	int rc = 0;
	struct buf *msgw = conn->msgw;
	struct buf *msgr = conn->msgr;
	char *remote_file = NULL;
	struct stat st;

	if ((ret = buf_get_cstring(msgr, &remote_file, NULL)) != 0) {
		ErrorLog("get_cstring failure. %s(errno: %d)", strerror(errno),
			 errno);
		goto return__;
	}

	rc = lstat(remote_file, &st);
	if ((ret = buf_put_u32(msgw, rc)) != 0 ||
	    (ret = buf_put_u32(msgw, errno)) != 0) {
		ErrorLog("put_u32 failure. %s failure. %s(errno: %d)",
			 remote_file, strerror(errno), errno);
		goto return__;
	}

	if (rc == 0 && (ret = encode_attrib(msgw, &st)) != 0) {
		ErrorLog("encode_attrib failure. %s failure. %s(errno: %d)",
			 remote_file, strerror(errno), errno);
		goto return__;
	} else if (rc != 0) {
		ErrorLog("lstat %s failure. %s(errno: %d)", remote_file,
			 strerror(errno), errno);
	}

	ret = rpc_conn_send_msg(conn);
	if (ret != 0) {
		ErrorLog("rpc_conn_send_msg failure. %s failure. %s(errno: %d)",
			 remote_file, strerror(errno), errno);
		goto return__;
	}

	ret = 0;
return__:
	if (remote_file != NULL) {
		free(remote_file);
	}
	return ret;
}

int rpc_conn_srv_readdir(struct rpc_conn *conn)
{
	int ret = 0;
	int rc = 0;
	int entry_count = 0;
	int dir_fd = 0;
	int chunk_size = 0;
	struct buf *buf_tmp = NULL;
	struct buf *msgw = conn->msgw;
	struct buf *msgr = conn->msgr;
	char *remote_dir = NULL;
	uint8_t remote_flags = 0;
	DIR *dir = NULL;
	char link_path[PATH_MAX];
	struct stat st;

	if ((ret = buf_get_u8(msgr, &remote_flags)) != 0 ||
	    (ret = buf_get_u32(msgr, (uint32_t *)&chunk_size)) != 0 ||
	    (ret = buf_get_cstring(msgr, &remote_dir, NULL)) != 0) {
		ErrorLog("get_cstring failure. %s(errno: %d)", strerror(errno),
			 errno);
		goto return__;
	}

	buf_tmp = buf_new();
	if (buf_tmp == NULL) {
		ErrorLog("buf_new failure. %s failure. %s(errno: %d)",
			 remote_dir, strerror(errno), errno);
		ret = -1;
		goto return__;
	}

	dir = opendir(remote_dir);
	if (dir == NULL) {
		rc = -1;
	} else {
		dir_fd = dirfd(dir);
	}
	if ((ret = buf_put_u32(msgw, rc)) != 0 ||
	    (ret = buf_put_u32(msgw, errno)) != 0) {
		ErrorLog("put_u32 failure. %s failure. %s(errno: %d)",
			 remote_dir, strerror(errno), errno);
		goto return__;
	}

	if ((ret = rpc_conn_send_msg(conn)) != 0) {
		ErrorLog("rpc_conn_send_msg failure. %s failure. %s(errno: %d)",
			 remote_dir, strerror(errno), errno);
		goto return__;
	}

	if (rc != 0) {
		ErrorLog("opendir %s failure. %s(errno: %d)", remote_dir,
			 strerror(errno), errno);
		goto return__;
	}

	while (1) {
		struct dirent *ent = readdir(dir);
		if (ent == NULL) {
			break;
		}
		if (strcmp(ent->d_name, ".") == 0 ||
		    strcmp(ent->d_name, "..") == 0) {
			continue;
		}

		if ((ret = buf_put_cstring(buf_tmp, ent->d_name)) != 0 ||
		    (ret = buf_put_u8(buf_tmp, ent->d_type)) != 0) {
			ErrorLog(
				"put_cstring failure. %s failure. %s(errno: %d)",
				remote_dir, strerror(errno), errno);
			goto return__;
		}

		if (remote_flags & READDIR_FLAG_WITH_STAT) {
			if (fstatat(dir_fd, ent->d_name, &st,
				    AT_SYMLINK_NOFOLLOW) != 0) {
				ErrorLog("fstatat %s failure. %s(errno: %d)",
					 remote_dir, strerror(errno), errno);
				goto return__;
			}
			if ((ret = encode_attrib(buf_tmp, &st)) != 0) {
				ErrorLog(
					"encode_attrib failure. %s failure. %s(errno: %d)",
					remote_dir, strerror(errno), errno);
				goto return__;
			}
		}

		if (ent->d_type == DT_LNK &&
		    (remote_flags & READDIR_FLAG_WITH_LINK)) {
			int link_len = readlinkat(dir_fd, ent->d_name,
						  link_path, sizeof(link_path));
			if (link_len < 0) {
				ErrorLog("readlinkat %s failure. %s(errno: %d)",
					 remote_dir, strerror(errno), errno);
				goto return__;
			}
			if ((ret = buf_put_cstring(buf_tmp, link_path)) != 0) {
				ErrorLog(
					"put_cstring failure. %s failure. %s(errno: %d)",
					remote_dir, strerror(errno), errno);
				errno = ENOMEM;
				goto return__;
			}
		}
		entry_count++;

		if (entry_count >= chunk_size) {
			if ((ret = buf_put_u32(msgw, entry_count)) != 0 ||
			    (ret = buf_put_stringb(msgw, buf_tmp)) != 0) {
				ErrorLog(
					"put_u32 failure. %s failure. %s(errno: %d)",
					remote_dir, strerror(errno), errno);
				goto return__;
			}

			if ((ret = rpc_conn_send_msg(conn)) != 0) {
				ErrorLog(
					"rpc_conn_send_msg failure. %s failure. %s(errno: %d)",
					remote_dir, strerror(errno), errno);
				goto return__;
			}
			buf_clear(buf_tmp);
			entry_count = 0;
		}
	}

	if (entry_count > 0) {
		if ((ret = buf_put_u32(msgw, entry_count)) != 0 ||
		    (ret = buf_put_stringb(msgw, buf_tmp)) != 0) {
			ErrorLog("put_u32 failure. %s failure. %s(errno: %d)",
				 remote_dir, strerror(errno), errno);
			goto return__;
		}

	} else {
		if ((ret = buf_put_u32(msgw, 0)) != 0) {
			ErrorLog("put_u32 failure. %s failure. %s(errno: %d)",
				 remote_dir, strerror(errno), errno);
			goto return__;
		}
	}
	if ((ret = rpc_conn_send_msg(conn)) != 0) {
		ErrorLog("rpc_conn_send_msg failure. %s failure. %s(errno: %d)",
			 remote_dir, strerror(errno), errno);
		goto return__;
	}

	ret = 0;
return__:
	if (buf_tmp != NULL) {
		buf_free(buf_tmp);
	}
	if (dir != NULL) {
		closedir(dir);
	}

	if (remote_dir != NULL) {
		free(remote_dir);
	}
	return ret;
}

struct readdir_tree_ctx {
	struct rpc_conn *conn;
	struct buf *buf_tmp;
	uint8_t remote_flags;
	int chunk_size;
	int entry_count;
	size_t base_len;
	int traversal_error;
};

static int readdir_tree_process_entry(struct readdir_tree_ctx *ctx,
				      const char *dir_path,
				      struct dirent *entry, int dirfd)
{
	char rel_path[PATH_MAX];
	const char *rel_start = dir_path + ctx->base_len;
	while (*rel_start == '/') {
		rel_start++;
	}

	if (rel_start[0] == '\0') {
		snprintf(rel_path, sizeof(rel_path), "%s", entry->d_name);
	} else {
		snprintf(rel_path, sizeof(rel_path), "%s/%s", rel_start,
			 entry->d_name);
	}

	int ret;
	if ((ret = buf_put_cstring(ctx->buf_tmp, rel_path)) != 0 ||
	    (ret = buf_put_u8(ctx->buf_tmp, entry->d_type)) != 0) {
		return ret;
	}

	if (ctx->remote_flags & READDIR_FLAG_WITH_STAT) {
		struct stat st;
		int rc;
		if (dirfd >= 0) {
			rc = fstatat(dirfd, entry->d_name, &st,
				     AT_SYMLINK_NOFOLLOW);
		} else {
			char entry_path[PATH_MAX];
			snprintf(entry_path, sizeof(entry_path), "%s/%s",
				 dir_path, entry->d_name);
			rc = lstat(entry_path, &st);
		}
		if (rc != 0) {
			return -1;
		}
		if ((ret = encode_attrib(ctx->buf_tmp, &st)) != 0) {
			return ret;
		}
	}

	if (entry->d_type == DT_LNK &&
	    (ctx->remote_flags & READDIR_FLAG_WITH_LINK)) {
		char link_path[PATH_MAX];
		int link_len;
		if (dirfd >= 0) {
			link_len = readlinkat(dirfd, entry->d_name, link_path,
					     sizeof(link_path));
		} else {
			char entry_path[PATH_MAX];
			snprintf(entry_path, sizeof(entry_path), "%s/%s",
				 dir_path, entry->d_name);
			link_len = readlink(entry_path, link_path,
					    sizeof(link_path));
		}
		if (link_len < 0) {
			return -1;
		}
		link_path[link_len] = '\0';
		if ((ret = buf_put_cstring(ctx->buf_tmp, link_path)) != 0) {
			return ret;
		}
	}

	ctx->entry_count++;

	if (ctx->entry_count >= ctx->chunk_size) {
		struct buf *msgw = ctx->conn->msgw;
		if ((ret = buf_put_u32(msgw, ctx->entry_count)) != 0 ||
		    (ret = buf_put_stringb(msgw, ctx->buf_tmp)) != 0) {
			return ret;
		}
		if ((ret = rpc_conn_send_msg(ctx->conn)) != 0) {
			return ret;
		}
		buf_clear(ctx->buf_tmp);
		ctx->entry_count = 0;
	}

	return 0;
}

static int readdir_tree_file_cb(const char *fullpath, struct dirent *entry,
				void *user_data)
{
	return readdir_tree_process_entry(
		(struct readdir_tree_ctx *)user_data, fullpath, entry, -1);
}

static int readdir_tree_dir_cb(const char *fullpath, struct dirent *entry,
			       void *user_data)
{
	return readdir_tree_process_entry(
		(struct readdir_tree_ctx *)user_data, fullpath, entry, -1);
}

static int readdir_tree_link_cb(int dirfd, const char *fullpath,
				struct dirent *entry, void *user_data)
{
	return readdir_tree_process_entry(
		(struct readdir_tree_ctx *)user_data, fullpath, entry, dirfd);
}

static int readdir_tree_other_cb(int dirfd, const char *fullpath,
				 struct dirent *entry, void *user_data)
{
	return readdir_tree_process_entry(
		(struct readdir_tree_ctx *)user_data, fullpath, entry, dirfd);
}

int rpc_conn_srv_readdir_tree(struct rpc_conn *conn)
{
	int ret = 0;
	int chunk_size = 0;
	size_t remote_dir_len = 0;
	struct buf *buf_tmp = NULL;
	struct buf *msgw = conn->msgw;
	struct buf *msgr = conn->msgr;
	char *remote_dir = NULL;
	uint8_t remote_flags = 0;
	struct readdir_tree_ctx ctx;
	dir_traversal_config_t config;

	if ((ret = buf_get_u8(msgr, &remote_flags)) != 0 ||
	    (ret = buf_get_u32(msgr, (uint32_t *)&chunk_size)) != 0 ||
	    (ret = buf_get_cstring(msgr, &remote_dir, NULL)) != 0) {
		ErrorLog("parse request failure. %s(errno: %d)",
			 strerror(errno), errno);
		goto return__;
	}

	buf_tmp = buf_new();
	if (buf_tmp == NULL) {
		ErrorLog("buf_new failure. %s(errno: %d)", strerror(errno),
			 errno);
		ret = -1;
		goto return__;
	}

	if ((ret = buf_put_u32(msgw, 0)) != 0 ||
	    (ret = buf_put_u32(msgw, 0)) != 0) {
		ErrorLog("put response failure. %s(errno: %d)",
			 strerror(errno), errno);
		goto return__;
	}
	if ((ret = rpc_conn_send_msg(conn)) != 0) {
		ErrorLog("send response failure. %s(errno: %d)",
			 strerror(errno), errno);
		goto return__;
	}

	remote_dir_len = strlen(remote_dir);
	while (remote_dir_len > 1 && remote_dir[remote_dir_len - 1] == '/') {
		remote_dir_len--;
	}
	remote_dir[remote_dir_len] = '\0';

	memset(&ctx, 0, sizeof(ctx));
	ctx.conn = conn;
	ctx.buf_tmp = buf_tmp;
	ctx.traversal_error = 0;
	ctx.remote_flags = remote_flags;
	ctx.chunk_size = chunk_size;
	ctx.base_len = remote_dir_len;

	memset(&config, 0, sizeof(config));
	config.file_cb = readdir_tree_file_cb;
	config.dir_cb = readdir_tree_dir_cb;
	config.link_cb = readdir_tree_link_cb;
	config.other_cb = readdir_tree_other_cb;
	config.user_data = &ctx;
	config.recursive = 1;

	ret = dir_traversal_at(AT_FDCWD, remote_dir, &config);
	if (ret != 0) {
		ctx.traversal_error = ret;
		ErrorLog("dir_traversal_at %s failed, ret=%d", remote_dir,
			 ret);
	}

	if (ctx.traversal_error != 0) {
		buf_clear(buf_tmp);
		if ((ret = buf_put_u32(msgw, 0)) != 0) {
			ErrorLog("put end marker failure. %s(errno: %d)",
				 strerror(errno), errno);
			goto return__;
		}
	} else if (ctx.entry_count > 0) {
		if ((ret = buf_put_u32(msgw, ctx.entry_count)) != 0 ||
		    (ret = buf_put_stringb(msgw, buf_tmp)) != 0) {
			ErrorLog("put remaining failure. %s(errno: %d)",
				 strerror(errno), errno);
			goto return__;
		}
	} else {
		if ((ret = buf_put_u32(msgw, 0)) != 0) {
			ErrorLog("put end marker failure. %s(errno: %d)",
				 strerror(errno), errno);
			goto return__;
		}
	}
	if ((ret = rpc_conn_send_msg(conn)) != 0) {
		ErrorLog("send remaining failure. %s(errno: %d)",
			 strerror(errno), errno);
		goto return__;
	}

	ret = ctx.traversal_error;
return__:
	if (buf_tmp != NULL) {
		buf_free(buf_tmp);
	}
	if (remote_dir != NULL) {
		free(remote_dir);
	}
	return ret;
}

int rpc_conn_srv_pread(struct rpc_conn *conn)
{
	int ret = 0;
	int rc = -1;
	struct buf *msgw = conn->msgw;
	struct buf *msgr = conn->msgr;
	char *remote_path = NULL;
	uint64_t remote_offset = 0;
	uint64_t remote_size = 0;
	uint32_t chunk_len = PREAD_CHUNK_SIZE;
	char *chunk = NULL;

	if ((ret = buf_get_u64(msgr, &remote_offset)) != 0 ||
	    (ret = buf_get_u64(msgr, &remote_size)) != 0 ||
	    (ret = buf_get_cstring(msgr, &remote_path, NULL)) != 0) {
		ErrorLog("get_cstring failure. %s(errno: %d)", strerror(errno),
			 errno);
		goto return__;
	}

	rc = open(remote_path, O_RDONLY);
	if (rc < 0) {
		ErrorLog("open %s failure. %s(errno: %d)", remote_path,
			 strerror(errno), errno);

		if ((ret = buf_put_u32(msgw, rc)) != 0 ||
		    (ret = buf_put_u32(msgw, errno)) != 0) {
			ErrorLog("put_u32 failure. %s failure. %s(errno: %d)",
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

		goto return__;
	} else if (g_rpc_config->debug) {
		InfoLog("open %s success. FD: %d.", remote_path, rc);
	}

	chunk = (char *)malloc(chunk_len);
	if (chunk == NULL) {
		ErrorLog("malloc failure. %s failure. %s(errno: %d)",
			 remote_path, strerror(errno), errno);
		goto return__;
	}

	while (remote_size >= 0) {
		uint64_t len = chunk_len;
		if (len > remote_size) {
			len = remote_size;
		}
		int n = pread(rc, chunk, len, remote_offset);
		if ((ret = buf_put_u32(msgw, n)) != 0) {
			ErrorLog("put_u32 failure. %s failure. %s(errno: %d)",
				 remote_path, strerror(errno), errno);
			goto return__;
		}
		if (n < 0) {
			ErrorLog("pread %s failure. %s(errno: %d)", remote_path,
				 strerror(errno), errno);

			if ((ret = buf_put_u32(msgw, errno)) != 0) {
				ErrorLog(
					"put_u32 failure. %s failure. %s(errno: %d)",
					remote_path, strerror(errno), errno);
				goto return__;
			}
		} else if (n > 0) {
			if ((ret = buf_put_string(msgw, chunk, n)) != 0) {
				ErrorLog(
					"put_u32 failure. %s failure. %s(errno: %d)",
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

		remote_offset += n;
		remote_size -= n;

		if (n <= 0) {
			break;
		}
	}

	ret = 0;
return__:
	if (rc >= 0) {
		close(rc);
		if (g_rpc_config->debug) {
			InfoLog("close %s success. FD: %d.", remote_path, rc);
		}
	}
	if (chunk != NULL) {
		free(chunk);
	}
	if (remote_path) {
		free(remote_path);
	}
	return ret;
}

int rpc_conn_srv_pwrite(struct rpc_conn *conn)
{
	int ret = 0;
	int rc = -1;
	int rc2 = -1;
	struct buf *msgw = conn->msgw;
	struct buf *msgr = conn->msgr;
	char *remote_path = NULL;
	uint64_t remote_offset = 0;
	uint64_t remote_size = 0;

	size_t recv_len = 0;

	if ((ret = buf_get_u64(msgr, &remote_offset)) != 0 ||
	    (ret = buf_get_u64(msgr, &remote_size)) != 0 ||
	    (ret = buf_get_cstring(msgr, &remote_path, NULL)) != 0) {
		ErrorLog("get_cstring failure. %s(errno: %d)", strerror(errno),
			 errno);
		goto return__;
	}

	rc = open(remote_path, O_WRONLY | O_CREAT | O_TRUNC, 0644);
	if (rc < 0) {
		ErrorLog("open %s failure. %s(errno: %d)", remote_path,
			 strerror(errno), errno);
		if ((ret = buf_put_u32(msgw, rc)) != 0 ||
		    (ret = buf_put_u32(msgw, errno)) != 0) {
			ErrorLog("put_u32 failure. %s failure. %s(errno: %d)",
				 remote_path, strerror(errno), errno);
			goto return__;
		}
		if ((ret = rpc_conn_send_msg(conn)) != 0) {
			ErrorLog("send_msg failure. %s failure. %s(errno: %d)",
				 remote_path, strerror(errno), errno);
			goto return__;
		}

		ret = -1;
		goto errno__;
	} else if (g_rpc_config->debug) {
		InfoLog("open %s success. FD: %d.", remote_path, rc);
	}

	while (1) {
		const char *data = NULL;
		size_t len = 0;

		ret = rpc_conn_recv_msg(conn);
		if (ret != 0) {
			ErrorLog(
				"rpc_conn_recv_msg failure. %s failure. %s(errno: %d)",
				remote_path, strerror(errno), errno);
			goto return__;
		}

		if ((ret = buf_get_string_direct(msgr, (const u_char **)&data,
						 &len)) != 0) {
			ErrorLog(
				"get_string_direct failure. %s failure. %s(errno: %d)",
				remote_path, strerror(errno), errno);
			goto return__;
		}
		if (len == 0) {
			break;
		}
		rc2 = pwrite(rc, data, len, remote_offset);
		if (rc2 != (ssize_t)len) {
			ErrorLog("write %s failure. %d!=%d. %s(errno: %d)",
				 remote_path, rc2, len, strerror(errno), errno);
			if ((ret = buf_put_u32(msgw, -1)) != 0 ||
			    (ret = buf_put_u32(msgw, errno)) != 0) {
				ErrorLog(
					"put_u32 failure. %s failure. %s(errno: %d)",
					remote_path, strerror(errno), errno);
				goto return__;
			}
			if ((ret = rpc_conn_send_msg(conn)) != 0) {
				ErrorLog(
					"send_msg failure. %s failure. %s(errno: %d)",
					remote_path, strerror(errno), errno);
				goto return__;
			}
			ret = -1;
			rpc_conn_close(conn);
			goto errno__;
		}

		remote_offset += len;

		recv_len += len;
		if (recv_len >= remote_size) {
			break;
		}
	}

	if ((ret = buf_put_u32(msgw, 0)) != 0 ||
	    (ret = buf_put_u32(msgw, errno)) != 0) {
		ErrorLog("put_u32 failure. %s failure. %s(errno: %d)",
			 remote_path, strerror(errno), errno);
		goto return__;
	}

	if ((ret = rpc_conn_send_msg(conn)) != 0) {
		ErrorLog("send_msg failure. %s failure. %s(errno: %d)",
			 remote_path, strerror(errno), errno);
		goto return__;
	}

	ret = 0;

return__:
	if (rc >= 0) {
		close(rc);
		if (g_rpc_config->debug) {
			InfoLog("close %s success. FD: %d.", remote_path, rc);
		}
		if (ret != 0) {
			unlink(remote_path);
		}
	}
	if (remote_path) {
		free(remote_path);
	}
	return ret;
errno__:
	ret = -1;
	goto return__;
}

int rpc_conn_srv_mkdir(struct rpc_conn *conn)
{
	int ret = 0;
	int rc = 0;
	struct buf *msgw = conn->msgw;
	struct buf *msgr = conn->msgr;
	char *remote_file = NULL;
	uint32_t remote_mode = 0;

	if ((ret = buf_get_u32(msgr, &remote_mode)) != 0 ||
	    (ret = buf_get_cstring(msgr, &remote_file, NULL)) != 0) {
		ErrorLog("get_cstring failure. %s(errno: %d)", strerror(errno),
			 errno);
		goto return__;
	}

	rc = mkdir(remote_file, remote_mode);
	if ((ret = buf_put_u32(msgw, rc)) != 0 ||
	    (ret = buf_put_u32(msgw, errno)) != 0) {
		ErrorLog("put_u32 failure. %s failure. %s(errno: %d)",
			 remote_file, strerror(errno), errno);
		goto return__;
	}

	if (rc != 0) {
		ErrorLog("mkdir %s failure. %s(errno: %d)", remote_file,
			 strerror(errno), errno);
	} else {
		InfoLog("mkdir %s:%d success.", remote_file, remote_mode);
	}

	ret = rpc_conn_send_msg(conn);
	if (ret != 0) {
		ErrorLog("rpc_conn_send_msg failure. %s failure. %s(errno: %d)",
			 remote_file, strerror(errno), errno);
		goto return__;
	}

	ret = 0;
return__:
	if (remote_file != NULL) {
		free(remote_file);
	}
	return ret;
}

int rpc_conn_srv_fchownats(struct rpc_conn *conn)
{
	int ret = 0;
	int rc = 0;
	struct buf *msgw = conn->msgw;
	struct buf *msgr = conn->msgr;
	int dirfd = -1;
	char *remote_path = NULL;
	char *remote_item = NULL;
	uint32_t remote_gid = 0;
	uint32_t remote_uid = 0;
	uint32_t remote_count = 0;

	if ((ret = buf_get_u32(msgr, &remote_count)) != 0 ||
	    (ret = buf_get_cstring(msgr, &remote_path, NULL)) != 0) {
		ErrorLog("get_u32 failure. %s(errno: %d)", strerror(errno),
			 errno);
		goto return__;
	}

	dirfd = open(remote_path, O_RDONLY | O_DIRECTORY);
	if ((ret = buf_put_u32(msgw, dirfd < 0 ? -1 : 0)) != 0 ||
	    (ret = buf_put_u32(msgw, errno)) != 0) {
		ErrorLog("put_u32 failure. %s(errno: %d)", strerror(errno),
			 errno);
		goto return__;
	}

	if (dirfd < 0) {
		goto error__;
	} else if (g_rpc_config->debug) {
		InfoLog("open %s success. FD: %d.", remote_path, dirfd);
	}
	for (uint32_t i = 0; i < remote_count; i++) {
		if ((ret = buf_get_u32(msgr, &remote_uid)) != 0 ||
		    (ret = buf_get_u32(msgr, &remote_gid)) != 0 ||
		    (ret = buf_get_cstring(msgr, &remote_item, NULL)) != 0) {
			ErrorLog(
				"get_cstring failure. %s failure. %s(errno: %d)",
				remote_item, strerror(errno), errno);
			goto return__;
		}

		rc = fchownat(dirfd, remote_item, remote_uid, remote_gid,
			      AT_SYMLINK_NOFOLLOW);
		if ((ret = buf_put_u32(msgw, rc)) != 0 ||
		    (ret = buf_put_u32(msgw, errno)) != 0) {
			ErrorLog("put_u32 failure. %s failure. %s(errno: %d)",
				 remote_item, strerror(errno), errno);
			goto return__;
		}

		if (rc != 0) {
			ErrorLog("fchownat %s:%d:%d failure. %s(errno: %d)",
				 remote_item, remote_uid, remote_gid,
				 strerror(errno), errno);
		} else {
			InfoLog("fchownat %s:%d:%d success.", remote_item,
				remote_uid, remote_gid);
		}
		free(remote_item);
		remote_item = NULL;
	}
error__:
	ret = rpc_conn_send_msg(conn);
	if (ret != 0) {
		ErrorLog("rpc_conn_send_msg failure. %s failure. %s(errno: %d)",
			 remote_item, strerror(errno), errno);
		goto return__;
	}

	ret = 0;
return__:
	if (dirfd >= 0) {
		if (g_rpc_config->debug) {
			InfoLog("close %s success. FD: %d.", remote_path,
				dirfd);
		}
		close(dirfd);
	}
	if (remote_path) {
		free(remote_path);
	}

	if (remote_item != NULL) {
		free(remote_item);
	}
	return ret;
}

int rpc_conn_srv_fchmodats(struct rpc_conn *conn)
{
	int ret = 0;
	int rc = 0;
	struct buf *msgw = conn->msgw;
	struct buf *msgr = conn->msgr;
	int dirfd = -1;
	char *remote_path = NULL;
	char *remote_item = NULL;
	uint32_t remote_mode = 0;
	uint32_t remote_count = 0;

	if ((ret = buf_get_u32(msgr, &remote_count)) != 0 ||
	    (ret = buf_get_cstring(msgr, &remote_path, NULL)) != 0) {
		ErrorLog("get_u32 failure. %s(errno: %d)", strerror(errno),
			 errno);
		goto return__;
	}

	dirfd = open(remote_path, O_RDONLY | O_DIRECTORY);
	if ((ret = buf_put_u32(msgw, dirfd < 0 ? -1 : 0)) != 0 ||
	    (ret = buf_put_u32(msgw, errno)) != 0) {
		ErrorLog("put_u32 failure. %s(errno: %d)", strerror(errno),
			 errno);
		goto return__;
	}

	if (dirfd < 0) {
		goto error__;
	} else if (g_rpc_config->debug) {
		InfoLog("open %s success. FD: %d.", remote_path, dirfd);
	}
	for (uint32_t i = 0; i < remote_count; i++) {
		if ((ret = buf_get_u32(msgr, &remote_mode)) != 0 ||
		    (ret = buf_get_cstring(msgr, &remote_item, NULL)) != 0) {
			ErrorLog(
				"get_cstring failure. %s failure. %s(errno: %d)",
				remote_item, strerror(errno), errno);
			goto return__;
		}

		rc = fchmodat(dirfd, remote_item, remote_mode,
			      AT_SYMLINK_NOFOLLOW);
		if ((ret = buf_put_u32(msgw, rc)) != 0 ||
		    (ret = buf_put_u32(msgw, errno)) != 0) {
			ErrorLog("put_u32 failure. %s failure. %s(errno: %d)",
				 remote_item, strerror(errno), errno);
			goto return__;
		}

		if (rc != 0) {
			ErrorLog("fchownat %s:%d failure. %s(errno: %d)",
				 remote_item, remote_mode, strerror(errno),
				 errno);
		} else {
			InfoLog("fchownat %s:%d success.", remote_item,
				remote_mode);
		}
		free(remote_item);
		remote_item = NULL;
	}
error__:
	ret = rpc_conn_send_msg(conn);
	if (ret != 0) {
		ErrorLog("rpc_conn_send_msg failure. %s failure. %s(errno: %d)",
			 remote_item, strerror(errno), errno);
		goto return__;
	}

	ret = 0;
return__:
	if (dirfd >= 0) {
		if (g_rpc_config->debug) {
			InfoLog("close %s success. FD: %d.", remote_path,
				dirfd);
		}
		close(dirfd);
	}
	if (remote_path) {
		free(remote_path);
	}

	if (remote_item != NULL) {
		free(remote_item);
	}
	return ret;
}

int rpc_conn_srv_download_fileats(struct rpc_conn *conn)
{
	int ret = 0;
	int fd = -1;
	struct buf *msgw = conn->msgw;
	struct buf *msgr = conn->msgr;
	int dirfd = -1;
	char *remote_dir = NULL;
	char *remote_item = NULL;
	uint32_t remote_count = 0;

	// TODO: buf size limit
	char read_buf[4096];

	if ((ret = buf_get_u32(msgr, &remote_count)) != 0 ||
	    (ret = buf_get_cstring(msgr, &remote_dir, NULL)) != 0) {
		ErrorLog("get_u32 failure. %s(errno: %d)", strerror(errno),
			 errno);
		goto return__;
	}

	dirfd = open(remote_dir, O_RDONLY | O_DIRECTORY);
	if ((ret = buf_put_u32(msgw, dirfd < 0 ? -1 : 0)) != 0 ||
	    (ret = buf_put_u32(msgw, errno)) != 0) {
		ErrorLog("put_u32 failure. %s(errno: %d)", strerror(errno),
			 errno);
		goto return__;
	}

	ret = rpc_conn_send_msg(conn);
	if (ret != 0) {
		ErrorLog("rpc_conn_send_msg failure. %s(errno: %d)",
			 strerror(errno), errno);
		goto return__;
	}

	if (dirfd < 0) {
		goto return__;
	}
	for (uint32_t i = 0; i < remote_count; i++) {
		if ((ret = buf_get_cstring(msgr, &remote_item, NULL)) != 0) {
			ErrorLog("get_cstring failure. %s(errno: %d)",
				 strerror(errno), errno);
			goto return__;
		}

		fd = openat(dirfd, remote_item, O_RDONLY);
		if ((ret = buf_put_u32(msgw, fd < 0 ? -1 : 0)) != 0 ||
		    (ret = buf_put_u32(msgw, errno)) != 0) {
			ErrorLog("put_u32 failure. %s failure. %s(errno: %d)",
				 remote_item, strerror(errno), errno);
			goto return__;
		}

		if (fd < 0) {
			ErrorLog("openat %s failure. %s(errno: %d)",
				 remote_item, strerror(errno), errno);
		} else {
			InfoLog("openat %s success.", remote_item);
		}

		if (fd < 0) {
			ret = rpc_conn_send_msg(conn);
			if (ret != 0) {
				ErrorLog(
					"rpc_conn_send_msg failure. %s failure. %s(errno: %d)",
					remote_item, strerror(errno), errno);
				goto return__;
			}
			continue;
		}

		ret = 0;
		while (1) {
			ssize_t len = read(fd, read_buf, sizeof(read_buf));
			if ((ret = buf_put_u32(msgw, len)) != 0 ||
			    (ret = buf_put_u32(msgw, errno)) != 0) {
				ErrorLog(
					"put_u32 failure. %s failure. %s(errno: %d)",
					remote_item, strerror(errno), errno);
				goto return__;
			}
			if (len < 0) {
				ErrorLog("read %s failure. %s(errno: %d)",
					 remote_item, strerror(errno), errno);
				break;
			} else if (len == 0) {
				InfoLog("read %s success.", remote_item);
				break;
			}
			if ((ret = buf_put_string(msgw, read_buf, len)) != 0) {
				ErrorLog(
					"put_data failure. %s failure. %s(errno: %d)",
					remote_item, strerror(errno), errno);
				goto return__;
			}
			if ((ret = rpc_conn_send_msg(conn)) != 0) {
				ErrorLog(
					"rpc_conn_send_msg failure. %s failure. %s(errno: %d)",
					remote_item, strerror(errno), errno);
				goto return__;
			}
		}
		if ((ret = rpc_conn_send_msg(conn)) != 0) {
			ErrorLog(
				"rpc_conn_send_msg failure. %s failure. %s(errno: %d)",
				remote_item, strerror(errno), errno);
			goto return__;
		}
		free(remote_item);
		remote_item = NULL;
		close(fd);
		fd = -1;
	}

	ret = 0;
return__:
	if (fd >= 0) {
		close(fd);
	}
	if (dirfd >= 0) {
		close(dirfd);
	}

	if (remote_dir) {
		free(remote_dir);
	}

	if (remote_item != NULL) {
		free(remote_item);
	}
	return ret;
}

int rpc_conn_srv_upload_fileats(struct rpc_conn *conn)
{
	int ret = 0;
	int fd = 0;
	int rc = 0;
	struct buf *msgw = conn->msgw;
	struct buf *msgr = conn->msgr;
	int dirfd = -1;
	char *remote_dir = NULL;
	char *remote_item = NULL;
	uint32_t remote_count = 0;

	if ((ret = buf_get_u32(msgr, &remote_count)) != 0 ||
	    (ret = buf_get_cstring(msgr, &remote_dir, NULL)) != 0) {
		ErrorLog("get_u32 failure. %s(errno: %d)", strerror(errno),
			 errno);
		goto return__;
	}

	dirfd = open(remote_dir, O_RDONLY | O_DIRECTORY);
	if ((ret = buf_put_u32(msgw, dirfd < 0 ? -1 : 0)) != 0 ||
	    (ret = buf_put_u32(msgw, errno)) != 0) {
		ErrorLog("put_u32 failure. %s(errno: %d)", strerror(errno),
			 errno);
		goto return__;
	}

	ret = rpc_conn_send_msg(conn);
	if (ret != 0) {
		ErrorLog("rpc_conn_send_msg failure. %s(errno: %d)",
			 strerror(errno), errno);
		goto return__;
	}

	if (dirfd < 0) {
		goto return__;
	}
	for (uint32_t i = 0; i < remote_count; i++) {
		ret = rpc_conn_is_ready_recv_msg(conn);
		if (ret != 0) {
			ErrorLog(
				"rpc_conn_recv_msg failure. %s failure. %s(errno: %d)",
				remote_dir, strerror(errno), errno);
			goto return__;
		}
		if ((ret = buf_get_cstring(msgr, &remote_item, NULL)) != 0 ||
		    (ret = buf_get_u32(msgr, (uint32_t *)&rc)) != 0 ||
		    (ret = buf_get_u32(msgr, (uint32_t *)&errno)) != 0) {
			ErrorLog("get_cstring failure. %s(errno: %d)",
				 strerror(errno), errno);
			goto return__;
		}

		if (rc < 0) {
			WarningLog("openat %s failure. %s(errno: %d)",
				   remote_item, strerror(errno), errno);
			free(remote_item);
			remote_item = NULL;
			continue;
		}

		fd = openat(dirfd, remote_item, O_WRONLY | O_CREAT | O_TRUNC,
			    0644);

		if (fd < 0) {
			ErrorLog("openat %s failure. %s(errno: %d)",
				 remote_item, strerror(errno), errno);
			if ((ret = buf_put_u32(msgw, -1)) != 0 ||
			    (ret = buf_put_u32(msgw, errno)) != 0 ||
			    (ret = buf_put_cstring(msgw, remote_item)) != 0) {
				ErrorLog(
					"put_u32 failure. %s:%s failure. %s(errno: %d)",
					remote_dir, remote_item,
					strerror(errno), errno);
				goto return__;
			}
			if ((ret = rpc_conn_send_msg(conn)) != 0) {
				ErrorLog(
					"rpc_conn_send_msg failure. %s failure. %s(errno: %d)",
					remote_item, strerror(errno), errno);
				goto return__;
			}
			rpc_conn_close(conn);
			goto return__;
		} else {
			InfoLog("openat %s success.", remote_item);
		}

		ret = 0;
		while (true) {
			const char *data = NULL;
			size_t len = 0;

			if ((ret = buf_get_u32(msgr, (uint32_t *)&rc)) != 0 ||
			    (ret = buf_get_u32(msgr, (uint32_t *)&errno)) !=
				    0) {
				ErrorLog(
					"get_u32 failure. %s failure. %s(errno: %d)",
					remote_dir, strerror(errno), errno);
				goto return__;
			}
			if (rc < 0) {
				ErrorLog(
					"upload_fileat %s:%s failure. %s(errno: %d)",
					remote_dir, remote_item,
					strerror(errno), errno);
				break;
			} else if (rc == 0) {
				InfoLog("upload_fileat %s:%s success.",
					remote_dir, remote_item);
				break;
			}
			if ((ret = buf_get_string_direct(msgr,
							 (const u_char **)&data,
							 &len)) != 0) {
				ErrorLog(
					"get_string_direct failure. %s failure. %s(errno: %d)",
					remote_dir, strerror(errno), errno);
				goto return__;
			}
			if (write(fd, data, len) != (ssize_t)len) {
				ErrorLog("write %s:%s failure. %s(errno: %d)",
					 remote_dir, remote_item,
					 strerror(errno), errno);
				if ((ret = buf_put_u32(msgw, -1)) != 0 ||
				    (ret = buf_put_u32(msgw, errno)) != 0 ||
				    (ret = buf_put_cstring(msgw,
							   remote_item)) != 0) {
					ErrorLog(
						"put_u32 failure. %s:%s failure. %s(errno: %d)",
						remote_dir, remote_item,
						strerror(errno), errno);
					goto return__;
				}
				if ((ret = rpc_conn_send_msg(conn)) != 0) {
					ErrorLog(
						"rpc_conn_send_msg failure. %s failure. %s(errno: %d)",
						remote_item, strerror(errno),
						errno);
					goto return__;
				}
				rpc_conn_close(conn);
				ret = -1;
				goto return__;
			}

			ret = rpc_conn_is_ready_recv_msg(conn);
			if (ret != 0) {
				ErrorLog(
					"rpc_conn_recv_msg failure. %s failure. %s(errno: %d)",
					remote_dir, strerror(errno), errno);
				goto return__;
			}
		}
		free(remote_item);
		remote_item = NULL;
		close(fd);
		fd = -1;
	}

	ret = 0;

	if ((ret = buf_put_u32(msgw, 0)) != 0 ||
	    (ret = buf_put_u32(msgw, errno)) != 0) {
		ErrorLog("put_u32 failure. %s:%s failure. %s(errno: %d)",
			 remote_dir, remote_item, strerror(errno), errno);
		goto return__;
	}
	if ((ret = rpc_conn_send_msg(conn)) != 0) {
		ErrorLog("rpc_conn_send_msg failure. %s failure. %s(errno: %d)",
			 remote_item, strerror(errno), errno);
		goto return__;
	}

return__:
	if (fd >= 0) {
		close(fd);
	}
	if (dirfd >= 0) {
		close(dirfd);
	}

	if (remote_item != NULL) {
		free(remote_item);
	}
	if (remote_dir != NULL) {
		free(remote_dir);
	}
	return ret;
}

int rpc_conn_srv_readlink(struct rpc_conn *conn)
{
	int rc = 0;
	int ret = 0;
	struct buf *msgw = conn->msgw;
	struct buf *msgr = conn->msgr;
	char *remote_path = NULL;
	char buf[PATH_MAX];

	if ((ret = buf_get_cstring(msgr, &remote_path, NULL)) != 0) {
		ErrorLog("buf_get_cstring failure. %s(errno: %d)",
			 strerror(errno), errno);
		goto return__;
	}

	rc = readlink(remote_path, buf, sizeof(buf) - 1);
	if ((ret = buf_put_u32(msgw, rc < 0 ? -1 : 0)) != 0 ||
	    (ret = buf_put_u32(msgw, errno)) != 0) {
		ErrorLog("put_u32 failure. %s(errno: %d)", strerror(errno),
			 errno);
		goto return__;
	}

	if (rc < 0) {
		ErrorLog("readlink %s failure. %s(errno: %d)", remote_path,
			 strerror(errno), errno);
	} else {
		if ((ret = buf_put_string(msgw, buf, rc)) != 0) {
			ErrorLog("put_string failure. %s(errno: %d)",
				 strerror(errno), errno);
			goto return__;
		}
	}

	ret = rpc_conn_send_msg(conn);
	if (ret != 0) {
		ErrorLog("rpc_conn_send_msg failure. %s(errno: %d)",
			 strerror(errno), errno);
		goto return__;
	}

return__:
	if (remote_path != NULL) {
		free(remote_path);
	}
	return ret;
}

int rpc_conn_srv_symlink(struct rpc_conn *conn)
{
	int rc = 0;
	int ret = 0;
	struct buf *msgw = conn->msgw;
	struct buf *msgr = conn->msgr;
	char *remote_path = NULL;
	char *link_target = NULL;

	if ((ret = buf_get_cstring(msgr, &link_target, NULL)) != 0 ||
	    (ret = buf_get_cstring(msgr, &remote_path, NULL)) != 0) {
		ErrorLog("buf_get_cstring failure. %s(errno: %d)",
			 strerror(errno), errno);
		goto return__;
	}

	rc = symlink(link_target, remote_path);
	if ((ret = buf_put_u32(msgw, rc)) != 0 ||
	    (ret = buf_put_u32(msgw, errno)) != 0) {
		ErrorLog("put_u32 failure. %s(errno: %d)", strerror(errno),
			 errno);
		goto return__;
	}

	if (rc < 0) {
		ErrorLog("symlink %s failure. %s(errno: %d)", remote_path,
			 strerror(errno), errno);
	}

	ret = rpc_conn_send_msg(conn);
	if (ret != 0) {
		ErrorLog("rpc_conn_send_msg failure. %s(errno: %d)",
			 strerror(errno), errno);
		goto return__;
	}

return__:

	if (link_target != NULL) {
		free(link_target);
	}

	if (remote_path != NULL) {
		free(remote_path);
	}
	return ret;
}

int rpc_conn_srv_access(struct rpc_conn *conn)
{
	int rc = 0;
	int ret = 0;
	struct buf *msgw = conn->msgw;
	struct buf *msgr = conn->msgr;
	char *remote_path = NULL;
	int type = 0;

	if ((ret = buf_get_u32(msgr, (uint32_t *)&type)) != 0 ||
	    (ret = buf_get_cstring(msgr, &remote_path, NULL)) != 0) {
		ErrorLog("buf_get_cstring failure. %s(errno: %d)",
			 strerror(errno), errno);
		goto return__;
	}

	rc = access(remote_path, type);
	if ((ret = buf_put_u32(msgw, rc)) != 0 ||
	    (ret = buf_put_u32(msgw, errno)) != 0) {
		ErrorLog("put_u32 failure. %s(errno: %d)", strerror(errno),
			 errno);
		goto return__;
	}

	if (rc < 0) {
		ErrorLog("access %s failure. %s(errno: %d)", remote_path,
			 strerror(errno), errno);
	}

	ret = rpc_conn_send_msg(conn);
	if (ret != 0) {
		ErrorLog("rpc_conn_send_msg failure. %s(errno: %d)",
			 strerror(errno), errno);
		goto return__;
	}

return__:

	if (remote_path != NULL) {
		free(remote_path);
	}
	return ret;
}

int rpc_conn_srv_mkdirall(struct rpc_conn *conn)
{
	int ret = 0;
	int rc = 0;
	struct buf *msgw = conn->msgw;
	struct buf *msgr = conn->msgr;
	char *remote_file = NULL;
	uint32_t remote_mode = 0;

	if ((ret = buf_get_cstring(msgr, &remote_file, NULL)) != 0) {
		ErrorLog("get_cstring failure. %s(errno: %d)", strerror(errno),
			 errno);
		goto return__;
	}

	rc = mkdir_path(remote_file);
	if ((ret = buf_put_u32(msgw, rc)) != 0 ||
	    (ret = buf_put_u32(msgw, errno)) != 0) {
		ErrorLog("put_u32 failure. %s failure. %s(errno: %d)",
			 remote_file, strerror(errno), errno);
		goto return__;
	}

	if (rc != 0) {
		ErrorLog("mkdirall %s failure. %s(errno: %d)", remote_file,
			 strerror(errno), errno);
	} else {
		InfoLog("mkdirall %s:%d success.", remote_file, remote_mode);
	}

	ret = rpc_conn_send_msg(conn);
	if (ret != 0) {
		ErrorLog("rpc_conn_send_msg failure. %s failure. %s(errno: %d)",
			 remote_file, strerror(errno), errno);
		goto return__;
	}

	ret = 0;
return__:
	if (remote_file != NULL) {
		free(remote_file);
	}
	return ret;
}

int rpc_conn_srv_chmod(struct rpc_conn *conn)
{
	int ret = 0;
	int rc = 0;
	struct buf *msgw = conn->msgw;
	struct buf *msgr = conn->msgr;
	char *remote_file = NULL;
	uint32_t remote_mode = 0;

	if ((ret = buf_get_u32(msgr, &remote_mode)) != 0 ||
	    (ret = buf_get_cstring(msgr, &remote_file, NULL)) != 0) {
		ErrorLog("get_cstring failure. %s(errno: %d)", strerror(errno),
			 errno);
		goto return__;
	}

	rc = chmod(remote_file, remote_mode);
	if ((ret = buf_put_u32(msgw, rc)) != 0 ||
	    (ret = buf_put_u32(msgw, errno)) != 0) {
		ErrorLog("put_u32 failure. %s failure. %s(errno: %d)",
			 remote_file, strerror(errno), errno);
		goto return__;
	}

	if (rc != 0) {
		ErrorLog("chmod %s failure. %s(errno: %d)", remote_file,
			 strerror(errno), errno);
	} else {
		InfoLog("chmod %s:%d success.", remote_file, remote_mode);
	}

	ret = rpc_conn_send_msg(conn);
	if (ret != 0) {
		ErrorLog("rpc_conn_send_msg failure. %s failure. %s(errno: %d)",
			 remote_file, strerror(errno), errno);
		goto return__;
	}

	ret = 0;
return__:
	if (remote_file != NULL) {
		free(remote_file);
	}
	return ret;
}

int rpc_conn_srv_chown(struct rpc_conn *conn)
{
	int ret = 0;
	int rc = 0;
	struct buf *msgw = conn->msgw;
	struct buf *msgr = conn->msgr;
	char *remote_file = NULL;
	uint32_t remote_uid = 0;
	uint32_t remote_gid = 0;

	if ((ret = buf_get_u32(msgr, &remote_uid)) != 0 ||
	    (ret = buf_get_u32(msgr, &remote_gid)) != 0 ||
	    (ret = buf_get_cstring(msgr, &remote_file, NULL)) != 0) {
		ErrorLog("get_cstring failure. %s(errno: %d)", strerror(errno),
			 errno);
		goto return__;
	}

	rc = chown(remote_file, remote_uid, remote_gid);
	if ((ret = buf_put_u32(msgw, rc)) != 0 ||
	    (ret = buf_put_u32(msgw, errno)) != 0) {
		ErrorLog("put_u32 failure. %s failure. %s(errno: %d)",
			 remote_file, strerror(errno), errno);
		goto return__;
	}

	if (rc != 0) {
		ErrorLog("chmod %s failure. %s(errno: %d)", remote_file,
			 strerror(errno), errno);
	} else {
		InfoLog("chmod %s:%d success.", remote_file, remote_uid);
	}

	ret = rpc_conn_send_msg(conn);
	if (ret != 0) {
		ErrorLog("rpc_conn_send_msg failure. %s failure. %s(errno: %d)",
			 remote_file, strerror(errno), errno);
		goto return__;
	}

	ret = 0;
return__:
	if (remote_file != NULL) {
		free(remote_file);
	}
	return ret;
}

int rpc_conn_srv_openat(struct rpc_conn *conn)
{
	int ret = 0;
	int rc = 0;
	struct buf *msgw = conn->msgw;
	struct buf *msgr = conn->msgr;
	char *remote_name = NULL;
	uint32_t remote_fd = 0;
	uint32_t remote_flag = 0;
	uint32_t remote_mode = 0;

	if ((ret = buf_get_u32(msgr, &remote_fd)) != 0 ||
	    (ret = buf_get_u32(msgr, &remote_flag)) != 0 ||
	    (ret = buf_get_u32(msgr, &remote_mode)) != 0 ||
	    (ret = buf_get_cstring(msgr, &remote_name, NULL)) != 0) {
		ErrorLog("get_cstring failure. %s(errno: %d)", strerror(errno),
			 errno);
		goto return__;
	}

	rc = openat(remote_fd, remote_name, remote_flag, remote_mode);
	if ((ret = buf_put_u32(msgw, rc)) != 0 ||
	    (ret = buf_put_u32(msgw, errno)) != 0) {
		ErrorLog("put_u32 failure. %s failure. %s(errno: %d)",
			 remote_name, strerror(errno), errno);
		goto return__;
	}

	if (rc < 0) {
		ErrorLog("openat %s failure. %s(errno: %d)", remote_name,
			 strerror(errno), errno);
	} else {
		if (conn->dir_fd > 0) {
			close(conn->dir_fd);
			conn->dir_fd = -1;
		}
		conn->dir_fd = rc;
		if (g_rpc_config->debug) {
			InfoLog("openat %s:%d success.", remote_name,
				remote_fd);
		}
	}

	ret = rpc_conn_send_msg(conn);
	if (ret != 0) {
		ErrorLog("rpc_conn_send_msg failure. %s failure. %s(errno: %d)",
			 remote_name, strerror(errno), errno);
		goto return__;
	}

	ret = 0;
return__:
	if (remote_name != NULL) {
		free(remote_name);
	}
	return ret;
}

int rpc_conn_srv_download_fileat(struct rpc_conn *conn)
{
	int ret = 0;
	int rc = -1;
	struct buf *msgw = conn->msgw;
	struct buf *msgr = conn->msgr;
	char *remote_name = NULL;
	int remote_fd = 0;
	uint32_t chunk_len = PREAD_CHUNK_SIZE;
	char *chunk = NULL;

	if ((ret = buf_get_u32(msgr, (uint32_t *)&remote_fd)) != 0 ||
	    (ret = buf_get_cstring(msgr, &remote_name, NULL)) != 0) {
		ErrorLog("get_cstring failure. %s(errno: %d)", strerror(errno),
			 errno);
		goto return__;
	}

	rc = openat(remote_fd, remote_name, O_RDONLY);
	if (rc < 0) {
		ErrorLog("open %s failure. %s(errno: %d)", remote_name,
			 strerror(errno), errno);

		if ((ret = buf_put_u32(msgw, rc)) != 0 ||
		    (ret = buf_put_u32(msgw, errno)) != 0) {
			ErrorLog("put_u32 failure. %s failure. %s(errno: %d)",
				 remote_name, strerror(errno), errno);
			goto return__;
		}

		ret = rpc_conn_send_msg(conn);
		if (ret != 0) {
			ErrorLog(
				"rpc_conn_send_msg failure. %s failure. %s(errno: %d)",
				remote_name, strerror(errno), errno);
			goto return__;
		}

		goto return__;
	}

	chunk = (char *)malloc(chunk_len);
	if (chunk == NULL) {
		ErrorLog("malloc failure. %s failure. %s(errno: %d)",
			 remote_name, strerror(errno), errno);
		goto return__;
	}

	while (1) {
		int n = read(rc, chunk, chunk_len);
		if ((ret = buf_put_u32(msgw, n)) != 0) {
			ErrorLog("put_u32 failure. %s failure. %s(errno: %d)",
				 remote_name, strerror(errno), errno);
			goto return__;
		}
		if (n < 0) {
			ErrorLog("pread %s failure. %s(errno: %d)", remote_name,
				 strerror(errno), errno);

			if ((ret = buf_put_u32(msgw, errno)) != 0) {
				ErrorLog(
					"put_u32 failure. %s failure. %s(errno: %d)",
					remote_name, strerror(errno), errno);
				goto return__;
			}
		} else if (n >= 0) {
			if ((ret = buf_put_string(msgw, chunk, n)) != 0) {
				ErrorLog(
					"put_u32 failure. %s failure. %s(errno: %d)",
					remote_name, strerror(errno), errno);
				goto return__;
			}
		}
		if ((ret = rpc_conn_send_msg(conn)) != 0) {
			ErrorLog(
				"rpc_conn_send_msg failure. %s failure. %s(errno: %d)",
				remote_name, strerror(errno), errno);
			goto return__;
		}

		if (n < (int)chunk_len) {
			break;
		}

		if (n <= 0) {
			break;
		}
	}

	ret = 0;
return__:
	if (remote_name) {
		free(remote_name);
	}
	if (rc >= 0) {
		close(rc);
	}
	if (chunk != NULL) {
		free(chunk);
	}
	return ret;
}

int rpc_conn_srv_readlinkat(struct rpc_conn *conn)
{
	int rc = 0;
	int ret = 0;
	struct buf *msgw = conn->msgw;
	struct buf *msgr = conn->msgr;
	int remote_fd = 0;
	char *remote_name = NULL;
	char buf[PATH_MAX];

	if ((ret = buf_get_u32(msgr, (uint32_t *)&remote_fd)) != 0 ||
	    (ret = buf_get_cstring(msgr, &remote_name, NULL)) != 0) {
		ErrorLog("buf_get_cstring failure. %s(errno: %d)",
			 strerror(errno), errno);
		goto return__;
	}

	rc = readlinkat(remote_fd, remote_name, buf, sizeof(buf) - 1);
	if ((ret = buf_put_u32(msgw, rc < 0 ? -1 : 0)) != 0 ||
	    (ret = buf_put_u32(msgw, errno)) != 0) {
		ErrorLog("put_u32 failure. %s(errno: %d)", strerror(errno),
			 errno);
		goto return__;
	}

	if (rc < 0) {
		ErrorLog("readlink %s failure. %s(errno: %d)", remote_name,
			 strerror(errno), errno);
	} else {
		if ((ret = buf_put_string(msgw, buf, rc)) != 0) {
			ErrorLog("put_string failure. %s(errno: %d)",
				 strerror(errno), errno);
			goto return__;
		}
	}

	ret = rpc_conn_send_msg(conn);
	if (ret != 0) {
		ErrorLog("rpc_conn_send_msg failure. %s(errno: %d)",
			 strerror(errno), errno);
		goto return__;
	}

return__:
	if (remote_name != NULL) {
		free(remote_name);
	}
	return ret;
}
