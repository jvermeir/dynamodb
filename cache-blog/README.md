# cache blog

see https://cdkworkshop.com/20-typescript/20-create-project.html for setup instructions
https://docs.aws.amazon.com/cdk/v2/guide/about_examples.html
https://github.com/aws-samples/aws-cdk-examples

## experiment

install aws-cdk:

```
npm install -g aws-cdk
```

```
  cdk init sample-app --language typescript
  cdk synth
  cdk bootstrap
  cdk deploy
```

```
npm run build && cdk deploy
```

tail logs (copy path to log file from cdk output):

```
aws logs tail /aws/lambda/CacheBlogStack-CacheServiceCacheHandlerB8F529E4-TF7jVAJQkgv4 --follow
```

test curls:
```
curl -X POST https://vr48uz2cf9.execute-api.eu-central-1.amazonaws.com/prod -H "Accept: application/json" -X POST -d '{ "id": "id1", "value":"30"}'
curl https://vr48uz2cf9.execute-api.eu-central-1.amazonaws.com/prod\?id\=id1
```

## Blog

Caching is a useful technique to improve performance or avoid overload of services. There are many solutions available, 
and in AWS one of them is using DynamoDB. Using DynamoDB to store data with a limited time to live (TTL) made sense in
our use case. We were already using the database for client data. Using it as a cache allowed us to limit the number
of services we needed expertise on. It is also reasonably fast and will scale way beyond our needs. In this blog I
will show how to implement a cache using DynamoDB and a lambda written in TypeScript. In a follow-up blog I'll show
another technique to improve the performance of queries on largish datasets. 

The source code for the examples in this blog can be found in
[https://github.com/jvermeir/dynamodb/tree/main/cache-blog]. 

I've used CDK (https://aws.amazon.com/cdk) to build the infrastructure needed for the cache service. 
The infrastructure is defined in `cache-blog/lib/cache-blog-stack.ts`. The important parts are
`const cacheTable = new dynamoDB.Table(this, 'CacheTable'...` and `const handler = new lambda.Function(this, 'CacheHandler', ...`

The cache table has a partitionKey named `id`. Data can be accessed very efficiently using this id. 
The table definition also adds an attribute named `timeToLiveAttribute` with the value `ttl`. 
This attribute controls how long a record in the table remains valid. DynamoDB will automatically remove a record when its
ttl is in the past. There are no useful guarantees about the cleanup process, but we'll come back to that later.

```
    const cacheTable = new dynamoDB.Table(this, 'CacheTable', {
      tableName: 'Cache',
      partitionKey: {
        name: 'id',
        type: dynamoDB.AttributeType.STRING,
      },
      billingMode: dynamoDB.BillingMode.PROVISIONED,
      timeToLiveAttribute: 'ttl',
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });
```

The lambda is defined with Node18 as its runtime:

```
    const handler = new lambda.Function(this, 'CacheHandler', {
      runtime: lambda.Runtime.NODEJS_18_X,
      code: lambda.Code.fromAsset('lambda'),
      handler: 'cache.handler',
    });
```

Besides the table and the lambda, `cache-blog-stack.ts` also defines an api gateway that will allow http access to the
cache lambda.

To deploy the stack, run: 

```
cdk bootstrap
```

to create the stack in your aws account. And then

```
npm run build && cdk deploy
```

The stack is now created. The output shows the endpoint of the api gateway used to access the caching lambda. It will
look like this:

```
 ✅  CacheBlogStack

✨  Deployment time: 22.37s

Outputs:
CacheBlogStack.CacheServicecacheapiEndpointDA49EE49 = https://0znqtkdtml.execute-api.eu-west-1.amazonaws.com/prod/
```

Now we can store and retrieve values from the cache like this:

```
curl -X POST https://0znqtkdtml.execute-api.eu-west-1.amazonaws.com/prod/ -H "Accept: application/json" -d '{ "id": "id1", "value":"30"}'
    
curl https://0znqtkdtml.execute-api.eu-west-1.amazonaws.com/prod/\?id\=id1
```

The value of id doesn't really matter, but a pattern we found useful looks like `<tableName> - <uuid>`, e.g.
`PersonalData - dbf275d5-d61b-488a-97fc-c2cb1832c852`. This would store personal data, maybe retrieved from a 
backend service, for a user account with id `dbf275d5-d61b-488a-97fc-c2cb1832c852`. In principle, the uuid value
would be enough, but we found we often want to store different types of data about a specific user account. In that
case the uuid would be the uuid of the account and the prefix of the cache key would identify the type of data in the
cache record.

The lambda code is straight forward, implementing a GET and POST method. The GET method is interesting because it shows
how to avoid a pitfall with the TTL attribute. `const getCacheItem = async (id: string): ...` in `lambda/database.ts`
executes this query when retrieving the value with the given id: 

```
    const queryCommand = new QueryCommand({
      TableName: CACHE_TABLE,
      ExpressionAttributeNames: {
        '#id': 'id',
        '#ttl': 'ttl',
      },
      KeyConditionExpression: '#id = :id',
      ExpressionAttributeValues: {
        ':id': id,
        ':now': now,
      },
      FilterExpression: '#ttl > :now',
    });
```

The important part is `FilterExpression: '#ttl > :now',`. This filter expression is necessary because DynamoDB doesn't 
guarantee outdated records are removed when their TTL is passed. Therefore, a record may still be in the database when it has
actually expired. We can fix this problem by adding the filter expression. Note that TTL is expressed in seconds.

Removing the infrastructure created for this blog can be done with CDK: 

```
cdk destroy
Are you sure you want to delete: CacheBlogStack (y/n)? y
CacheBlogStack: destroying... [1/1]

 ✅  CacheBlogStack: destroyed
```

References:

Getting started with CDK: https://cdkworkshop.com/20-typescript/20-create-project.html
DynamoDB and typescript: https://docs.aws.amazon.com/sdk-for-javascript/v2/developer-guide/dynamodb-examples.html
timeToLiveAttribute: https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/howitworks-ttl.html


# Welcome to your CDK TypeScript project

You should explore the contents of this project. It demonstrates a CDK app with an instance of a stack (`CacheBlogStack`)
which contains an Amazon SQS queue that is subscribed to an Amazon SNS topic.

The `cdk.json` file tells the CDK Toolkit how to execute your app. 

## Useful commands

* `npm run build`   compile typescript to js
* `npm run watch`   watch for changes and compile
* `npm run test`    perform the jest unit tests
* `cdk deploy`      deploy this stack to your default AWS account/region
* `cdk diff`        compare deployed stack with current state
* `cdk synth`       emits the synthesized CloudFormation template
