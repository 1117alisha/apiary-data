import requests
from pymongo import MongoClient
from datetime import datetime
import csv
import io

client = MongoClient("mongodb://localhost:27017/")
db = client["apiary"]


if "diy_sensor_data" not in db.list_collection_names():
    db.create_collection("diy_sensor_data", timeseries={
        "timeField": "timestamp",
        "metaField": "hive",
        "granularity": "minutes"
    })

collection = db["diy_sensor_data"]

hives = {
    "B": "2b9680f6b54ccc45",
    "C": "3d0d8721b29bbed2",
    "E": "c14dc33a38ef5474"
}

for hive, monitor_id in hives.items():
    print(f"📡 Fetching data for Hive {hive}...")
    url = f"https://beehive.gccis.rit.edu/api/monitor/{hive}?limit=1000"
    response = requests.get(url)

    if response.status_code == 200:
        raw_text = response.text.strip()
        if raw_text.startswith("monitor id"):
            reader = csv.DictReader(io.StringIO(raw_text), delimiter='|')
            inserted = 0
            for row in reader:
                try:
                    timestamp = datetime.fromisoformat(row["timestamp"])
                    doc = {
                        "hive": hive,
                        "timestamp": timestamp,
                        "hive_temp": int(row["hive temp"]),
                        "hive_humidity": int(row["hive humidity"]),
                        "hive_acoustics": int(row["hive acoustics"]),
                        "external_temp": int(row["external temp"]),
                        "external_pressure": int(row["external pressure"]),
                        "battery_life": int(row["battery life"]),
                        "monitor_id": row["monitor id"]
                    }
                    collection.insert_one(doc)
                    inserted += 1
                except Exception as e:
                    print("Skipping row:", e)
            print(f"Inserted {inserted} rows for Hive {hive}")
        else:
            print("Unexpected format or empty data for Hive", hive)
    else:
        print(f"Request failed for Hive {hive} (Status: {response.status_code})")
