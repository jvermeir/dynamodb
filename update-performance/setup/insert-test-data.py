#
# Create table and add test data
#
# inspired by: https://python.plainenglish.io/using-python-to-create-a-dynamodb-table-56ed01fa3a10
# and https://boto3.amazonaws.com/v1/documentation/api/latest/guide/dynamodb.html

import sys
sys.path.append('../..')
import boto3
import uuid
from util import log


dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000/')
# dynamodb = boto3.resource('dynamodb')
table_name = 'test_table'
number_of_records = 65_000


def insert_test_data(table):
    with table.batch_writer() as batch:
        for i in range(number_of_records):
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
    insert_test_data(table)
    log(f"inserted {number_of_records} in {table_name}")
