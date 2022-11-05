import json


def lambda_handler(event, context):
    print("Received event: " + json.dumps(event))
    for record in event['Records']:
        print("do something useful")
    return 'Successfully processed {} records.'.format(len(event['Records']))
