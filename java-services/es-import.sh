#!/bin/sh
# 等待 Elasticsearch 就绪
echo "Waiting for Elasticsearch to be available…"
until curl -s http://elasticsearch-test:9200/_cluster/health?wait_for_status=yellow > /dev/null; do
  sleep 1
done
echo "Elasticsearch is up—importing ES_products.csv…"

# 将 CSV 转为 Bulk API 格式并导入
# 第一列假设是 id，后面字段将作为 JSON
tail -n +2 /data/ES_products.csv | \
  awk -F',' '{ printf("{\"index\":{\"_index\":\"products\",\"_id\":\"%s\"}}\n", $1); printf("{\"field1\":\"%s\",\"field2\":\"%s\",\"field3\":%s}\n", $2, $3, $4) }' \
  > /data/bulk.json

curl -s -H "Content-Type: application/x-ndjson" \
     -XPOST http://elasticsearch-test:9200/_bulk --data-binary @/data/bulk.json

echo "Import complete."
