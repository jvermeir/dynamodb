#
# Insert records into table
#
# inspired by: https://python.plainenglish.io/using-python-to-create-a-dynamodb-table-56ed01fa3a10
# and https://boto3.amazonaws.com/v1/documentation/api/latest/guide/dynamodb.html
# and https://www.educative.io/courses/python-concurrency-for-senior-engineering-interviews/gkVzyO8V6Qj

import sys
import boto3
sys.path.append('..')

from util import log
from threading import Thread
from threading import Condition
import uuid
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


def producer_thread(q):
    item = 0
    while item < 3 * 10_000:
        q.enqueue(item)
        item += 1


def consumer_thread(table, q):
    with table.batch_writer() as batch:
        while 1:
            i = q.dequeue()
            if i % 1000 == 0:
                log('record: ' + str(i))

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
    blocking_q = BlockingQueue(5)

    consumerThread1 = Thread(target=consumer_thread, name="consumer-1", args=(table, blocking_q,), daemon=True)
    consumerThread2 = Thread(target=consumer_thread, name="consumer-2", args=(table, blocking_q,), daemon=True)
    consumerThread3 = Thread(target=consumer_thread, name="consumer-3", args=(table, blocking_q,), daemon=True)
    consumerThread4 = Thread(target=consumer_thread, name="consumer-4", args=(table, blocking_q,), daemon=True)
    producerThread1 = Thread(target=producer_thread, name="producer-1", args=(blocking_q,), daemon=True)

    consumerThread1.start()
    consumerThread2.start()
    consumerThread3.start()
    consumerThread4.start()
    producerThread1.start()

    producerThread1.join()
    # TODO: wait until queue is empty
    time.sleep(5)
