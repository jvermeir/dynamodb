import { DynamoDB } from "@aws-sdk/client-dynamodb";
import { fromNodeProviderChain } from "@aws-sdk/credential-providers";
import {
  DynamoDBDocumentClient,
  PutCommand,
  QueryCommand,
} from "@aws-sdk/lib-dynamodb";

export type Transaction = {
  id: string;
  owner: string;
  amount: number;
  createdAt: number;
};
export const TRANSACTION_TABLE = "Transaction";
export const DynamoDBClient = (client: DynamoDBDocumentClient) => {
  const getTransaction = async (id: string): Promise<Transaction | null> => {
    console.log(`find item with ${id}`);

    const queryCommand = new QueryCommand({
      TableName: TRANSACTION_TABLE,
      ExpressionAttributeNames: {
        "#id": "id",
      },
      KeyConditionExpression: "#id = :id",
      ExpressionAttributeValues: {
        ":id": id,
      },
    });

    return client
      .send(queryCommand)
      .then(({ Items }) => (Items ?? []) as Transaction[])
      .then((transactions) => transactions[0] ?? null);
  };

  const getTransactionsByOwner = async (
    owner: string
  ): Promise<Transaction[] | null> => {
    console.log(`find transactions by ${owner}`);

    let command = new QueryCommand({
      TableName: TRANSACTION_TABLE,
      IndexName: "byOwnerByCreatedAt",
      ExpressionAttributeNames: {
        "#owner": "owner",
      },
      KeyConditionExpression: "#owner = :owner",
      ExpressionAttributeValues: {
        ":owner": owner,
      },
      ScanIndexForward: false,
    });

    const items: Transaction[] = [];
    do {
      const { Items: newItems, LastEvaluatedKey } = await client.send(command);
      items.push(...((newItems ?? []) as Transaction[]));
      command = new QueryCommand({
        ...command.input,
        ExclusiveStartKey: LastEvaluatedKey,
      });
    } while (command.input.ExclusiveStartKey !== undefined);

    return items;
  };

  const saveTransaction = async (transaction: Transaction) => {
    console.log(`save ${JSON.stringify(transaction)}`);
    transaction.createdAt = transaction.createdAt ?? Date.now();
    const putCommand = new PutCommand({
      TableName: TRANSACTION_TABLE,
      Item: {
        id: transaction.id,
        owner: transaction.owner,
        amount: transaction.amount,
        createdAt: transaction.createdAt,
      },
    });

    return client.send(putCommand).then(() => transaction);
  };

  return { getTransaction, getTransactionsByOwner, saveTransaction };
};

export const dynamoDB = DynamoDBClient(
  DynamoDBDocumentClient.from(
    new DynamoDB({
      region: "eu-central-1",
      maxAttempts: 5,
      credentials: fromNodeProviderChain(),
    })
  )
);

(async () => {
  await dynamoDB.saveTransaction({
    id: "owner1-1",
    amount: 10,
    owner: "owner1",
  } as Transaction);
  const transaction = await dynamoDB.getTransaction("myId");
  console.log(transaction);
})();
