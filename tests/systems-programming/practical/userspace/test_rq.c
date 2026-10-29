#define _POSIX_C_SOURCE 200809L
#include "rq.h"
#include "test_support.h"

#include <errno.h>
#include <sched.h>
#include <stdatomic.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

static void count_consume(const void *data, size_t len, void *arg)
{
	unsigned int *calls = arg;

	(void)data;
	(void)len;
	if (calls)
		(*calls)++;
}

static struct rq_stats stats_of(struct rq *queue)
{
	struct rq_stats stats;

	CHECK(rq_get_stats(queue, &stats) == 0);
	return stats;
}

static void check_closed_empty(struct rq *queue)
{
	struct rq_stats stats = stats_of(queue);

	CHECK(stats.closed);
	CHECK(stats.live_items == 0);
	CHECK(stats.live_payload_bytes == 0);
}

static void check_balanced(void)
{
	CHECK(test_allocations() == 0);
	CHECK(test_threads() == 0);
}

static void test_invalid_and_create_failures(void)
{
	const enum test_failure failures[] = {
		TEST_FAIL_MALLOC, TEST_FAIL_MUTEX_INIT,
		TEST_FAIL_COND_INIT, TEST_FAIL_THREAD_CREATE
	};
	const int errors[] = { -ENOMEM, -EBUSY, -ENOMEM, -EAGAIN };
	struct rq_options options = { 1, 4, count_consume, NULL };
	struct rq *queue = (struct rq *)(uintptr_t)1;
	struct rq_stats stats;
	size_t i;

	CHECK(rq_create(&options, NULL) == -EINVAL);
	CHECK(rq_create(NULL, &queue) == -EINVAL && queue == NULL);
	options.max_items = 0;
	queue = (struct rq *)(uintptr_t)1;
	CHECK(rq_create(&options, &queue) == -EINVAL && queue == NULL);
	options.max_items = 1;
	options.max_payload_bytes = 0;
	CHECK(rq_create(&options, &queue) == -EINVAL && queue == NULL);
	options.max_payload_bytes = 4;
	options.consume = NULL;
	CHECK(rq_create(&options, &queue) == -EINVAL && queue == NULL);
	options.consume = count_consume;
	CHECK(rq_submit(NULL, NULL, 0) == -EINVAL);
	CHECK(rq_get_stats(NULL, &stats) == -EINVAL);
	CHECK(rq_close(NULL) == -EINVAL);
	rq_destroy(NULL);
	for (i = 0; i < sizeof(failures) / sizeof(failures[0]); i++) {
		queue = (struct rq *)(uintptr_t)1;
		test_fail_next(failures[i]);
		errno = ERANGE;
		CHECK(rq_create(&options, &queue) == errors[i]);
		CHECK(test_failure_consumed());
		CHECK(queue == NULL);
		check_balanced();
		CHECK(rq_create(&options, &queue) == 0);
		rq_destroy(queue);
		check_balanced();
	}
}

static void test_submit_failure_and_limits(void)
{
	unsigned int calls = 0;
	struct rq_options options = { 1, 4, count_consume, &calls };
	struct rq *queue;
	struct rq_stats stats;
	const unsigned char bytes[] = { 1, 0, 2, 0xff, 5 };
	size_t allocations_before;

	CHECK(rq_create(&options, &queue) == 0);
	CHECK(rq_get_stats(queue, NULL) == -EINVAL);
	CHECK(rq_submit(queue, NULL, 1) == -EINVAL);
	CHECK(rq_submit(queue, bytes, sizeof(bytes)) == -EMSGSIZE);
	test_fail_next(TEST_FAIL_MALLOC);
	CHECK(rq_submit(queue, bytes, 4) == -ENOMEM);
	CHECK(test_failure_consumed());
	stats = stats_of(queue);
	CHECK(stats.live_items == 0 && stats.live_payload_bytes == 0);
	CHECK(stats.peak_live_items <= 1 && stats.peak_live_payload_bytes <= 4);
	CHECK(rq_submit(queue, bytes, 4) == 0);
	CHECK(rq_close(queue) == 0);
	CHECK(calls == 1);
	check_closed_empty(queue);
	allocations_before = test_allocation_calls();
	CHECK(rq_submit(queue, bytes, 1) == -ESHUTDOWN);
	CHECK(rq_submit(queue, NULL, 0) == -ESHUTDOWN);
	CHECK(test_allocation_calls() == allocations_before);
	CHECK(rq_close(queue) == 0);
	rq_destroy(queue);
	check_balanced();

	/* Valid logical limits can still exceed representable allocation size. */
	options.max_items = SIZE_MAX;
	options.max_payload_bytes = SIZE_MAX;
	calls = 0;
	CHECK(rq_create(&options, &queue) == 0);
	allocations_before = test_allocation_calls();
	CHECK(rq_submit(queue, bytes, SIZE_MAX) == -ENOMEM);
	CHECK(test_allocation_calls() == allocations_before);
	stats = stats_of(queue);
	CHECK(stats.live_items == 0 && stats.live_payload_bytes == 0);
	CHECK(rq_submit(queue, NULL, 0) == 0);
	CHECK(rq_close(queue) == 0 && calls == 1);
	rq_destroy(queue);
}

