#
# Re-create infrastructure for use in tests
# info: https://boto3.amazonaws.com/v1/documentation/api/latest/guide/sqs-example-using-queues.html
#

import sys
sys.path.append('../..')
import os
import json
import boto3

from util import log

# local: dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000/')
dynamodb = boto3.resource('dynamodb')
sqs = boto3.client('sqs')
lambda_client = boto3.client('lambda')
iam = boto3.client('iam')

# dynamodb = boto3.resource('dynamodb')
table_name = 'test_table'
queue_name = 'test_queue'
account_id = os.environ['ACCOUNT_ID']



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
        'ProvisionedThroughput': {
            'ReadCapacityUnits': 1000,
            'WriteCapacityUnits': 1000
        }
    }
    table = dynamodb.create_table(**params)
    log(f"Creating {table_name}")
    table.wait_until_exists()
    return table


def delete_queue():
    try:
        response = sqs.get_queue_url(QueueName=queue_name)
        queue_url = response['QueueUrl']
        sqs.delete_queue(QueueUrl=queue_url)
    except:
        log(f'assuming  {queue_name} was deleted')


def create_queue():
    response = sqs.create_queue(
        QueueName=queue_name,
        Attributes={
            'DelaySeconds': '60',
            'MessageRetentionPeriod': '86400'
        }
    )


def delete_lambda():
    try:
        lambda_client.delete_function(FunctionName='Test-lambda')
    except:
        log(f'assuming  Test-lambda was deleted')


def aws_file():
    with open('./processor.zip', 'rb') as file_data:
        bytes_content = file_data.read()
    return bytes_content


def create_lambda():
    response = lambda_client.create_function(
        Code={
            'ZipFile': aws_file()
        },
        Description='Hello World Test.',
        FunctionName='Test-lambda',
        Handler='lambda_function.lambda_handler',
        Publish=True,
        Role=f'arn:aws:iam::{account_id}:role/lambda-role',
        Runtime='python3.8',
    )
    return response


def create_role():
    log(f"Creating LambdaBasicExecution role")
    role_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "",
                "Effect": "Allow",
                "Principal": {
                    "Service": "lambda.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }

    response = iam.create_role(
        RoleName='LambdaBasicExecution',
        AssumeRolePolicyDocument=json.dumps(role_policy),
    )
    log(response)


if __name__ == '__main__':
    # delete_table()
    # delete_queue()
    delete_lambda()
    # create_table()
    # create_queue()
    # create_role()
    create_lambda()
