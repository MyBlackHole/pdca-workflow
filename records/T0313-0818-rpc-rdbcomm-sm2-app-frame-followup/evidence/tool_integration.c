#define _GNU_SOURCE

#include <assert.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>

static int run_command(const char *command)
{
	int status = system(command);
	return status == 0 ? 0 : -1;
}

static int make_certs(const char *root, const char *tls_keygen)
{
	char command[4096];
	char ca[512], server[512], client_a[512], client_b[512];
	snprintf(ca, sizeof(ca), "%s/ca", root);
	snprintf(server, sizeof(server), "%s/server", root);
	snprintf(client_a, sizeof(client_a), "%s/client-a", root);
	snprintf(client_b, sizeof(client_b), "%s/client-b", root);

	snprintf(command, sizeof(command), "'%s' ca -n 'Test CA' -o '%s' -f",
		 tls_keygen, ca);
	if (run_command(command) != 0)
		return -1;
	snprintf(command, sizeof(command), "'%s' create -n Server -o '%s' -f",
		 tls_keygen, server);
	if (run_command(command) != 0)
		return -1;
	snprintf(command, sizeof(command),
		 "'%s' sign --purpose server --ca-cert '%s/ca.crt' "
		 "--ca-key '%s/ca.key' --key '%s/host.key' --csr '%s/host.csr' "
		 "--out '%s/server.crt' -f",
		tls_keygen, ca, ca, server, server, server);
	if (run_command(command) != 0)
		return -1;
	snprintf(command, sizeof(command), "'%s' create -n ClientA -o '%s' -f",
		 tls_keygen, client_a);
	if (run_command(command) != 0)
		return -1;
	snprintf(command, sizeof(command),
		 "'%s' sign --purpose client --ca-cert '%s/ca.crt' "
		 "--ca-key '%s/ca.key' --key '%s/host.key' --csr '%s/host.csr' "
		 "--out '%s/client.crt' -f",
		tls_keygen, ca, ca, client_a, client_a, client_a);
	if (run_command(command) != 0)
		return -1;
	snprintf(command, sizeof(command), "'%s' create -n ClientB -o '%s' -f",
		 tls_keygen, client_b);
	if (run_command(command) != 0)
		return -1;
	snprintf(command, sizeof(command),
		 "'%s' sign --purpose client --ca-cert '%s/ca.crt' "
		 "--ca-key '%s/ca.key' --key '%s/host.key' --csr '%s/host.csr' "
		 "--out '%s/client.crt' -f",
		tls_keygen, ca, ca, client_b, client_b, client_b);
	return run_command(command);
}

static int make_sm2_certs(const char *root, const char *tls_keygen)
{
	char command[4096];
	char ca[512], server[512], client[512];
	snprintf(ca, sizeof(ca), "%s/sm2/ca", root);
	snprintf(server, sizeof(server), "%s/sm2/server", root);
	snprintf(client, sizeof(client), "%s/sm2/client", root);
	snprintf(command, sizeof(command),
		 "'%s' ca -n 'SM2 Test CA' -o '%s' -a sm2 -f",
		tls_keygen, ca);
	if (run_command(command) != 0)
		return -1;
	snprintf(command, sizeof(command),
		 "'%s' create -n Server -o '%s' -a sm2 -f",
		tls_keygen, server);
	if (run_command(command) != 0)
		return -1;
	snprintf(command, sizeof(command),
		 "'%s' sign --purpose server --algo sm2 --ca-cert '%s/ca.crt' "
		 "--ca-key '%s/ca.key' --key '%s/host.key' --csr '%s/host.csr' "
		 "--out '%s/server.crt' -f",
		tls_keygen, ca, ca, server, server, server);
	if (run_command(command) != 0)
		return -1;
	snprintf(command, sizeof(command),
		 "'%s' create -n Client -o '%s' -a sm2 -f",
		tls_keygen, client);
	if (run_command(command) != 0)
		return -1;
	snprintf(command, sizeof(command),
		 "'%s' sign --purpose client --algo sm2 --ca-cert '%s/ca.crt' "
		 "--ca-key '%s/ca.key' --key '%s/host.key' --csr '%s/host.csr' "
		 "--out '%s/client.crt' -f",
		tls_keygen, ca, ca, client, client, client);
	return run_command(command);
}