struct sample {
	unsigned int value;
	unsigned char bytes[4];
};

struct fifo_state {
	struct test_gate gate;
	struct sample observed[3];
	size_t calls;
};

static void fifo_consume(const void *data, size_t len, void *arg)
{
	struct fifo_state *state = arg;

	CHECK(state->calls < 3);
	CHECK(len == sizeof(struct sample));
	if (state->calls == 0)
		test_gate_enter(&state->gate);
	memcpy(&state->observed[state->calls++], data, len);
}

static void test_fifo_and_owned_copy(void)
{
	struct fifo_state state = { .gate = TEST_GATE_INIT };
	struct rq_options options = {
		3, 3 * sizeof(struct sample), fifo_consume, &state
	};
	struct rq *queue;
	size_t i;

	CHECK(rq_create(&options, &queue) == 0);
	for (i = 0; i < 3; i++) {
		struct sample input = { (unsigned int)(100 + i), { 1, 0, 2, 0xff } };

		CHECK(rq_submit(queue, &input, sizeof(input)) == 0);
		if (i == 0)
			test_gate_wait(&state.gate);
		memset(&input, 0xa5, sizeof(input));
	}
	test_gate_release(&state.gate);
	CHECK(rq_close(queue) == 0);
	CHECK(state.calls == 3);
	for (i = 0; i < 3; i++) {
		const unsigned char expected[] = { 1, 0, 2, 0xff };

		CHECK(state.observed[i].value == 100 + i);
		CHECK(memcmp(state.observed[i].bytes, expected, sizeof(expected)) == 0);
	}
	check_closed_empty(queue);
	rq_destroy(queue);
	test_gate_destroy(&state.gate);
}

struct holding_state {
	struct test_gate gate;
	unsigned int calls;
};

static void holding_consume(const void *data, size_t len, void *arg)
{
	struct holding_state *state = arg;

	(void)data;
	(void)len;
	if (state->calls++ == 0)
		test_gate_enter(&state->gate);
}

static void test_inflight_item_and_byte_budgets(void)
{
	struct holding_state state = { .gate = TEST_GATE_INIT };
	struct rq_options options = { 3, 3, holding_consume, &state };
	struct rq_stats stats;
	struct rq *queue;
	const unsigned char input[] = { 1, 2, 3, 4 };
	size_t allocations_before;

	CHECK(rq_create(&options, &queue) == 0);
	CHECK(rq_submit(queue, input, 2) == 0);
	test_gate_wait(&state.gate);
	stats = stats_of(queue);
	CHECK(stats.live_items == 1 && stats.live_payload_bytes == 2);
	allocations_before = test_allocation_calls();
	CHECK(rq_submit(queue, input, 2) == -EAGAIN);
	CHECK(rq_submit(queue, input, 4) == -EMSGSIZE);
	CHECK(test_allocation_calls() == allocations_before);
	CHECK(rq_submit(queue, NULL, 0) == 0);
	stats = stats_of(queue);
	CHECK(stats.live_items == 2 && stats.live_payload_bytes == 2);
	CHECK(rq_submit(queue, input, 1) == 0);
	CHECK(rq_submit(queue, NULL, 0) == -EAGAIN);
	stats = stats_of(queue);
	CHECK(stats.live_items == 3 && stats.live_payload_bytes == 3);
	CHECK(stats.peak_live_items == 3 && stats.peak_live_payload_bytes == 3);
	test_gate_release(&state.gate);
	CHECK(rq_close(queue) == 0 && state.calls == 3);
	check_closed_empty(queue);
	rq_destroy(queue);
	test_gate_destroy(&state.gate);
}

