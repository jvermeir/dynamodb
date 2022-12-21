#
# Insert records into table
#
# inspired by: https://python.plainenglish.io/using-python-to-create-a-dynamodb-table-56ed01fa3a10
# and https://boto3.amazonaws.com/v1/documentation/api/latest/guide/dynamodb.html

import sys
import boto3
import queue

sys.path.append('..')

from util import log
from threading import Thread
import time

dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000/')
# use this if you've got a configuration file in ~/.aws: dynamodb = boto3.resource('dynamodb')
table_name = 'test_table'


def add_batch_to_queue(q, data):
    [q.put(item) for item in data]


def producer_thread(q, thread_name, segment):
    batch = table.scan(
        Segment=segment,
        TotalSegments=2,
    )
    data = batch['Items']
    log('producer: ' + thread_name + ' count: ' + str(len(data)))
    add_batch_to_queue(q, data)

    while 'LastEvaluatedKey' in batch:
        batch = table.scan(ExclusiveStartKey=batch['LastEvaluatedKey'],
                           Segment=segment,
                           TotalSegments=2,
                           )
        data = batch['Items']
        log('producer: ' + thread_name + ' count: ' + str(len(data)))
        add_batch_to_queue(q, data)


def consumer_thread(table, q, thread_name):
    i = 0
    with table.batch_writer() as batch:
        while 1:
            item = q.get()
            i = i + 1
            if i % 1000 == 0:
                log('thread_name: ' + thread_name + ', count: ' + str(i))
            if 'update_count' in item:
                item['update_count'] = item['update_count'] + 1
            else:
                item['update_count'] = 1
            batch.put_item(
                Item=item
            )


def waiter_thread(q):
    log('waiter start sleeping')
    time.sleep(5)
    while not q.empty():
        time.sleep(5)
        log('sleeping')
    log('done')


if __name__ == '__main__':
    table = dynamodb.Table(table_name)
    q = queue.Queue()
    number_of_producers = 2
    number_of_consumers = 10
    producers = []
    consumers = []

    for i in range(number_of_consumers):
        thread_name = "consumer-" + str(i)
        thread = Thread(target=consumer_thread, name=thread_name, args=(table, q, thread_name,), daemon=True)
        producers.append(thread)
        thread.start()

    for i in range(number_of_producers):
        thread_name = "producer-" + str(i)
        thread = Thread(target=producer_thread, name=thread_name, args=(q, thread_name, i,), daemon=True)
        producers.append(thread)
        thread.start()

    waiter_thread = Thread(target=waiter_thread, name='waiter', args=(q,), daemon=True)
    waiter_thread.start()
    waiter_thread.join()