static int prepare_client_dir(const char *root, const char *cert_root,
				      const char *client_base)
{
	char dir[2048], source[2048], target[2048];
	snprintf(dir, sizeof(dir), "%s/Test CA", cert_root);
	if (mkdir(cert_root, 0755) != 0 && access(cert_root, F_OK) != 0)
		return -1;
	if (mkdir(dir, 0755) != 0 && access(dir, F_OK) != 0)
		return -1;
	snprintf(source, sizeof(source), "%s/client.crt", client_base);
	snprintf(target, sizeof(target), "%.2000s/host.crt", dir);
	if (symlink(source, target) != 0)
		return -1;
	snprintf(source, sizeof(source), "%s/host.key", client_base);
	snprintf(target, sizeof(target), "%.2000s/host.key", dir);
	if (symlink(source, target) != 0)
		return -1;
	snprintf(source, sizeof(source), "%s/ca.crt", root);
	snprintf(target, sizeof(target), "%.2000s/ca.crt", dir);
	return symlink(source, target) == 0 ? 0 : -1;
}

static int link_file(const char *source, const char *target)
{
	return symlink(source, target) == 0 ? 0 : -1;
}

static int run_client(const char *client, const char *port, const char *command,
			      int expect_success, const char *cert_dir,
			      const char *ciphers, int tls_enabled)
{
	pid_t child = fork();
	int status;
	if (child == 0) {
		if (cert_dir)
			setenv("RPC_TLS_CERT_DIR", cert_dir, 1);
		if (!tls_enabled)
			setenv("RPC_TLS_ENABLE", "0", 1);
		if (ciphers)
			setenv("RPC_TLS_CIPHERSUITES", ciphers, 1);
		if (!strcmp(command, "time"))
			execl(client, client, "time", "-h", "127.0.0.1", "-p", port,
			      NULL);
		execl(client, client, "-h", "127.0.0.1", "-p", port, "-c",
		      command, NULL);
		_exit(127);
	}
	if (child < 0 || waitpid(child, &status, 0) < 0 || !WIFEXITED(status))
		return -1;
	return (WEXITSTATUS(status) == 0) == expect_success ? 0 : -1;
}

static int run_case(const char *root, int tls, int client_tls, int port,
			    const char *client_cert_dir, const char *client_ciphers,
			    const char *server_ca, const char *server_cert,
			    const char *server_key, const char *ca_cn,
			    const char *server_ciphers, const char *server_cert_dir,
			    int expect_app_success)
{
	char work[160], log[200], server[512], client[512], port_s[16];
	pid_t server_pid;
	int status, result = -1;
	snprintf(work, sizeof(work), "/tmp/rdbcomm-tool-test-%d", port);
	snprintf(log, sizeof(log), "%s/log", work);
	snprintf(server, sizeof(server), "%s/build/linux/x86_64/debug/rdbcommd", root);
	snprintf(client, sizeof(client), "%s/build/linux/x86_64/debug/rdbcomm", root);
	snprintf(port_s, sizeof(port_s), "%d", port);
	mkdir(work, 0755);
	mkdir(log, 0755);
	if (tls) {
		setenv("RPC_TLS_ENABLE", "1", 1);
		setenv("RPC_TLS_CA_CERT", server_ca, 1);
		setenv("RPC_TLS_SERVER_CERT", server_cert, 1);
		setenv("RPC_TLS_SERVER_KEY", server_key, 1);
		setenv("RPC_TLS_CA_CN", ca_cn, 1);
		setenv("RPC_TLS_CERT_DIR", server_cert_dir, 1);
		if (server_ciphers)
			setenv("RPC_TLS_CIPHERSUITES", server_ciphers, 1);
		else
			unsetenv("RPC_TLS_CIPHERSUITES");
	} else {
		unsetenv("RPC_TLS_ENABLE");
		unsetenv("RPC_TLS_CA_CN");
		unsetenv("RPC_TLS_CIPHERSUITES");
	}
	server_pid = fork();
	if (server_pid == 0) {
		execl(server, server, "-h", "127.0.0.1", "-p", port_s,
		      "-l", log, "-a", log, "-w", work, NULL);
		_exit(127);
	}
	if (server_pid < 0)
		return -1;
	usleep(300000);
		if (run_client(client, port_s, "time", 1, client_cert_dir,
			       client_ciphers, client_tls) != 0)
		goto done;
	if (run_client(client, port_s, "true", expect_app_success,
			       client_cert_dir, client_ciphers, client_tls) != 0)
		goto done;
	result = 0;
done:
	kill(server_pid, SIGTERM);
	waitpid(server_pid, &status, 0);
	return result;
}

