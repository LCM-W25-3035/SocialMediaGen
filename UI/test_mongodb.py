import pymongo

client = pymongo.MongoClient("mongodb+srv://jashanpreetkaur:jashangill@newsanalytics.rq1k3.mongodb.net/?retryWrites=true&w=majority&appName=NewsAnalytics")
db = client['news_database']
collection = db['cnn_news']

# Test connection by fetching one document
print(collection.find_one())