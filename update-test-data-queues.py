#
# Insert records into table
#
# inspired by: https://python.plainenglish.io/using-python-to-create-a-dynamodb-table-56ed01fa3a10
# and https://boto3.amazonaws.com/v1/documentation/api/latest/guide/dynamodb.html
# and https://www.educative.io/courses/python-concurrency-for-senior-engineering-interviews/gkVzyO8V6Qj

import uuid
import boto3

from util import log
from threading import Thread
from threading import Condition
import time

dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000/')
# dynamodb = boto3.resource('dynamodb')
table_name = 'test_table'


class BlockingQueue:

    def __init__(self, max_size):
        self.max_size = max_size
        self.curr_size = 0
        self.cond = Condition()
        self.q = []

    def dequeue(self):

        self.cond.acquire()
        while self.curr_size == 0:
            self.cond.wait()

        item = self.q.pop(0)
        self.curr_size -= 1

        self.cond.notify_all()
        self.cond.release()

        return item

    def enqueue(self, item):

        self.cond.acquire()
        while self.curr_size == self.max_size:
            self.cond.wait()

        self.q.append(item)
        self.curr_size += 1

        self.cond.notify_all()
        self.cond.release()


def add_batch_to_queue(q, data):
    [q.enqueue(item) for item in data]


def producer_thread(q, thread_name):
    batch = table.scan()
    data = batch['Items']
    log('producer: ' + thread_name + ' count: ' + str(len(data)))
    add_batch_to_queue(q, data)

    while 'LastEvaluatedKey' in batch:
        batch = table.scan(ExclusiveStartKey=batch['LastEvaluatedKey'])
        data = batch['Items']
        log('producer: ' + thread_name + ' count: ' + str(len(data)))
        add_batch_to_queue(q, data)


def consumer_thread(table, q, thread_name):
    i = 0
    with table.batch_writer() as batch:
        while 1:
            item = q.dequeue()
            i = i+1
            if i % 1000 == 0:
                log('thread_name: ' + thread_name + ', count: ' + str(i))
            # {'attr5': '55555', 'id': 'ef84358b-46e2-433f-8d58-42e047bd556e', 'attr2': '22222', 'attr1': '11111', 'attr4': '44444', 'attr3': '33333'}
            if 'update_count' in item:
                item['update_count'] = item['update_count'] + 1
            else:
                item['update_count'] = 1
            batch.put_item(
                Item=item
            )


if __name__ == '__main__':
    table = dynamodb.Table(table_name)
    blocking_q = BlockingQueue(15)
    number_of_producers = 1
    producers = []
    number_of_consumers = 5
    consumers = []

    for i in range(number_of_consumers):
        thread_name = "consumer-" + str(i)
        thread = Thread(target=consumer_thread, name=thread_name, args=(table, blocking_q, thread_name, ), daemon=True)
        producers.append(thread)
        thread.start()

    for i in range(number_of_producers):
        thread_name = "producer-" + str(i)
        thread = Thread(target=producer_thread, name=thread_name, args=(blocking_q, thread_name,), daemon=True)
        producers.append(thread)
        thread.start()

    all_processes = consumers + producers
    print (len(all_processes))
    [i.join() for i in all_processes]

    # TODO: wait until queue is empty
    time.sleep(5)

