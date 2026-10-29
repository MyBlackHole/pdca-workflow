#include "rq.h"
#include <assert.h>
#include <errno.h>
#include <pthread.h>
#include <sched.h>
#include <stdio.h>
#include <string.h>

struct blocked {
	struct rq *queue;
	pthread_mutex_t lock;
	pthread_cond_t changed;
	int entered;
	int release;
	int close_started;
	int close_returned;
};
static void checked(int rc) { assert(rc == 0); }
static void consume_blocked(const void *data, size_t len, void *arg)
{
	struct blocked *s = arg;
	struct rq_stats stats;
	unsigned value = 0;
	assert(len == sizeof(value));
	memcpy(&value, data, sizeof(value));
	assert(value == 73);
	assert(rq_get_stats(s->queue, &stats) == 0);
	assert(stats.live_items == 1);
	assert(stats.live_payload_bytes == sizeof(value));
	assert(rq_submit(s->queue, &value, sizeof(value)) == -EAGAIN);
	assert(rq_close(s->queue) == -EDEADLK);
	checked(pthread_mutex_lock(&s->lock));
	s->entered = 1;
	checked(pthread_cond_broadcast(&s->changed));
	while (!s->release)
		checked(pthread_cond_wait(&s->changed, &s->lock));
	checked(pthread_mutex_unlock(&s->lock));
}
static void *close_thread(void *arg)
{
	struct blocked *s = arg;
	checked(pthread_mutex_lock(&s->lock));
	s->close_started++;
	checked(pthread_cond_broadcast(&s->changed));
	checked(pthread_mutex_unlock(&s->lock));
	assert(rq_close(s->queue) == 0);
	checked(pthread_mutex_lock(&s->lock));
	s->close_returned++;
	checked(pthread_cond_broadcast(&s->changed));
	checked(pthread_mutex_unlock(&s->lock));
	return NULL;
}
static void inflight_and_close(void)
{
	struct blocked s = {0};
	struct rq_options o = {1, sizeof(unsigned), consume_blocked, &s};
	struct rq_stats stats;
	pthread_t closer[2];
	unsigned value = 73;
	checked(pthread_mutex_init(&s.lock, NULL));
	checked(pthread_cond_init(&s.changed, NULL));
	assert(rq_create(&o, &s.queue) == 0);
	assert(rq_submit(s.queue, &value, sizeof(value)) == 0);
	checked(pthread_mutex_lock(&s.lock));
	while (!s.entered)
		checked(pthread_cond_wait(&s.changed, &s.lock));
	checked(pthread_mutex_unlock(&s.lock));
	assert(rq_get_stats(s.queue, &stats) == 0);
	assert(!stats.closed);
	assert(stats.live_items == 1 && stats.live_payload_bytes == sizeof(value));
	assert(rq_submit(s.queue, &value, sizeof(value)) == -EAGAIN);
	assert(rq_submit(s.queue, &value, sizeof(value) + 1) == -EMSGSIZE);
	checked(pthread_create(&closer[0], NULL, close_thread, &s));
	checked(pthread_create(&closer[1], NULL, close_thread, &s));
	checked(pthread_mutex_lock(&s.lock));
	while (s.close_started != 2)
		checked(pthread_cond_wait(&s.changed, &s.lock));
	checked(pthread_mutex_unlock(&s.lock));
	do {
		assert(rq_get_stats(s.queue, &stats) == 0);
		if (!stats.closed)
			sched_yield();
	} while (!stats.closed);
	assert(rq_submit(s.queue, &value, sizeof(value)) == -ESHUTDOWN);
	checked(pthread_mutex_lock(&s.lock));
	assert(s.close_returned == 0);
	s.release = 1;
	checked(pthread_cond_broadcast(&s.changed));
	checked(pthread_mutex_unlock(&s.lock));
	checked(pthread_join(closer[0], NULL));
	checked(pthread_join(closer[1], NULL));
	assert(rq_close(s.queue) == 0);
	assert(rq_get_stats(s.queue, &stats) == 0);
	assert(stats.closed && !stats.live_items && !stats.live_payload_bytes);
	assert(stats.peak_live_items <= 1);
	assert(stats.peak_live_payload_bytes <= sizeof(value));
	rq_destroy(s.queue);
	checked(pthread_cond_destroy(&s.changed));
	checked(pthread_mutex_destroy(&s.lock));
}

