rm -rf build
mkdir -p build
cp create-table.py build/
cp JansTestLambda.py build/
cat JansTestLambdaRole-Policy.json | sed "s/ACCOUNT_ID/${ACCOUNT_ID}/g" > build/JansTestLambda-Policy.json