int main(void)
{
	char root[512], tls_keygen[1024], client_dir[1024];
	char sm2_dir[1024], sm2_client_dir[2048], sm2_source[1024];
	char sm2_ca[1024], sm2_server[1024], sm2_client[1024];
	const char *configured_root = getenv("AIO_PROJECT_ROOT");
	if (configured_root)
		snprintf(root, sizeof(root), "%s", configured_root);
	else
		assert(getcwd(root, sizeof(root)) != NULL);
	snprintf(tls_keygen, sizeof(tls_keygen),
		 "%s/build/linux/x86_64/debug/tls-keygen", root);
	run_command("rm -rf /tmp/t0312-rdbcomm");
	assert(mkdir("/tmp/t0312-rdbcomm", 0755) == 0);
	assert(make_certs("/tmp/t0312-rdbcomm", tls_keygen) == 0);
	assert(make_sm2_certs("/tmp/t0312-rdbcomm", tls_keygen) == 0);
	snprintf(client_dir, sizeof(client_dir), "%s/client-certs/",
		 "/tmp/t0312-rdbcomm");
	assert(prepare_client_dir("/tmp/t0312-rdbcomm/ca", client_dir,
					 "/tmp/t0312-rdbcomm/client-a") == 0);
	snprintf(sm2_dir, sizeof(sm2_dir), "%s/sm2-certs/", "/tmp/t0312-rdbcomm");
	snprintf(sm2_client_dir, sizeof(sm2_client_dir), "%sSM2 Test CA", sm2_dir);
	snprintf(sm2_ca, sizeof(sm2_ca), "%s/sm2/ca", "/tmp/t0312-rdbcomm");
	snprintf(sm2_server, sizeof(sm2_server), "%s/sm2/server", "/tmp/t0312-rdbcomm");
	snprintf(sm2_client, sizeof(sm2_client), "%s/sm2/client", "/tmp/t0312-rdbcomm");
	assert(mkdir(sm2_dir, 0755) == 0);
	assert(mkdir(sm2_client_dir, 0755) == 0);
	snprintf(sm2_source, sizeof(sm2_source), "%.1000s/ca.crt", sm2_ca);
	assert(link_file(sm2_source, "/tmp/t0312-rdbcomm/sm2-certs/ca.crt") == 0);
	assert(link_file(sm2_source, "/tmp/t0312-rdbcomm/sm2-certs/sm2_ca.crt") == 0);
	snprintf(sm2_source, sizeof(sm2_source), "%.1000s/server.crt", sm2_server);
	assert(link_file(sm2_source, "/tmp/t0312-rdbcomm/sm2-certs/sm2_host.crt") == 0);
	snprintf(sm2_source, sizeof(sm2_source), "%.1000s/host.key", sm2_server);
	assert(link_file(sm2_source, "/tmp/t0312-rdbcomm/sm2-certs/sm2_host.key") == 0);
	snprintf(sm2_source, sizeof(sm2_source), "%.1000s/ca.crt", sm2_ca);
	assert(link_file(sm2_source, "/tmp/t0312-rdbcomm/sm2-certs/SM2 Test CA/ca.crt") == 0);
	assert(link_file(sm2_source, "/tmp/t0312-rdbcomm/sm2-certs/SM2 Test CA/sm2_ca.crt") == 0);
	snprintf(sm2_source, sizeof(sm2_source), "%.1000s/client.crt", sm2_client);
	assert(link_file(sm2_source, "/tmp/t0312-rdbcomm/sm2-certs/SM2 Test CA/host.crt") == 0);
	snprintf(sm2_source, sizeof(sm2_source), "%.1000s/host.key", sm2_client);
	assert(link_file(sm2_source, "/tmp/t0312-rdbcomm/sm2-certs/SM2 Test CA/host.key") == 0);
	snprintf(sm2_source, sizeof(sm2_source), "%.1000s/server.crt", sm2_server);
	assert(link_file(sm2_source, "/tmp/t0312-rdbcomm/sm2-certs/SM2 Test CA/sm2_host.crt") == 0);
	snprintf(sm2_source, sizeof(sm2_source), "%.1000s/host.key", sm2_server);
	assert(link_file(sm2_source, "/tmp/t0312-rdbcomm/sm2-certs/SM2 Test CA/sm2_host.key") == 0);
	assert(run_case(root, 0, 0, 17610, NULL, NULL, NULL, NULL, NULL, NULL,
			       NULL, NULL, 1) == 0);
	assert(run_case(root, 1, 1, 17611, client_dir, NULL,
			       "/tmp/t0312-rdbcomm/ca/ca.crt",
			       "/tmp/t0312-rdbcomm/server/server.crt",
			       "/tmp/t0312-rdbcomm/server/host.key", "Test CA", NULL,
			       client_dir, 1) == 0);
	assert(run_case(root, 1, 1, 17612, client_dir, "TLS_SM4_GCM_SM3",
			       "/tmp/t0312-rdbcomm/ca/ca.crt",
			       "/tmp/t0312-rdbcomm/server/server.crt",
			       "/tmp/t0312-rdbcomm/server/host.key", "Test CA", NULL,
			       client_dir, 0) == 0);
	assert(run_case(root, 1, 1, 17613, "/tmp/t0312-rdbcomm/missing-certs/", NULL,
			       "/tmp/t0312-rdbcomm/ca/ca.crt",
			       "/tmp/t0312-rdbcomm/server/server.crt",
			       "/tmp/t0312-rdbcomm/server/host.key", "Test CA", NULL,
			       "/tmp/t0312-rdbcomm/missing-certs/", 0) == 0);
	/* SM2 must complete the same application-frame path as classic mTLS. */
	assert(run_case(root, 1, 1, 17614, sm2_dir, "TLS_SM4_GCM_SM3",
			       "/tmp/t0312-rdbcomm/sm2-certs/ca.crt",
			       "/tmp/t0312-rdbcomm/sm2-certs/sm2_host.crt",
			       "/tmp/t0312-rdbcomm/sm2-certs/sm2_host.key",
			       "SM2 Test CA", "TLS_SM4_GCM_SM3", sm2_dir, 1) == 0);
	assert(run_case(root, 1, 0, 17615, NULL, NULL,
			       "/tmp/t0312-rdbcomm/ca/ca.crt",
			       "/tmp/t0312-rdbcomm/server/server.crt",
			       "/tmp/t0312-rdbcomm/server/host.key", "Test CA", NULL,
			       client_dir, 0) == 0);
	puts("rdbcomm_tool_integration: PASS");
	return 0;
}
