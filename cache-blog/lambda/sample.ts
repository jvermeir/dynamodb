import {CacheItem, dynamoDB} from "./database";

/*
    This example shows how to use the cache table from typescript code.
    In the context of a lambda, the cache methods can be used without the lambda.
 */

(async () => {
    await dynamoDB.saveCacheItem({ id: 'myId', value: 'myValue' } as CacheItem);
    const cacheItem = await dynamoDB.getCacheItem('myId');
    console.log(cacheItem);
})();
