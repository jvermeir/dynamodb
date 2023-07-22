import * as cdk from "aws-cdk-lib";
import * as dynamoDB from "aws-cdk-lib/aws-dynamodb";
import { Construct } from "constructs";
import * as apigateway from "aws-cdk-lib/aws-apigateway";
import * as lambda from "aws-cdk-lib/aws-lambda";

export class TransactionService extends Construct {
  constructor(scope: Construct, id: string) {
    super(scope, id);

    const handler = new lambda.Function(this, "TransactionHandler", {
      runtime: lambda.Runtime.NODEJS_18_X,
      code: lambda.Code.fromAsset("lambda"),
      handler: "transaction.handler",
    });

    const transactionTable = new dynamoDB.Table(this, "TransactionTable", {
      tableName: "Transaction",
      partitionKey: {
        name: "id",
        type: dynamoDB.AttributeType.STRING,
      },
      billingMode: dynamoDB.BillingMode.PROVISIONED,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    transactionTable.addGlobalSecondaryIndex({
      indexName: "byOwnerByCreatedAt",
      partitionKey: { name: "owner", type: dynamoDB.AttributeType.STRING },
      sortKey: { name: "createdAt", type: dynamoDB.AttributeType.NUMBER },
      readCapacity: 1,
      writeCapacity: 1,
      projectionType: dynamoDB.ProjectionType.ALL,
    });

    transactionTable.grantReadWriteData(handler);

    new apigateway.LambdaRestApi(this, 'myapi', {
      handler: handler,
    });
  }
}
