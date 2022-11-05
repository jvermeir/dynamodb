#SRC_ROOT=$(git rev-parse --show-toplevel)
REGISTRY=${ACCOUNT_ID}.dkr.ecr.eu-central-1.amazonaws.com

#cd $SRC_ROOT

docker build . -t test
docker tag test:latest {$REGISTRY}/test:latest

aws ecr get-login-password --region eu-central-1 | docker login --username AWS --password-stdin {$REGISTRY}
docker push {$REGISTRY}/test:latest
