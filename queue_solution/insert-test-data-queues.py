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
import uuid
import time
import click

dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000/')
# dynamodb = boto3.resource('dynamodb')
table_name = 'test_table'


def producer_thread(q, no_of_records):
    item = 0
    while item < no_of_records:
        q.put(item)
        item += 1


def consumer_thread(table, q):
    with table.batch_writer() as batch:
        while 1:
            i = q.get()
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


def insert(no_of_records):
    table = dynamodb.Table(table_name)
    q = queue.Queue()

    consumerThread1 = Thread(target=consumer_thread, name="consumer-1", args=(table, q,), daemon=True)
    consumerThread2 = Thread(target=consumer_thread, name="consumer-2", args=(table, q,), daemon=True)
    consumerThread3 = Thread(target=consumer_thread, name="consumer-3", args=(table, q,), daemon=True)
    consumerThread4 = Thread(target=consumer_thread, name="consumer-4", args=(table, q,), daemon=True)
    producerThread1 = Thread(target=producer_thread, name="producer-1", args=(q, no_of_records), daemon=True)

    consumerThread1.start()
    consumerThread2.start()
    consumerThread3.start()
    consumerThread4.start()
    producerThread1.start()

    producerThread1.join()
    # TODO: wait until queue is empty
    time.sleep(5)


@click.command()
@click.option('--no_of_records', default = 30_000,
              help ='Number of test records to insert')
def cli(no_of_records):
    print('inserting ' + str(no_of_records) + ' records')
    insert(no_of_records)


if __name__ == '__main__':
    cli()
