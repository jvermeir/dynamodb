rm -rf build
mkdir -p build
cp create-table.py build/
cp JansTestLambda.py build/
cat JansTestLambdaRole-Policy.json | sed "s/ACCOUNT_ID/${ACCOUNT_ID}/g" > build/JansTestLambdaRole-Policy.json
cp trust-policy.json build/

cd build
aws iam create-policy --policy-name jans-test-lambda-policy --policy-document file://JansTestLambdaRole-Policy.json
aws iam attach-role-policy --role-name lambda-ex --policy-arn arn:aws:iam::${ACCOUNT_ID}:policy/jans-test-lambda-policy
cd -
