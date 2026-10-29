#include "rq.h"

#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

struct callback_state {
	struct rq *queue;
	unsigned int calls;
};

static void consume(const void *data, size_t len, void *arg)
{
	struct callback_state *state = (struct callback_state *)arg;
	const unsigned char expected[] = { 0x12, 0, 0x34, 0xff };
	struct rq_stats stats;

	assert(len == sizeof(expected));
	assert(memcmp(data, expected, len) == 0);
	assert(rq_get_stats(state->queue, &stats) == 0);
	assert(stats.live_items == 1);
	assert(stats.live_payload_bytes == sizeof(expected));
	state->calls++;
}

int main(void)
{
	struct callback_state state = { NULL, 0 };
	struct rq_options options = { 2, 16, consume, &state };
	struct rq_stats stats;
	unsigned char input[] = { 0x12, 0, 0x34, 0xff };

	assert(rq_create(&options, &state.queue) == 0);
	assert(rq_submit(state.queue, input, sizeof(input)) == 0);
	memset(input, 0xa5, sizeof(input));
	assert(rq_close(state.queue) == 0);
	assert(rq_close(state.queue) == 0);
	assert(state.calls == 1);
	assert(rq_get_stats(state.queue, &stats) == 0);
	assert(stats.closed && stats.live_items == 0);
	assert(stats.live_payload_bytes == 0);
	rq_destroy(state.queue);
	puts("PASS C++ caller: C ABI, binary copy, close, stats");
	return 0;
}
