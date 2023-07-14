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

compare to my-widget-service

index.ts -> define class MyWidgetServiceStack and create instance
                uses widget_service.WidgetService
widget_service.ts -> export class WidgetService extends Construct 
                defines stack with lambda and rest api
resources/widgets.js -> defines rest service

lib/cache-blog-stack.ts -> export class CacheBlogStack extends Construct
                defines stack with lambda and rest api
 bin/cache-blog.ts -> semi completed version of index.ts
lib/cache-blog-stack.function.ts -> lambda defines rest service

tail logs:

```
aws logs tail /aws/lambda/CacheBlogStack-CacheServiceCacheHandlerB8F529E4-TF7jVAJQkgv4 --follow
```

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
