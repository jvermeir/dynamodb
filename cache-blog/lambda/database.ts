import { DynamoDB } from '@aws-sdk/client-dynamodb';
import { fromNodeProviderChain } from '@aws-sdk/credential-providers';
import { DynamoDBDocumentClient, PutCommand, QueryCommand } from '@aws-sdk/lib-dynamodb';

export type CacheItem = {
  id: string;
  value: string;
  ttl: number;
  updatedAt: number;
  createdAt: number;
};
export const CACHE_TABLE = 'Cache';
export const DynamoDBClient = (client: DynamoDBDocumentClient) => {
  const getCacheItem = async (id: string): Promise<CacheItem | null> => {
    const now = Math.round(Date.now() / 1000);
    console.log(`find item with ${id} at now: ${now}`);

    const queryCommand = new QueryCommand({
      TableName: CACHE_TABLE,
      ExpressionAttributeNames: {
        '#id': 'id',
        '#ttl': 'ttl',
      },
      KeyConditionExpression: '#id = :id',
      ExpressionAttributeValues: {
        ':id': id,
        ':now': now,
      },
      FilterExpression: '#ttl > :now',
    });

    return client
      .send(queryCommand)
      .then(({ Items }) => (Items ?? []) as CacheItem[])
      .then((cacheItems) => cacheItems[0] ?? null);
  };

  const saveCacheItem = async (cacheItem: CacheItem) => {
    const ttl = Math.round(Date.now() / 1000) + 60 * 60;
    cacheItem.createdAt = cacheItem.createdAt ?? Date.now();
    cacheItem.updatedAt = Date.now();
    cacheItem.ttl = ttl;
    const putCommand = new PutCommand({
      TableName: CACHE_TABLE,
      Item: cacheItem,
    });

    console.log(`save ${JSON.stringify(cacheItem)}`);

    return client.send(putCommand).then(() => cacheItem);
  };

  return { getCacheItem, saveCacheItem };
};

export const dynamoDB = DynamoDBClient(
  DynamoDBDocumentClient.from(
    new DynamoDB({
      region: 'eu-west-1',
      maxAttempts: 5,
      credentials: fromNodeProviderChain(),
    })
  )
);
