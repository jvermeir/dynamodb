#
# Update records in a table using threads
#

import json
import multiprocessing
import os
from datetime import datetime
from multiprocessing import freeze_support
import boto3
import sys
from decimal import Decimal


sys.path.append('../..')
from util import log

dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000/')
# use this if you've got a configuration file in ~/.aws: dynamodb = boto3.resource('dynamodb')
table_name = 'test_table'
table = dynamodb.Table(table_name)
concurrent_jobs = 20


def log(s):
    print(datetime.utcnow().isoformat()[:-3] + 'Z: ' + s)


# For some types we need encoders for the JSON serializer. This is necessary because
# the data is sent as a string to the child process
class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return json.JSONEncoder.default(self, obj)


# Do something useful here specific for your use case. In this case the tenant field is set to a default if its empty.
# Testing if a record needs updating may considerably speed up the process. Also, it ensures the script
# can be restarted.
def update_record(item, updated, batch):
    if 'update_count' in item:
        item['update_count'] = item['update_count'] + 1
    else:
        item['update_count'] = 1
    batch.put_item(Item=item)
    return updated + 1


# run the update_record method on all records in a batch
def process_batch(batch):
    updated = 0
    data = json.loads(batch, parse_float=Decimal)
    log(f'update {len(data)} records')

    with table.batch_writer() as batch:
        for item in data:
            updated = update_record(item, updated, batch)

    log(str(os.getpid()) + ' updated :' + str(updated) + ' records')
    return updated


# Add a job to process a batch of records
def add_job(batch, pool):
    log('append job')
    items = json.dumps(batch['Items'], cls=JSONEncoder)
    job = pool.apply_async(process_batch, (items,))

    return job


# Read all data in a table and process in chunks
def execute_update():
    with multiprocessing.Pool(processes=concurrent_jobs) as pool:

        jobs = []
        batch = table.scan()
        jobs.append(add_job(batch, pool))

        while 'LastEvaluatedKey' in batch:
            batch = table.scan(ExclusiveStartKey=batch['LastEvaluatedKey'])
            jobs.append(add_job(batch, pool))

        results = [job.get() for job in jobs]

        log(f'total updated: {sum(results)}')


if __name__ == '__main__':
    freeze_support()
    log('start - multiprocessing')
    table = dynamodb.Table(table_name)
    start_time = datetime.utcnow()
    execute_update()
    end_time = datetime.utcnow()
    log(f'end - multiprocessing, elapsed time: {str(end_time - start_time)}')