enum { PRODUCERS = 4, ATTEMPTS = 100, REQUESTS = PRODUCERS * ATTEMPTS };
struct mass {
	struct rq *queue;
	pthread_mutex_t lock;
	pthread_cond_t changed;
	int ready;
	int first_done;
	int start;
	int finish;
	unsigned seen[REQUESTS];
	unsigned accepted[REQUESTS];
};
struct producer { struct mass *state; unsigned number; };
static void consume_mass(const void *data, size_t len, void *arg)
{
	struct mass *s = arg;
	unsigned id;
	assert(len == sizeof(id));
	memcpy(&id, data, sizeof(id));
	assert(id < REQUESTS);
	checked(pthread_mutex_lock(&s->lock));
	s->seen[id]++;
	checked(pthread_mutex_unlock(&s->lock));
}
static void one_submit(struct producer *p, unsigned slot)
{
	struct mass *s = p->state;
	unsigned id = p->number * ATTEMPTS + slot;
	int rc = rq_submit(s->queue, &id, sizeof(id));
	assert(rc == 0 || rc == -EAGAIN || rc == -ESHUTDOWN);
	s->accepted[id] = (rc == 0);
}
static void *produce(void *arg)
{
	struct producer *p = arg;
	struct mass *s = p->state;
	checked(pthread_mutex_lock(&s->lock));
	s->ready++;
	checked(pthread_cond_broadcast(&s->changed));
	while (!s->start)
		checked(pthread_cond_wait(&s->changed, &s->lock));
	checked(pthread_mutex_unlock(&s->lock));
	one_submit(p, 0);
	checked(pthread_mutex_lock(&s->lock));
	s->first_done++;
	checked(pthread_cond_broadcast(&s->changed));
	while (!s->finish)
		checked(pthread_cond_wait(&s->changed, &s->lock));
	checked(pthread_mutex_unlock(&s->lock));
	for (unsigned i = 1; i < ATTEMPTS; i++)
		one_submit(p, i);
	return NULL;
}
static void producers_and_stop(void)
{
	struct mass s = {0};
	struct rq_options o = {8, 8 * sizeof(unsigned), consume_mass, &s};
	struct rq_stats stats;
	pthread_t threads[PRODUCERS];
	struct producer p[PRODUCERS];
	unsigned accepted = 0;
	checked(pthread_mutex_init(&s.lock, NULL));
	checked(pthread_cond_init(&s.changed, NULL));
	assert(rq_create(&o, &s.queue) == 0);
	for (unsigned i = 0; i < PRODUCERS; i++) {
		p[i].state = &s;
		p[i].number = i;
		checked(pthread_create(&threads[i], NULL, produce, &p[i]));
	}
	checked(pthread_mutex_lock(&s.lock));
	while (s.ready != PRODUCERS)
		checked(pthread_cond_wait(&s.changed, &s.lock));
	s.start = 1;
	checked(pthread_cond_broadcast(&s.changed));
	while (s.first_done != PRODUCERS)
		checked(pthread_cond_wait(&s.changed, &s.lock));
	s.finish = 1;
	checked(pthread_cond_broadcast(&s.changed));
	checked(pthread_mutex_unlock(&s.lock));
	assert(rq_close(s.queue) == 0);
	for (unsigned i = 0; i < PRODUCERS; i++)
		checked(pthread_join(threads[i], NULL));
	for (unsigned i = 0; i < REQUESTS; i++) {
		assert(s.seen[i] == s.accepted[i]);
		accepted += s.accepted[i];
	}
	assert(accepted >= PRODUCERS);
	assert(rq_get_stats(s.queue, &stats) == 0);
	assert(!stats.live_items && !stats.live_payload_bytes);
	assert(stats.peak_live_items <= o.max_items);
	assert(stats.peak_live_payload_bytes <= o.max_payload_bytes);
	rq_destroy(s.queue);
	checked(pthread_cond_destroy(&s.changed));
	checked(pthread_mutex_destroy(&s.lock));
}
int main(void)
{
	inflight_and_close();
	producers_and_stop();
	puts("parent public-API checks: passed");
	return 0;
}
