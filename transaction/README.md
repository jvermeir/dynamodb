# Transactions and summaries

```
npm run build && cdk deploy
```

tail logs (copy path to log file from cdk output):

```
aws logs tail /aws/lambda/CacheBlogStack-CacheServiceCacheHandlerB8F529E4-TF7jVAJQkgv4 --follow
```

test curls:
```
curl -X POST https://erswhy1zm5.execute-api.eu-central-1.amazonaws.com/prod/ -H "Accept: application/json" -X POST -d '{ "id": "id1", "amount":"30"}'
curl https://erswhy1zm5.execute-api.eu-central-1.amazonaws.com/prod//\?id\=id1
```
