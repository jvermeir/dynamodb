#
# Read a random record to check the contents of the table
#

import boto3

from util import log
from threading import Thread
from threading import Condition
import time

dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000/')
# dynamodb = boto3.resource('dynamodb')
table_name = 'test_table'


if __name__ == '__main__':
    table = dynamodb.Table(table_name)
    batch = table.scan()
    item = batch['Items'][0]
    print(item)
