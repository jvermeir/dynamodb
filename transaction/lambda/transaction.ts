import { dynamoDB } from "./database";

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

export const handler = async (event: any, context: any) => {
  const method = event.httpMethod;

  try {
    if (method === "GET") {
      const queryStringParameters = event.queryStringParameters;
      console.log(
        `queryStringParameters: ${JSON.stringify(queryStringParameters)}`
      );
      if (queryStringParameters?.id) {
        return queryById(queryStringParameters.id);
      } else {
        return queryByOwner(queryStringParameters.owner);
      }
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
