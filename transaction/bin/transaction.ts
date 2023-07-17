#!/usr/bin/env node
import * as cdk from "aws-cdk-lib";
import { TransactionService } from "../lib/transaction-stack";

export class TransactionStack extends cdk.Stack {
  constructor(scope: cdk.App, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    new TransactionService(this, "TransactionService");
  }
}

const app = new cdk.App();
new TransactionStack(app, "TransactionStack");
app.synth();
