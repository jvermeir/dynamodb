# Store a bunch of test data in the database.

for i in {1..100} ; do
  data="{ \"id\": \"record-$i\", \"amount\":\"$i\", \"owner\": \"owner1\"}"
  echo $data
  curl -X POST https://n60qtqvldf.execute-api.eu-central-1.amazonaws.com/prod/ -H "Accept: application/json" -d "$data"
done