struct close_call {
	struct rq *queue;
	pthread_mutex_t lock;
	pthread_cond_t changed;
	bool done;
	int result;
};

static void close_call_init(struct close_call *call, struct rq *queue)
{
	call->queue = queue;
	call->done = false;
	call->result = 1;
	CHECK(pthread_mutex_init(&call->lock, NULL) == 0);
	CHECK(pthread_cond_init(&call->changed, NULL) == 0);
}

static void *close_thread(void *arg)
{
	struct close_call *call = arg;
	int result = rq_close(call->queue);

	CHECK(pthread_mutex_lock(&call->lock) == 0);
	call->result = result;
	call->done = true;
	CHECK(pthread_cond_broadcast(&call->changed) == 0);
	CHECK(pthread_mutex_unlock(&call->lock) == 0);
	return NULL;
}

static void expect_close_waiting(struct close_call *call)
{
	struct timespec deadline = test_deadline(40);
	int error = 0;

	CHECK(pthread_mutex_lock(&call->lock) == 0);
	while (!call->done && !error)
		error = pthread_cond_timedwait(&call->changed, &call->lock, &deadline);
	CHECK(error == ETIMEDOUT);
	CHECK(!call->done);
	CHECK(pthread_mutex_unlock(&call->lock) == 0);
}

static void close_call_destroy(struct close_call *call)
{
	CHECK(call->done && call->result == 0);
	CHECK(pthread_cond_destroy(&call->changed) == 0);
	CHECK(pthread_mutex_destroy(&call->lock) == 0);
}

static void wait_until_closed(struct rq *queue)
{
	struct timespec deadline = test_deadline(5000);
	struct timespec now;

	while (!stats_of(queue).closed) {
		CHECK(clock_gettime(CLOCK_REALTIME, &now) == 0);
		CHECK(now.tv_sec < deadline.tv_sec ||
		      (now.tv_sec == deadline.tv_sec && now.tv_nsec < deadline.tv_nsec));
		sched_yield();
	}
}

struct reentrant_state {
	struct rq *queue;
	struct test_gate gate;
	unsigned int calls;
};

static void reentrant_consume(const void *data, size_t len, void *arg)
{
	struct reentrant_state *state = arg;
	struct rq_stats stats;
	unsigned char next = 0x7f;

	CHECK(len == 1);
	CHECK(rq_close(state->queue) == -EDEADLK);
	stats = stats_of(state->queue);
	if (state->calls++ == 0) {
		CHECK(*(const unsigned char *)data == 0x12);
		CHECK(!stats.closed && stats.live_items == 1);
		CHECK(rq_submit(state->queue, &next, 1) == 0);
		next = 0;
		CHECK(rq_submit(state->queue, &next, 1) == -EAGAIN);
		test_gate_enter(&state->gate);
	} else {
		CHECK(state->calls == 2);
		CHECK(*(const unsigned char *)data == 0x7f);
		CHECK(stats.closed);
		CHECK(rq_submit(state->queue, &next, 1) == -ESHUTDOWN);
	}
}

static void test_callback_reentry_and_self_close(void)
{
	struct reentrant_state state = { .gate = TEST_GATE_INIT };
	struct rq_options options = { 2, 2, reentrant_consume, &state };
	struct close_call closer;
	struct rq_stats stats;
	pthread_t close_id;
	unsigned char first = 0x12;

	CHECK(rq_create(&options, &state.queue) == 0);
	CHECK(rq_submit(state.queue, &first, 1) == 0);
	test_gate_wait(&state.gate);
	stats = stats_of(state.queue);
	CHECK(!stats.closed && stats.live_items == 2 && stats.live_payload_bytes == 2);
	close_call_init(&closer, state.queue);
	CHECK(pthread_create(&close_id, NULL, close_thread, &closer) == 0);
	wait_until_closed(state.queue);
	expect_close_waiting(&closer);
	test_gate_release(&state.gate);
	CHECK(pthread_join(close_id, NULL) == 0);
	close_call_destroy(&closer);
	CHECK(state.calls == 2);
	check_closed_empty(state.queue);
	CHECK(rq_close(state.queue) == 0);
	rq_destroy(state.queue);
	test_gate_destroy(&state.gate);
}

