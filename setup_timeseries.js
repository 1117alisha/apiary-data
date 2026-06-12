const connection = new Mongo( `localhost:27017` ),
        db = connection.getDB( `apiary` );
        

db.createCollection("broodminder_ts", {
  timeseries: {
    timeField: "timestamp",
    metaField: "hive",
    granularity: "minutes"
  }
});
print("Time-series collection created.");


const count = db.broodminder_data.countDocuments();
let copied = 0;

db.broodminder_data.find().forEach(doc => {
  db.broodminder_ts.insertOne(doc);
  copied++;
});

print(` Copied ${copied} out of ${count} documents to time-series collection.`);


const sample = db.broodminder_ts.findOne();
print(" Sample document from time-series collection:");
printjson(sample);
