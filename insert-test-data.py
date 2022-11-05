#
# Create table and add test data
#
# inspired by: https://python.plainenglish.io/using-python-to-create-a-dynamodb-table-56ed01fa3a10
# and https://boto3.amazonaws.com/v1/documentation/api/latest/guide/dynamodb.html

import boto3
import uuid
from util import log


dynamodb = boto3.resource('dynamodb')
table_name = 'test_table'


def insert_test_data(table):
    with table.batch_writer() as batch:
        for i in range(200_000):
            if i % 1000 == 0:
                log('record: ' + str(i))

            batch.put_item(
                Item={
                    'id': str(uuid.uuid4()),
                    'attr1': "1" * 200,
                    'attr2': "2" * 200,
                    'attr3': "3" * 200,
                    'attr4': "4" * 200,
                    'attr5': "5" * 200,
                }
            )


if __name__ == '__main__':
    table = dynamodb.Table(table_name)
    insert_test_data(table)
    log(f"Created {table_name}")
