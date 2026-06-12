from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)
CORS(app)

client = MongoClient("mongodb://localhost:27017/")
db = client["apiary"]

@app.route("/")
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route("/data")
def get_data():
    source = request.args.get("source")
    hive = request.args.get("hive")
    metric = request.args.get("metric")
    start = request.args.get("start")
    end = request.args.get("end")

    if not all([source, hive, metric, start, end]):
        return jsonify([])

    start_date = datetime.strptime(start, "%Y-%m-%d")
    end_date = datetime.strptime(end, "%Y-%m-%d")

    if source == "BroodMinder":
        collection = db.broodminder_ts
        field_map = {
            "Hive Temperature": "temperature_f",
            "Hive Humidity": "humidity",
            "External Temperature": "external_temp",
            "External Pressure": "external_pressure",
            "Battery Life": "battery_life",
            "Hive Acoustics": "acoustics"
        }

        if metric not in field_map:
            return jsonify([])

        field_name = field_map[metric]

        match_stage = {
            "$match": {
                "hive": hive,
                "timestamp": {"$gte": start_date, "$lte": end_date},
                field_name: {"$exists": True, "$nin": [255, -128, 0, None]}
            }
        }

        project_stage = {
            "$project": {
                "timestamp": 1,
                "value": f"${field_name}",
                "_id": 0
            }
        }

        results = list(collection.aggregate([match_stage, project_stage]))

    else:  # DIY
        collection = db.diy_sensor_data_reshaped
        results = list(collection.find({
            "hive": hive,
            "metric": metric,
            "timestamp": {"$gte": start_date, "$lte": end_date}
        }, {
            "_id": 0,
            "timestamp": 1,
            "value": 1
        }))
    print(f"Results returned: {len(results)} for {source} - {metric}")

    return jsonify(results)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