struct submit_call {
	struct rq *queue;
	enum test_pause pause;
	struct test_gate *gate;
	int result;
};

static void *paused_submit_thread(void *arg)
{
	struct submit_call *call = arg;
	uint32_t input = 0x12345678;

	test_pause_next(call->pause, call->gate);
	call->result = rq_submit(call->queue, &input, sizeof(input));
	return NULL;
}

static void test_constructor_close(enum test_pause pause)
{
	struct test_gate gate = TEST_GATE_INIT;
	unsigned int calls = 0;
	struct rq_options options = { 1, sizeof(uint32_t), count_consume, &calls };
	struct rq *queue;
	struct submit_call submitter;
	struct close_call closers[3];
	pthread_t submit_id;
	pthread_t close_ids[3];
	struct rq_stats stats;
	size_t baseline;
	size_t i;

	CHECK(rq_create(&options, &queue) == 0);
	baseline = test_allocations();
	submitter = (struct submit_call) { queue, pause, &gate, 1 };
	CHECK(pthread_create(&submit_id, NULL, paused_submit_thread, &submitter) == 0);
	test_gate_wait(&gate);
	stats = stats_of(queue);
	CHECK(stats.live_items == 1 && stats.live_payload_bytes == sizeof(uint32_t));
	if (pause == TEST_PAUSE_BEFORE_MALLOC)
		CHECK(test_allocations() == baseline);
	else
		CHECK(test_allocations() > baseline);
	CHECK(rq_submit(queue, NULL, 0) == -EAGAIN);
	for (i = 0; i < 3; i++) {
		close_call_init(&closers[i], queue);
		CHECK(pthread_create(&close_ids[i], NULL, close_thread, &closers[i]) == 0);
	}
	wait_until_closed(queue);
	CHECK(rq_submit(queue, NULL, 0) == -ESHUTDOWN);
	for (i = 0; i < 3; i++)
		expect_close_waiting(&closers[i]);
	test_gate_release(&gate);
	CHECK(pthread_join(submit_id, NULL) == 0);
	CHECK(submitter.result == -ESHUTDOWN);
	for (i = 0; i < 3; i++) {
		CHECK(pthread_join(close_ids[i], NULL) == 0);
		close_call_destroy(&closers[i]);
	}
	CHECK(calls == 0);
	CHECK(test_allocations() == baseline);
	check_closed_empty(queue);
	rq_destroy(queue);
	test_gate_destroy(&gate);
}

struct delayed_free_state {
	struct test_gate gate;
	unsigned int calls;
};

static void delayed_free_consume(const void *data, size_t len, void *arg)
{
	struct delayed_free_state *state = arg;

	CHECK(len == 4 && data != NULL);
	state->calls++;
	test_pause_next(TEST_PAUSE_BEFORE_FREE, &state->gate);
}

static void test_budget_until_real_free(void)
{
	struct delayed_free_state state = { .gate = TEST_GATE_INIT };
	struct rq_options options = { 1, 4, delayed_free_consume, &state };
	struct rq *queue;
	struct close_call closer;
	pthread_t close_id;
	struct rq_stats stats;
	uint32_t input = 42;
	size_t baseline;

	CHECK(rq_create(&options, &queue) == 0);
	baseline = test_allocations();
	CHECK(rq_submit(queue, &input, sizeof(input)) == 0);
	test_gate_wait(&state.gate);
	CHECK(test_allocations() > baseline);
	stats = stats_of(queue);
	CHECK(stats.live_items == 1 && stats.live_payload_bytes == 4);
	CHECK(rq_submit(queue, NULL, 0) == -EAGAIN);
	close_call_init(&closer, queue);
	CHECK(pthread_create(&close_id, NULL, close_thread, &closer) == 0);
	wait_until_closed(queue);
	expect_close_waiting(&closer);
	test_gate_release(&state.gate);
	CHECK(pthread_join(close_id, NULL) == 0);
	close_call_destroy(&closer);
	CHECK(state.calls == 1);
	CHECK(test_allocations() == baseline);
	check_closed_empty(queue);
	rq_destroy(queue);
	test_gate_destroy(&state.gate);
}

