# Adds a transaction
#
# ex: ./tools/add_transaction.sh l86omzmsi0 "{ \"id\": \"owner2-id\", \"amount\":1, \"owner\":\"owner2\"}"

host=$1
data=$2

if [ -z "$host" ] || [ -z "$data" ]; then
  echo "Usage: $0 <host> <data>"
  exit 1
fi

curl -X POST https://${host}.execute-api.eu-central-1.amazonaws.com/prod/ -H "Accept: application/json" -d "${data}"
