import * as cdk from 'aws-cdk-lib';
import * as dynamoDB from 'aws-cdk-lib/aws-dynamodb';
import { Construct } from 'constructs';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as lambda from 'aws-cdk-lib/aws-lambda';

export class CacheService extends Construct {
  constructor(scope: Construct, id: string) {
    super(scope, id);

    const handler = new lambda.Function(this, 'CacheHandler', {
      runtime: lambda.Runtime.NODEJS_18_X,
      code: lambda.Code.fromAsset('lambda'),
      handler: 'cache.handler',
    });

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

    cacheTable.grantReadWriteData(handler);

    const api = new apigateway.RestApi(this, 'cache-api', {
      restApiName: 'Cache Service',
      description: 'This service caches stuff.',
    });

    const getCacheIntegration = new apigateway.LambdaIntegration(handler, {
      requestTemplates: { 'application/json': '{ "statusCode": "200" }' },
    });

    api.root.addMethod('GET', getCacheIntegration);

    const postCacheIntegration = new apigateway.LambdaIntegration(handler, {
      requestTemplates: { 'application/json': '{ "statusCode": "200" }' },
    });

    api.root.addMethod('POST', postCacheIntegration);
  }
}
