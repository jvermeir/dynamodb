# Query transaction by id

host=$1
id=$2

if [ -z "$host" ] || [ -z "$id" ]; then
  echo "Usage: $0 <host> <id>"
  exit 1
fi

curl https://${host}.execute-api.eu-central-1.amazonaws.com/prod/?id\=${id}
