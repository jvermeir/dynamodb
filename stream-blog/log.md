# D20221102

cleanup, remove all buckets in this account. This is dangerous stuff...

``` 
buckets=`aws s3api list-buckets | jq '.Buckets[].Name'`
echo ${buckets} | while read line; do
    bucket=`echo ${line} | sed "s/\"//g"`
    echo ${bucket}
    aws s3 rb s3://${bucket} --force 
done
```

```
aws s3 rb s3://jans-lambda-bucket --force 
```

create bucket and store lambda code:

```
aws s3api create-bucket \
--acl private \
--bucket jans-lambda-bucket \
--region eu-central-1 \
--create-bucket-configuration LocationConstraint=eu-central-1
```

http://jans-lambda-bucket.s3.amazonaws.com

add lambda code

```
rm -f JansTestLambda.zip

zip JansTestLambda.zip JansTestLambda.py

aws s3 cp JansTestLambda.zip s3://jans-lambda-bucket
```

create role:

```
aws iam create-role --role-name lambda-ex --assume-role-policy-document file://trust-policy.json
```

attach policy to role:

```
aws iam attach-role-policy --role-name lambda-ex --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
```

create lambda:

https://awscli.amazonaws.com/v2/documentation/api/latest/reference/lambda/create-function.html

```
aws lambda create-function \
--function-name jans-test-lambda \
--runtime python3.9 \
--zip-file fileb://JansTestLambda.zip \
--handler lambda_handler \
--role arn:aws:iam::${ACCOUNT_ID}:role/lambda-ex 
```

```
aws iam create-policy --policy-name jans-test-lambda-policy --policy-document file://JansTestLambdaRole-Policy.json
aws iam attach-role-policy --role-name lambda-ex --policy-arn arn:aws:iam::${ACCOUNT_ID}:policy/jans-test-lambda-policy
```

create table

```
aws dynamodb create-table \
    --table-name JansTable \
    --attribute-definitions AttributeName=Id,AttributeType=S AttributeName=someText,AttributeType=S \
    --key-schema AttributeName=Id,KeyType=HASH AttributeName=someText,KeyType=RANGE \
    --stream-specification StreamEnabled=true,StreamViewType=NEW_AND_OLD_IMAGES \
    --provisioned-throughput=ReadCapacityUnits=100,WriteCapacityUnits=100
```

TODO

```
aws lambda add-permission \
    --function-name jans-test-lambda \
    --action lambda:InvokeFunction \
    --statement-id sns \
    --principal sns.amazonaws.com


aws lambda add-permission \
  --function-name {{LAMBDA-FUNCTION-NAME}} \
  --statement-id {{UNIQUE-ID}} \
  --action "lambda:InvokeFunction" \
  --principal sns.amazonaws.com \
  --source-arn arn:aws:sns:us-east-1:77889900:{{SNS-TOPIC-ARN}}
```

EventSourceDDBTableStream:
Type: AWS::Lambda::EventSourceMapping
Properties:
BatchSize: 1
Enabled: True
EventSourceArn: !GetAtt StreamsSampleDDBTable.StreamArn
FunctionName: !GetAtt ProcessEventLambda.Arn
StartingPosition: LATEST

## Parking lot
create policy:
