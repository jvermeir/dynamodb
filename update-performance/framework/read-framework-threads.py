#
# Template to run a DynamoDB scan and update operation in parallel
#

import sys
import boto3
import queue
from threading import Thread
import time
from datetime import datetime

sys.path.append('../..')
from util import log

dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000/')
# use this if you've got a configuration file in ~/.aws:
# dynamodb = boto3.resource('dynamodb')
table_name = 'test_table'
total_segments = 2


def add_batch_to_queue(q, data):
    [q.put(item) for item in data]


def producer(table, q, thread_name, segment):
    batch = table.scan(
        Segment=segment,
        TotalSegments=total_segments,
    )
    data = batch['Items']
    log(f'producer: {thread_name} count: {len(data)}')
    add_batch_to_queue(q, data)

    while 'LastEvaluatedKey' in batch:
        batch = table.scan(ExclusiveStartKey=batch['LastEvaluatedKey'],
                           Segment=segment,
                           TotalSegments=total_segments,
                           )
        data = batch['Items']
        log(f'producer: {thread_name} count: {len(data)}')
        add_batch_to_queue(q, data)


def consumer(table, q, thread_name, update_function):
    i = 0
    with table.batch_writer() as batch:
        while 1:
            item = q.get()
            i += 1
            if i % 1000 == 0:
                log(f'thread_name: {thread_name}, count: {i}')

            update_function(item)

            batch.put_item(
                Item=item
            )


def waiter(q):
    log('waiter start sleeping')
    time.sleep(1)
    while not q.empty():
        log('sleeping')
        time.sleep(1)
    log('done')


def update(number_of_producers, number_of_consumers, table_name, update_function):
    table = dynamodb.Table(table_name)
    q = queue.Queue(maxsize=5_000)
    producers = []
    consumers = []

    for i in range(number_of_consumers):
        thread_name = f'consumer-{i}'
        thread = Thread(target=consumer, name=thread_name, args=(table, q, thread_name, update_function), daemon=True)
        consumers.append(thread)
        thread.start()

    for i in range(number_of_producers):
        thread_name = f'producer-{i}'
        thread = Thread(target=producer, name=thread_name, args=(table, q, thread_name, i,), daemon=True)
        producers.append(thread)
        thread.start()

    [i.join() for i in producers]

    log('producers finished, waiting for consumers')
    waiter_thread = Thread(target=waiter, name='waiter', args=(q,), daemon=True)
    waiter_thread.start()
    waiter_thread.join()


# This where our business logic lives. In this case,
# we increment a counter on each item.
def update_item(item):
    if 'update_count' in item:
        item['update_count'] = item['update_count'] + 1
    else:
        item['update_count'] = 1
    return item


if __name__ == '__main__':
    log('start - queue solution')
    start_time = datetime.utcnow()
    number_of_producers = total_segments
    number_of_consumers = 10
    update(number_of_producers, number_of_consumers, table_name, update_item)
    end_time = datetime.utcnow()
    log(f'end - threads and queues, elapsed time: {str(end_time - start_time)}')
