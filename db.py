from pymongo import MongoClient
client = MongoClient("mongodb+srv://nguyentran186:tkbd1752003@printer-db.3x2fjj1.mongodb.net/?retryWrites=true&w=majority")
db = client.get_database('CN')
records = db.Client_Info

def matching():
    cursor = records.find({"file_name":"image.png"})
    for record in cursor:
        print(record)

matching()
