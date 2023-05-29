import { Construct } from 'constructs';
import { NodejsFunction } from 'aws-cdk-lib/aws-lambda-nodejs';
import { LambdaRestApi } from 'aws-cdk-lib/aws-apigateway';
import {AttributeType, BillingMode, Table} from 'aws-cdk-lib/aws-dynamodb';
import {RemovalPolicy} from "aws-cdk-lib";

export class HelloWorld extends Construct {
    constructor(scope: Construct, id: string) {
        super(scope, id);
        const helloFunction = new NodejsFunction(this, 'function');
        new LambdaRestApi(this, 'apigw', {
            handler: helloFunction,
        });

        const cacheTable = new Table(this, 'CacheTable', {
            tableName: 'Cache',
            partitionKey: {
                name: 'id',
                type: AttributeType.STRING,
            },
            billingMode: BillingMode.PROVISIONED,
            timeToLiveAttribute: 'ttl',
            removalPolicy: RemovalPolicy.DESTROY,
        });

        cacheTable.grantReadWriteData(helloFunction);

    }
}