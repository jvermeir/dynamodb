import {Context, APIGatewayProxyResult, APIGatewayEvent} from 'aws-lambda';
import {DynamoDB, PutItemInput, QueryInput, UpdateItemInput} from '@aws-sdk/client-dynamodb';
import {marshall, unmarshall} from '@aws-sdk/util-dynamodb';

interface CacheItem {
    id: string;
    value: string;
    ttl: number;
}

export const handler = async (event: APIGatewayEvent, context: Context): Promise<APIGatewayProxyResult> => {

    const dynamoClient = new DynamoDB({
        region: 'eu-central-1'
    })

    const now = Math.round(new Date().getTime() / 1000);
    const newCacheItem: CacheItem = {
        id: 'test',
        value: Math.random().toString(),
        ttl: now + 60 * 60,
    }

    try {
        console.log('querying');
        const queryItem: QueryInput = {
            KeyConditionExpression: '#id = :id',
            ExpressionAttributeNames: {
                '#id': 'id'
            },
            ExpressionAttributeValues: marshall({
                ':id': newCacheItem.id
            }),
            TableName: 'Cache'
        }

        const {Items} = await dynamoClient.query(queryItem);

        const items = Items ? Items.map(item => unmarshall(item)) : []
        console.log(`Items: ${JSON.stringify(items, null, 2)}`);

        if (items.length === 0) {
            console.log('inserting');
            const cacheParams: PutItemInput = {
                Item: marshall(newCacheItem),
                TableName: 'Cache',
            }
            await dynamoClient.putItem(cacheParams);
        } else {
            console.log('updating');
            console.log(`newCacheItem: ${JSON.stringify(newCacheItem, null, 2)}`);
            const id = newCacheItem.id;
            const cacheParams: UpdateItemInput = {
                Key: marshall({'id':id}),
                UpdateExpression: 'SET #value = :value, #ttl = :ttl',
                ExpressionAttributeValues: marshall({
                    ':value': newCacheItem.value,
                    ':ttl': newCacheItem.ttl,
                }),
                ExpressionAttributeNames: {
                    '#ttl': 'ttl',
                    '#value': 'value',
                },

                ReturnValues: 'ALL_NEW',
                TableName: 'Cache',
            }
            await dynamoClient.updateItem(cacheParams);
        }

    } catch (error) {
        console.log(`Error: ${JSON.stringify(error, null, 2)}`);
        return {
            statusCode: 500,
            body: JSON.stringify({
                message: `failed to save ${JSON.stringify(newCacheItem)}`,
            }),
        };
    }

    return {
        statusCode: 200,
        body: JSON.stringify({
            message: `saved ${JSON.stringify(newCacheItem)}`,
        }),
    };
};