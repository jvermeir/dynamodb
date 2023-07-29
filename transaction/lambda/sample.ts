import {dynamoDB, Transaction} from "./database";

(async () => {
    await dynamoDB.saveTransaction({
        id: 'owner2-1',
        amount: 10,
        owner: 'owner2',
        createdAt: 1,
    } as Transaction);
    await dynamoDB.saveTransaction({
        id: 'owner2-2',
        amount: 11,
        owner: 'owner2',
        createdAt: 2,
    } as Transaction);
    const step1Transactions = await dynamoDB.getTransactionsByOwner('owner2');
    const step1Total = await dynamoDB.getTotalByOwner('owner2');
    console.log(`step1Transactions: ${step1Transactions}`);

    const transaction = await dynamoDB.getTransaction('myId');
    console.log(transaction);

    const transactions = [
        {
            id: 'owner1-1',
            amount: 11,
            owner: 'owner1',
        } as Transaction,
        {
            id: 'owner1-1',
            amount: 10,
            owner: 'owner1',
        } as Transaction,
        {
            id: 'owner1-1',
            amount: 10,
            owner: 'owner1',
            type: 'summary',
        } as Transaction,
        {
            id: 'owner1-1',
            amount: 5,
            owner: 'owner1',
        } as Transaction,
        {
            id: 'owner1-1',
            amount: 5,
            owner: 'owner1',
            type: 'summary',
        } as Transaction,
        {
            id: 'owner1-1',
            amount: 5,
            owner: 'owner1',
        } as Transaction,
    ];
    const total = transactions.reduce((a, b) => {
        return { amount: a.amount + b.amount } as Transaction;
    });

    console.log(total);

    let t = 0;
    transactions.every((transaction) => {
        t += transaction.amount;
        return transaction.type !== 'summary';
    });
    console.log(t);
})();
