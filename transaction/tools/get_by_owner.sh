# Query transactions by owner

host=$1
owner=$2

if [ -z "$host" ] || [ -z "$owner" ]; then
  echo "Usage: $0 <host> <owner>"
  exit 1
fi

curl https://${host}.execute-api.eu-central-1.amazonaws.com/prod/?owner\=${owner}