enum { PRODUCERS = 4, MESSAGES = 512, STRESS_ITEMS = 32 };

struct stress_message {
	unsigned int producer;
	unsigned int sequence;
	unsigned int check;
};

struct stress_state {
	struct rq *queue;
	pthread_mutex_t lock;
	pthread_barrier_t first_submitted;
	struct test_gate first_callback;
	struct test_gate observer_ready;
	bool hold_first;
	bool have_worker;
	pthread_t worker;
	unsigned int next[PRODUCERS];
	unsigned int calls;
	atomic_bool stop_observer;
};

struct producer_state {
	struct stress_state *shared;
	unsigned int id;
	unsigned int accepted;
	bool saw_shutdown;
};

static void barrier_wait(pthread_barrier_t *barrier)
{
	int error = pthread_barrier_wait(barrier);

	CHECK(error == 0 || error == PTHREAD_BARRIER_SERIAL_THREAD);
}

static void stress_consume(const void *data, size_t len, void *arg)
{
	struct stress_state *state = arg;
	struct stress_message message;
	bool hold;

	CHECK(len == sizeof(message));
	memcpy(&message, data, len);
	CHECK(message.producer < PRODUCERS && message.sequence < MESSAGES);
	CHECK(message.check == (message.producer ^ message.sequence ^ 0xa5a55a5aU));
	CHECK(pthread_mutex_lock(&state->lock) == 0);
	if (state->have_worker)
		CHECK(pthread_equal(state->worker, pthread_self()) != 0);
	else {
		state->worker = pthread_self();
		state->have_worker = true;
	}
	CHECK(message.sequence == state->next[message.producer]++);
	hold = state->hold_first && state->calls == 0;
	state->calls++;
	CHECK(pthread_mutex_unlock(&state->lock) == 0);
	if (hold)
		test_gate_enter(&state->first_callback);
}

static void *stress_producer(void *arg)
{
	struct producer_state *producer = arg;
	struct stress_state *state = producer->shared;
	unsigned int sequence;

	for (sequence = 0; sequence < MESSAGES; sequence++) {
		struct stress_message message = {
			producer->id, sequence, producer->id ^ sequence ^ 0xa5a55a5aU
		};
		int result;

		do {
			result = rq_submit(state->queue, &message, sizeof(message));
			if (result == -EAGAIN)
				sched_yield();
		} while (result == -EAGAIN);
		if (result == -ESHUTDOWN) {
			producer->saw_shutdown = true;
			return NULL;
		}
		CHECK(result == 0);
		producer->accepted++;
		memset(&message, 0, sizeof(message));
		if (sequence == 0)
			barrier_wait(&state->first_submitted);
	}
	return NULL;
}

static void validate_stress_stats(struct rq_stats stats)
{
	CHECK(stats.live_items <= STRESS_ITEMS);
	CHECK(stats.live_payload_bytes <= STRESS_ITEMS * sizeof(struct stress_message));
	CHECK(stats.peak_live_items >= stats.live_items);
	CHECK(stats.peak_live_items <= STRESS_ITEMS);
	CHECK(stats.peak_live_payload_bytes >= stats.live_payload_bytes);
	CHECK(stats.peak_live_payload_bytes <= STRESS_ITEMS * sizeof(struct stress_message));
}

static void *stress_observer(void *arg)
{
	struct stress_state *state = arg;
	bool closed_seen = false;

	validate_stress_stats(stats_of(state->queue));
	test_gate_enter(&state->observer_ready);
	while (!atomic_load(&state->stop_observer)) {
		struct rq_stats stats = stats_of(state->queue);

		validate_stress_stats(stats);
		CHECK(!closed_seen || stats.closed);
		closed_seen = stats.closed;
		sched_yield();
	}
	return NULL;
}

