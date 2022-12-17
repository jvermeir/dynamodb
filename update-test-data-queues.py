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

        self.cond.notifyAll()
        self.cond.release()

        return item

    def enqueue(self, item):

        self.cond.acquire()
        while self.curr_size == self.max_size:
            self.cond.wait()

        self.q.append(item)
        self.curr_size += 1

        self.cond.notifyAll()
        self.cond.release()


def producer_thread(q):
    item = 0
    while item < 3 * 10_000:
        q.enqueue(item)
        item += 1


def consumer_thread(table, q, thread_name):
    with table.batch_writer() as batch:
        while 1:
            i = q.dequeue()
            if i % 1000 == 0:
                log('thread_name: ' + thread_name + ', record: ' + str(i))

            batch.put_item(
                Item={
                    'id': str(uuid.uuid4()),
                    'attr1': "11111",
                    'attr2': "22222",
                    'attr3': "33333",
                    'attr4': "44444",
                    'attr5': "55555",
                }
            )


if __name__ == '__main__':
    table = dynamodb.Table(table_name)
    blocking_q = BlockingQueue(15)
    number_of_readers = 1
    number_of_writers = 5
    readers = []
    writers = []

    for i in range(number_of_writers):
        thread_name = "consumer-" + str(i)
        thread = Thread(target=consumer_thread, name=thread_name, args=(table, blocking_q, thread_name, ), daemon=True)
        writers.append(thread)
        thread.start()

    for i in range(number_of_readers):
        thread = Thread(target=producer_thread, name="producer-" + str(i), args=(blocking_q,), daemon=True)
        writers.append(thread)
        thread.start()


    all = readers + writers
    print (len(all))
    [i.join() for i in writers]
