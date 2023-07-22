# Transactions and summaries

```
npm run build && cdk deploy
```

The output includes the name of the lambda.

tail logs (copy name from cdk output):

```
aws logs tail /aws/lambda/<enter lambda name here> --follow
```

test scripts:

Given hostname `l86omzmsi0.execute-api.eu-central-1.amazonaws.com`:

```
./tools/add_transaction.sh l86omzmsi0 "{ \"id\": \"owner1-txn1\", \"amount\":1, \"owner\":\"owner1\"}"
./tools/get_by_owner.sh l86omzmsi0 owner1
./tools/get_by_id.sh l86omzmsi0 owner1-txn1
./tools/total.sh l86omzmsi0 owner1
```

## Blog

In this blog [TODO:link], we looked at a simple solution to use DynamoDB as a cache to store data with a limited time to live. 
The blog showed how to store values that might be retrieved from a back end server. This service might have limited 
capacity or be too expensive to handle a lot of requests. Storing a temporary value may help reducing the load. Also, 
DynamoDB is especially good at getting data from a possibly very large table by primary key.  

Another use case is slightly different. What if we have a lot of data and want to avoid querying all that data just
to get a summary? An example would be retrieving a total at a specific point in time based on a list of transactions.
We might have thousands of transactions for a specific userId and might be interested in showing the sum of 
all transactions as well as the latest five. 

The code for this blog can be found here: [https://github.com/jvermeir/dynamodb/tree/main/transaction].

Getting the latest transactions from a table by owner can be done with a `GlobalSecondaryIndex`, 
with this CDK code:

```
    const transactionTable = new dynamoDB.Table(this, "TransactionTable", {
      tableName: "Transaction",
      partitionKey: {
        name: "id",
        type: dynamoDB.AttributeType.STRING,
      },
      billingMode: dynamoDB.BillingMode.PROVISIONED,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });
```

The table definition shows a partition key based on an id. This could be anything, e.g. a generated uuid.
Adding a sortKey like this 

```
    transactionTable.addGlobalSecondaryIndex({
      indexName: "byOwnerByCreatedAt",
      partitionKey: { name: "owner", type: dynamoDB.AttributeType.STRING },
      sortKey: { name: "createdAt", type: dynamoDB.AttributeType.NUMBER },
      readCapacity: 1,
      writeCapacity: 1,
      projectionType: dynamoDB.ProjectionType.ALL,
    });
```

creates an index that can be used to query data by the owner field. The data is stored in sorted order using a timestamp stored in `createdAt`.
Given this definition of the transaction table, we can run this query:

```
   let command = new QueryCommand({
      TableName: TRANSACTION_TABLE,
      IndexName: 'byOwnerByCreatedAt',
      ExpressionAttributeNames: {
        '#owner': 'owner',
        '#createdAt': 'createdAt',
      },
      ExpressionAttributeValues: {
        ':owner': owner,
        ':createdAt': timestamp,
      },
      KeyConditionExpression: '#owner = :owner AND #createdAt <= :createdAt',
      ScanIndexForward: false,
    });
```

This query would return all transactions for a given `owner` older than a `timestamp` passed as parameters.
`ScanIndexForward: false,` is essential, because it retrieves records starting with the most recent. 

Given this query, the `getTotalByOwner` function in `transaction/lambda/database.ts` loops through records, calculating
a total, until it finds a summary record. It then adds a new summary record to the transactions table to speed up
follow-up requests. The data in the table may look like this:

```
{
  "transactions": [
    {"amount": 14, "createdAt": 1690052471641, "owner": "owner1", "id": "id14"},
    {"amount": 91, "createdAt": 1690016544701, "owner": "owner1", "id": "summary-owner1-1690016544701", "type": "summary"},
    {"amount": 13, "createdAt": 1690016527772, "owner": "owner1", "id": "id13"},
    ...
    {"amount": 3, "createdAt": 1690016421753, "owner": "owner1", "id": "id3"},
    {"amount": 3, "createdAt": 1690016395422, "owner": "owner1", "id": "summary-owner1-1690016395422", "type": "summary"},
    {"amount": 2, "createdAt": 1690016368019, "owner": "owner1", "id": "id2"},
    {"amount": 1, "createdAt": 1690016361282, "owner": "owner1", "id": "id1"}
  ]
}
```

So there's a list of transactions with an amount and id sorted by createdAt and 
interspersed with transactions where `type` is `summary`. 

The algorithm in `getTotalByOwner` does this while trying to cope with potential concurrency issues: 

```
define the query
define a summary record with the current date as its createdAt value
while there's more data, get a set of record
    loop through the records
        add the value of amount to total
        stop if the type of the record is summary
    update the query and get the next set of records
save the summary value in the transactions table        
```

There are some pitfalls that are addressed by the code in `getTotalByOwner`. Several processes may try to read
the transaction table for a `owner` concurrently. Or a record may be added while we're calculating the summary. 
To protect against concurrency issues, the code creates a summary record with the current date as its `createdAt` 
value as its first action. Then transactions are queried that are older then the timestamp in the new summary record. 
This freezes the dataset the summary is based on: even if records are added the set considered for the summary won't change.

As an optimization, we don't write a summary record every time the transactions are retrieved. Records are returned 
by the database in a set anyway, so before any processing may take place, a full set has to be loaded. We can 
therefore save a bit of storage space by adding a summary every X records (10 in the code example). This strategy
would also avoid degenerate cases where following every record a summary record is stored.

These optimizations complicate the code but we could easily hide them in a generic function. 