#include "rq.h"

#include <errno.h>
#include <pthread.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

struct rq_message {
	struct rq_message *next;
	size_t len;
	unsigned char data[];
};

struct rq {
	struct rq_options options;
	pthread_t worker;
	pthread_mutex_t lock;
	pthread_cond_t changed;
	struct rq_message *head;
	struct rq_message *tail;
	struct rq_stats stats;
};

/*
 * lock protects links and the entire stats snapshot. live_items includes every
 * reserved constructor, queued message, callback and not-yet-freed allocation.
 * Consequently live_items == 0 also proves all constructors have converged;
 * a separate submitter reference count is unnecessary under the destroy contract.
 */
static void release_budget(struct rq *queue, size_t len)
{
	queue->stats.live_items--;
	queue->stats.live_payload_bytes -= len;
	pthread_cond_broadcast(&queue->changed);
}

static void *consume_messages(void *arg)
{
	struct rq *queue = arg;

	pthread_mutex_lock(&queue->lock);
	for (;;) {
		struct rq_message *message;
		size_t len;

		while (!queue->head && !queue->stats.closed)
			pthread_cond_wait(&queue->changed, &queue->lock);
		if (!queue->head)
			break;
		message = queue->head;
		queue->head = message->next;
		if (!queue->head)
			queue->tail = NULL;
		pthread_mutex_unlock(&queue->lock);

		/* The worker now exclusively owns this message, still charged. */
		len = message->len;
		queue->options.consume(message->data, len, queue->options.arg);
		free(message);

		pthread_mutex_lock(&queue->lock);
		release_budget(queue, len);
	}
	pthread_mutex_unlock(&queue->lock);
	return NULL;
}

int rq_create(const struct rq_options *options, struct rq **out)
{
	struct rq *queue;
	int error;

	if (!out)
		return -EINVAL;
	*out = NULL;
	if (!options || !options->max_items || !options->max_payload_bytes ||
	    !options->consume)
		return -EINVAL;
	queue = malloc(sizeof(*queue));
	if (!queue)
		return -ENOMEM;
	memset(queue, 0, sizeof(*queue));
	queue->options = *options;
	error = pthread_mutex_init(&queue->lock, NULL);
	if (error)
		goto out_free;
	error = pthread_cond_init(&queue->changed, NULL);
	if (error)
		goto out_mutex;
	error = pthread_create(&queue->worker, NULL, consume_messages, queue);
	if (error)
		goto out_cond;
	*out = queue;
	return 0;

out_cond:
	pthread_cond_destroy(&queue->changed);
out_mutex:
	pthread_mutex_destroy(&queue->lock);
out_free:
	free(queue);
	return -error;
}

int rq_submit(struct rq *queue, const void *data, size_t len)
{
	struct rq_message *message;
	int result;

	if (!queue || (len && !data))
		return -EINVAL;
	if (len > queue->options.max_payload_bytes)
		return -EMSGSIZE;
	pthread_mutex_lock(&queue->lock);
	if (queue->stats.closed) {
		pthread_mutex_unlock(&queue->lock);
		return -ESHUTDOWN;
	}
	if (queue->stats.live_items == queue->options.max_items ||
	    len > queue->options.max_payload_bytes - queue->stats.live_payload_bytes) {
		pthread_mutex_unlock(&queue->lock);
		return -EAGAIN;
	}
	queue->stats.live_items++;
	queue->stats.live_payload_bytes += len;
	if (queue->stats.live_items > queue->stats.peak_live_items)
		queue->stats.peak_live_items = queue->stats.live_items;
	if (queue->stats.live_payload_bytes > queue->stats.peak_live_payload_bytes)
		queue->stats.peak_live_payload_bytes = queue->stats.live_payload_bytes;
	pthread_mutex_unlock(&queue->lock);

	/* Reserve before allocation, including this lock-free construction phase. */
	if (len > SIZE_MAX - sizeof(*message)) {
		result = -ENOMEM;
		goto out_release;
	}
	message = malloc(sizeof(*message) + len);
	if (!message) {
		result = -ENOMEM;
		goto out_release;
	}
	message->next = NULL;
	message->len = len;
	if (len)
		memcpy(message->data, data, len);

	pthread_mutex_lock(&queue->lock);
	if (!queue->stats.closed) {
		/* Successful submit linearizes here, transferring unique ownership. */
		if (queue->tail)
			queue->tail->next = message;
		else
			queue->head = message;
		queue->tail = message;
		pthread_cond_signal(&queue->changed);
		pthread_mutex_unlock(&queue->lock);
		return 0;
	}
	pthread_mutex_unlock(&queue->lock);
	free(message);
	result = -ESHUTDOWN;

out_release:
	/* No allocated data remains when its budget becomes reusable. */
	pthread_mutex_lock(&queue->lock);
	release_budget(queue, len);
	pthread_mutex_unlock(&queue->lock);
	return result;
}

int rq_get_stats(struct rq *queue, struct rq_stats *out)
{
	if (!queue || !out)
		return -EINVAL;
	pthread_mutex_lock(&queue->lock);
	*out = queue->stats;
	pthread_mutex_unlock(&queue->lock);
	return 0;
}

int rq_close(struct rq *queue)
{
	if (!queue)
		return -EINVAL;
	/* Check before changing admission, even if another closer already ran. */
	if (pthread_equal(pthread_self(), queue->worker))
		return -EDEADLK;
	pthread_mutex_lock(&queue->lock);
	queue->stats.closed = true;
	pthread_cond_broadcast(&queue->changed);
	while (queue->stats.live_items)
		pthread_cond_wait(&queue->changed, &queue->lock);
	pthread_mutex_unlock(&queue->lock);
	return 0;
}

void rq_destroy(struct rq *queue)
{
	if (!queue)
		return;
	/* The owner has already excluded all other public API callers. */
	if (rq_close(queue))
		return;
	if (pthread_join(queue->worker, NULL))
		return;
	pthread_cond_destroy(&queue->changed);
	pthread_mutex_destroy(&queue->lock);
	free(queue);
}
