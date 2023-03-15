#
# Re-create table for use in tests
#

import sys
sys.path.append('../..')

import boto3

from util import log

dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000/')
# dynamodb = boto3.resource('dynamodb')
table_name = 'test_table'


def delete_table():
    log(f'Deleting {table_name}')
    try:
        table = dynamodb.Table(table_name)
        table.delete()
        table.wait_until_not_exists()
    except:
        log(f'assuming  {table_name} was deleted')


def create_table():
    params = {
        'TableName': table_name,
        'KeySchema': [
            {'AttributeName': 'id', 'KeyType': 'HASH'}
        ],
        'AttributeDefinitions': [
            {'AttributeName': 'id', 'AttributeType': 'S'}
        ],
        'BillingMode': 'PAY_PER_REQUEST',
        'ProvisionedThroughput': {
            'ReadCapacityUnits': 1000,
            'WriteCapacityUnits': 1000
        }
    }
    table = dynamodb.create_table(**params)
    log(f"Creating {table_name}")
    table.wait_until_exists()
    return table


if __name__ == '__main__':
    delete_table()
    create_table()
