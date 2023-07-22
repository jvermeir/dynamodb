import { DynamoDB } from '@aws-sdk/client-dynamodb';
import { fromNodeProviderChain } from '@aws-sdk/credential-providers';
import {
  DynamoDBDocumentClient,
  PutCommand,
  QueryCommand,
} from '@aws-sdk/lib-dynamodb';

export type Transaction = {
  id: string;
  owner: string;
  amount: number;
  createdAt: number;
  type: string;
};
export const TRANSACTION_TABLE = 'Transaction';
export const DynamoDBClient = (client: DynamoDBDocumentClient) => {
  const getTransaction = async (id: string): Promise<Transaction | null> => {
    console.log(`find item with ${id}`);

    const queryCommand = new QueryCommand({
      TableName: TRANSACTION_TABLE,
      ExpressionAttributeNames: {
        '#id': 'id',
      },
      KeyConditionExpression: '#id = :id',
      ExpressionAttributeValues: {
        ':id': id,
      },
    });

    return client
      .send(queryCommand)
      .then(({ Items }) => (Items ?? []) as Transaction[])
      .then((transactions) => transactions[0] ?? null);
  };

  const getTotalByOwner = async (owner: string): Promise<Transaction | null> => {
    const timestamp = Date.now();
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

    const summary = {
      id: `summary-${owner}-${timestamp}`,
      owner,
      amount: 0,
      createdAt: timestamp,
      type: 'summary',
    };

    let summaryFound = false;
    let counter = 0;
    do {
      const { Items: newItems, LastEvaluatedKey } = await client.send(command);

      const transactions = newItems?.map((item) => item as Transaction) ?? [];

      transactions.every((transaction) => {
        counter++;
        console.log(`transaction: ${JSON.stringify(transaction)}`);
        summary.amount += transaction.amount;
        if (transaction.type === 'summary') {
          summaryFound = true;
          console.log(`summary found: ${JSON.stringify(summary)}`);
          return false;
        }
        return true;
      });

      command = new QueryCommand({
        ...command.input,
        ExclusiveStartKey: LastEvaluatedKey,
      });
    } while (command.input.ExclusiveStartKey !== undefined && !summaryFound);

    if (summaryFound && counter > 10 || !summaryFound) {
      return saveTransaction(summary);
    }
    return summary;
  };

  const getTransactionsByOwner = async (
    owner: string
  ): Promise<Transaction[] | null> => {
    console.log(`find transactions by ${owner}`);

    let command = new QueryCommand({
      TableName: TRANSACTION_TABLE,
      IndexName: 'byOwnerByCreatedAt',
      ExpressionAttributeNames: {
        '#owner': 'owner',
      },
      KeyConditionExpression: '#owner = :owner',
      ExpressionAttributeValues: {
        ':owner': owner,
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
        type: transaction.type,
      },
    });

    return client.send(putCommand).then(() => transaction);
  };

  return { getTransaction, getTotalByOwner, getTransactionsByOwner, saveTransaction };
};

export const dynamoDB = DynamoDBClient(
  DynamoDBDocumentClient.from(
    new DynamoDB({
      region: 'eu-central-1',
      maxAttempts: 5,
      credentials: fromNodeProviderChain(),
    }), { marshallOptions: { removeUndefinedValues: true }}
  )
);
