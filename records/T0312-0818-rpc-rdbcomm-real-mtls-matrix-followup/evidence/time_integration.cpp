#include <cassert>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <sys/wait.h>
#include <sys/stat.h>
#include <unistd.h>

static int run_client(const char *path, const char *port, const char *cmd)
{
	pid_t pid = fork();
	if (pid == 0) {
		if (std::strcmp(cmd, "time") == 0)
			execl(path, path, "time", "-h", "127.0.0.1", "-p", port,
			      nullptr);
		execl(path, path, "-h", "127.0.0.1", "-p", port,
		      "-c", cmd, nullptr);
		_exit(127);
	}
	if (pid < 0)
		return -1;
	int status = 0;
	if (waitpid(pid, &status, 0) < 0 || !WIFEXITED(status))
		return -1;
	return WEXITSTATUS(status);
}

int main()
{
	const char *root = std::getenv("AIO_PROJECT_ROOT");
	assert(root != nullptr);
	char server[1024], client[1024];
	const char *port = "17622";
	std::snprintf(server, sizeof(server), "%.900s/build/linux/x86_64/debug/aio-speedd", root);
	std::snprintf(client, sizeof(client), "%.900s/build/linux/x86_64/debug/aio-speed", root);
	mkdir("/tmp/t0312-rpc-time", 0755);
	pid_t server_pid = fork();
	if (server_pid == 0) {
		execl(server, server, "-p", port, "--log-path", "/tmp/t0312-rpc-time",
		      "--audit-dir", "/tmp/t0312-rpc-time", "--work-dir",
		      "/tmp/t0312-rpc-time", nullptr);
		_exit(127);
	}
	assert(server_pid > 0);
	usleep(500000);
	assert(run_client(client, port, "time") == 0);
	assert(run_client(client, port, "true") == 0);
	kill(server_pid, SIGTERM);
	waitpid(server_pid, nullptr, 0);
	puts("rpc_time_integration: PASS");
	return 0;
}
