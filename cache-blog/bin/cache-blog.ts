#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { CacheService} from '../lib/cache-blog-stack';

export class CacheBlogStack extends cdk.Stack {
    constructor(scope: cdk.App, id: string, props?: cdk.StackProps) {
        super(scope, id, props);

        new CacheService(this, 'CacheService');
    }
}


const app = new cdk.App();
new CacheBlogStack(app, 'CacheBlogStack');
app.synth();