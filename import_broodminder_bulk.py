import csv
from pymongo import MongoClient
from datetime import datetime
import os

client = MongoClient("mongodb://localhost:27017/")
db = client["apiary"]
collection = db["broodminder_data"]


device_map = {
    "56:40:52": {"hive": "C", "sensor": "upper-brood"},
    "56:40:58": {"hive": "B", "sensor": "upper-brood"},
    "56:40:59": {"hive": "E", "sensor": "upper-brood"},
    "63:06:7C": {"hive": "E", "sensor": "outside-hive"},
    "63:06:7D": {"hive": "B", "sensor": "outside-hive"},
}

for filename in os.listdir():
    if filename.endswith(".csv"):
        print(f"Reading {filename}")
        with open(filename, newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    
                    uuid = row.get("UUID", "").strip()
                    temp_f = float(row["Temperature"]) if row["Temperature"] else None
                    timestamp = datetime.strptime(row["Local_TimeStamp"], "%m/%d/%Y %I:%M %p")

                    if uuid in device_map and temp_f is not None:
                        doc = {
                            "device_id": uuid,
                            "hive": device_map[uuid]["hive"],
                            "sensor": device_map[uuid]["sensor"],
                            "timestamp": timestamp,
                            "temperature_f": temp_f
                        }
                        collection.insert_one(doc)
                    else:
                        print(f"Skipped row: unknown UUID or missing temperature → {uuid}")
                except Exception as e:
                    print("Error:", e)

print("Import finished.")
