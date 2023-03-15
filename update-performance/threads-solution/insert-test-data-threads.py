#
# Insert records into table
#
# inspired by: https://python.plainenglish.io/using-python-to-create-a-dynamodb-table-56ed01fa3a10
# and https://boto3.amazonaws.com/v1/documentation/api/latest/guide/dynamodb.html

import sys
import boto3
import queue
from threading import Thread
import uuid
import click
import time

sys.path.append('../..')
from util import log

dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000/')
# dynamodb = boto3.resource('dynamodb')
table_name = 'test_table'


def producer(q, no_of_records):
    item = 0
    while item < no_of_records:
        q.put(item)
        item += 1
        if item % 10_000 == 0:
            log('producer, record: ' + str(item))
            time.sleep(1)


def consumer(table, q, thread_name):
    with table.batch_writer() as batch:
        while 1:
            i = q.get(timeout=5)
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


def waiter(q):
    log('waiter start sleeping')
    time.sleep(5)
    while not q.empty():
        time.sleep(5)
        log('sleeping')
    log('done')


def insert(no_of_records):
    table = dynamodb.Table(table_name)
    q = queue.Queue()

    number_of_consumers = 5
    consumers = []

    for i in range(number_of_consumers):
        thread_name = "consumer-" + str(i)
        thread = Thread(target=consumer, name=thread_name, args=(table, q, thread_name,), daemon=True)
        consumers.append(thread)
        thread.start()

    producer_tread = Thread(target=producer, name="producer-1", args=(q, no_of_records), daemon=True)
    producer_tread.start()

    waiter_thread = Thread(target=waiter, name='waiter', args=(q,), daemon=True)
    waiter_thread.start()
    waiter_thread.join()


@click.command()
@click.option('--no_of_records', default=30_000,
              help='Number of test records to insert')
def cli(no_of_records):
    print('inserting ' + str(no_of_records) + ' records')
    insert(no_of_records)


if __name__ == '__main__':
    cli()
