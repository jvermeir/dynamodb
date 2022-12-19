#
# update all records in a table using a single process read/update loop
#

import sys
import boto3
sys.path.append('..')
from util import log

dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000/')
# dynamodb = boto3.resource('dynamodb')
table_name = 'test_table'

i = 0


def update(item):
    global i
    i = i+1
    if i % 1000 == 0:
        log('count: ' + str(i))
    if 'update_count' in item:
        item['update_count'] = item['update_count'] + 1
    else:
        item['update_count'] = 1
    table.put_item(Item=item)

def update_batch(batch):
    data = batch['Items']
    [update(record) for record in data]


def update_all():
    batch = table.scan()
    update_batch(batch)

    while 'LastEvaluatedKey' in batch:
        batch = table.scan(ExclusiveStartKey=batch['LastEvaluatedKey'])
        update_batch(batch)


if __name__ == '__main__':
    log('start')
    table = dynamodb.Table(table_name)
    update_all()
    log('end')
