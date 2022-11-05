# D20221102


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

create policy:

```
aws iam create-policy --policy-name JansTestLambdaPolicy --policy-document file://JansTestLambdaRole-Policy.json
```

create lambda:

https://awscli.amazonaws.com/v2/documentation/api/latest/reference/lambda/create-function.html

```
aws lambda create-function \
--function-name JansTestLambda \
--runtime python3.9 \
--role JansTestLambdaRole \
--handler lambda_handler \
--code S3Bucket=jans-lambda-bucket
```

create table

```
aws dynamodb create-table \
    --table-name JansTable \
    --attribute-definitions AttributeName=Id,AttributeType=S AttributeName=someText,AttributeType=S \
    --key-schema AttributeName=Id,KeyType=HASH AttributeName=Department,KeyType=RANGE \
    --stream-specification StreamEnabled=boolean,StreamViewType=NEW_AND_OLD_IMAGES \
```
