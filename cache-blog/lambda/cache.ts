import {dynamoDB} from './database';

/*
    This lambda allows storing and retrieving of arbitrary JSON formatted data from the cache table.
    The service could be used from a front end to get data for a user.
 */

export const handler = async (event: any, context: any) => {
    const method = event.httpMethod;

    try {
        if (method === 'GET') {
            const queryStringParameters = event.queryStringParameters;
            const id = queryStringParameters?.id;
            console.log(`queryStringParameters: ${JSON.stringify(queryStringParameters)}, id: ${id}`);
            const cacheItem = await dynamoDB.getCacheItem(id);
            const body = {
                item: cacheItem,
            };
            return {
                statusCode: 200,
                headers: {},
                body: JSON.stringify(body),
            };
        } else if (method === 'POST') {
            const cacheItemParam = event.body;
            const cacheItem = JSON.parse(cacheItemParam);
            console.log(`cacheItem: ${JSON.stringify(cacheItem)}`);
            const cacheItemSaved = await dynamoDB.saveCacheItem(cacheItem);
            console.log(cacheItemSaved);
            return {
                statusCode: 200,
                body: JSON.stringify({
                    message: `saved ${JSON.stringify(cacheItemSaved)}`,
                }),
            };
        } else {
            return {
                statusCode: 500,
                body: JSON.stringify({
                    message: `method ${method} not supported`,
                }),
            };
        }
    } catch (error) {
        const message = `Error: ${JSON.stringify(error, null, 2)}`;
        return {
            statusCode: 500,
            body: JSON.stringify({
                message,
            }),
        };
    }
};
