#!/usr/bin/env python3
import csv
import json
import sys
import time
import requests

ES_HOST = "http://elasticsearch-test:9200"
INDEX = "products"
CSV_PATH = "/data/ES_products.csv"
BULK_PATH = "/tmp/bulk.json"

def wait_for_es():
    url = f"{ES_HOST}/_cluster/health?wait_for_status=yellow&timeout=60s"
    while True:
        try:
            r = requests.get(url)
            if r.status_code == 200:
                print("Elasticsearch is up")
                return
        except:
            pass
        print("Waiting for Elasticsearch…")
        time.sleep(1)

def csv_to_bulk():
    with open(CSV_PATH, newline='', encoding='utf-8') as f_csv, open(BULK_PATH, 'w', encoding='utf-8') as f_bulk:
        reader = csv.DictReader(f_csv)
        for row in reader:
            # 假设 CSV 第一列是 "id"，其余列都当字符串处理
            doc_id = row.pop("id", None) or ""
            action = { "index": { "_index": INDEX, "_id": doc_id } }
            f_bulk.write(json.dumps(action, ensure_ascii=False) + "\n")
            f_bulk.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"Bulk file written to {BULK_PATH}")

def import_bulk():
    with open(BULK_PATH, 'rb') as f:
        resp = requests.post(f"{ES_HOST}/_bulk", data=f,
                             headers={"Content-Type": "application/x-ndjson"})
    print("Bulk import response:", resp.status_code, resp.text)

if __name__ == "__main__":
    wait_for_es()
    csv_to_bulk()
    import_bulk()
    print("Import complete.")