static void test_concurrent_producers_and_close(bool close_early)
{
	struct stress_state state = {
		.lock = PTHREAD_MUTEX_INITIALIZER,
		.first_callback = TEST_GATE_INIT,
		.observer_ready = TEST_GATE_INIT,
		.hold_first = close_early,
		.stop_observer = ATOMIC_VAR_INIT(false)
	};
	struct rq_options options = {
		STRESS_ITEMS, STRESS_ITEMS * sizeof(struct stress_message),
		stress_consume, &state
	};
	struct producer_state producers[PRODUCERS] = { 0 };
	struct close_call closers[3];
	pthread_t producer_ids[PRODUCERS];
	pthread_t close_ids[3];
	pthread_t observer_id;
	unsigned int accepted = 0;
	size_t i;

	CHECK(pthread_barrier_init(&state.first_submitted, NULL, PRODUCERS + 1) == 0);
	CHECK(rq_create(&options, &state.queue) == 0);
	CHECK(pthread_create(&observer_id, NULL, stress_observer, &state) == 0);
	test_gate_wait(&state.observer_ready);
	test_gate_release(&state.observer_ready);
	for (i = 0; i < PRODUCERS; i++) {
		producers[i].shared = &state;
		producers[i].id = (unsigned int)i;
		CHECK(pthread_create(&producer_ids[i], NULL, stress_producer, &producers[i]) == 0);
	}
	barrier_wait(&state.first_submitted);
	if (close_early) {
		test_gate_wait(&state.first_callback);
		for (i = 0; i < 3; i++) {
			close_call_init(&closers[i], state.queue);
			CHECK(pthread_create(&close_ids[i], NULL, close_thread, &closers[i]) == 0);
		}
		wait_until_closed(state.queue);
		for (i = 0; i < 3; i++)
			expect_close_waiting(&closers[i]);
		test_gate_release(&state.first_callback);
	}
	for (i = 0; i < PRODUCERS; i++) {
		CHECK(pthread_join(producer_ids[i], NULL) == 0);
		CHECK(producers[i].accepted >= 1);
		CHECK(producers[i].saw_shutdown == close_early);
		accepted += producers[i].accepted;
	}
	if (close_early) {
		for (i = 0; i < 3; i++) {
			CHECK(pthread_join(close_ids[i], NULL) == 0);
			close_call_destroy(&closers[i]);
		}
	} else {
		CHECK(accepted == PRODUCERS * MESSAGES);
		CHECK(rq_close(state.queue) == 0);
	}
	CHECK(rq_close(state.queue) == 0);
	CHECK(rq_close(state.queue) == 0);
	check_closed_empty(state.queue);
	atomic_store(&state.stop_observer, true);
	CHECK(pthread_join(observer_id, NULL) == 0);
	CHECK(state.calls == accepted);
	for (i = 0; i < PRODUCERS; i++)
		CHECK(state.next[i] == producers[i].accepted);
	rq_destroy(state.queue);
	CHECK(pthread_barrier_destroy(&state.first_submitted) == 0);
	CHECK(pthread_mutex_destroy(&state.lock) == 0);
	test_gate_destroy(&state.first_callback);
	test_gate_destroy(&state.observer_ready);
}

static void test_destroy_drains(void)
{
	unsigned int calls = 0;
	struct rq_options options = { 32, 32, count_consume, &calls };
	struct rq *queue;
	unsigned char input = 3;
	unsigned int i;

	CHECK(rq_create(&options, &queue) == 0);
	for (i = 0; i < 16; i++)
		CHECK(rq_submit(queue, &input, 1) == 0);
	rq_destroy(queue);
	CHECK(calls == 16);
}

#define RUN(test) do { \
	test; \
	check_balanced(); \
	puts("PASS " #test); \
} while (0)

int main(void)
{
	RUN(test_invalid_and_create_failures());
	RUN(test_submit_failure_and_limits());
	RUN(test_fifo_and_owned_copy());
	RUN(test_inflight_item_and_byte_budgets());
	RUN(test_callback_reentry_and_self_close());
	RUN(test_constructor_close(TEST_PAUSE_BEFORE_MALLOC));
	RUN(test_constructor_close(TEST_PAUSE_AFTER_MALLOC));
	RUN(test_budget_until_real_free());
	RUN(test_concurrent_producers_and_close(false));
	RUN(test_concurrent_producers_and_close(true));
	RUN(test_destroy_drains());
	puts("PASS all 11 C scenarios; tracked allocations=0, unjoined threads=0");
	return 0;
}
