from pymongo import MongoClient

client = MongoClient()
db = client["apiary"]
original = db["diy_sensor_data"]
reshaped = db["diy_sensor_data_reshaped"]


metrics = {
    "hive_temp": "Hive Temperature",
    "hive_humidity": "Hive Humidity",
    "hive_acoustics": "Hive Acoustics",
    "external_temp": "External Temperature",
    "external_pressure": "External Pressure",
    "battery_life": "Battery Life"
}

count = 0
for doc in original.find():
    for field, metric_name in metrics.items():
        if field in doc and doc[field] is not None:
            reshaped.insert_one({
                "timestamp": doc["timestamp"],
                "hive": doc["hive"],
                "metric": metric_name,
                "value": float(doc[field])
            })
            count += 1

print(f"Reshaped and inserted {count} documents.")
