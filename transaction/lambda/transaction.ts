import {dynamoDB} from "./database";

const queryById = async (id: string) => {
    const transaction = await dynamoDB.getTransaction(id);
    console.log(`found transaction: ${JSON.stringify(transaction)}`);
    const body = {
        transaction,
    };
    return {
        statusCode: 200,
        headers: {},
        body: JSON.stringify(body),
    };
};

const updateAndGetTotal = async (owner: string) => {
    const total = await dynamoDB.getTotalByOwner(owner);
    console.log(`found total: ${JSON.stringify(total)}`);
    const body = {
        total,
    };
    return {
        statusCode: 200,
        headers: {},
        body: JSON.stringify(body),
    };
};

const queryByOwner = async (owner: string) => {
    const transactions = await dynamoDB.getTransactionsByOwner(owner);
    console.log(`found transactions: ${JSON.stringify(transactions)}`);
    const body = {
        transactions,
    };
    return {
        statusCode: 200,
        headers: {},
        body: JSON.stringify(body),
    };
};

const saveTransaction = async (transactionAsJson: string) => {
    console.log(`transactionAsJson: ${transactionAsJson}`);
    const transaction = JSON.parse(transactionAsJson);
    console.log(`save transaction: ${JSON.stringify(transaction)}`);
    const transactionSaved = await dynamoDB.saveTransaction(transaction);
    console.log(transactionSaved);
    return {
        statusCode: 200,
        body: JSON.stringify({
            message: `saved ${JSON.stringify(transactionSaved)}`,
        }),
    };
};

export const handler = async (event: any) => {
    const method = event.httpMethod;

    try {
        if (method === "GET") {
            const queryStringParameters = event.queryStringParameters;
            console.log(
                `queryStringParameters: ${JSON.stringify(queryStringParameters)}, event.path: ${event.path}`
            );
            if (event.path.indexOf("/total") >= 0) {
                console.log(`find total for: ${queryStringParameters.owner}`);
                return updateAndGetTotal(queryStringParameters.owner);
            }
            if (queryStringParameters?.id) {
                console.log(`find transaction by id: ${queryStringParameters.id}`);
                return queryById(queryStringParameters.id);
            }
            if (queryStringParameters?.owner) {
                console.log(`find transactions by owner: ${queryStringParameters.owner}`);
                return queryByOwner(queryStringParameters.owner);
            }
            return {
                statusCode: 500,
                body: JSON.stringify({
                    message: `path ${event} not supported`,
                }),
            };
        } else if (method === "POST") {
            const transactionParam = event.body;
            return saveTransaction(transactionParam);
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
