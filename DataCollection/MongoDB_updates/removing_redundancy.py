#!/usr/bin/env python
# coding: utf-8

# In[2]:


"""Prompts:
1st:
want to perform deduplication based on id and link

last:
how to delete collection and database in mongodb
"""
from pymongo import MongoClient

# Connecting to MongoDB
client = MongoClient("mongodb+srv://Govind:*******@projectnewsanalytics.kdevn.mongodb.net/?retryWrites=true&w=majority&appName=ProjectNewsAnalytics")

# source and destination collections
source_db = client["News_Api"]
destination_db = client["news_database"]

source_collection1 = source_db["News_data"]
source_collection2 = destination_db["NewsApi"]
destination_collection = destination_db["Newsapi_data"]

# Fetching all documents from source collections
documents = list(source_collection1.find()) + list(source_collection2.find())

# Deduplication (checking by '_id' and 'link')
inserted_count = 0
for doc in documents:
    query = {"$or": [{"_id": doc["_id"]}, {"link": doc.get("link")}]}

    # Insert only if no duplicate is found
    if not destination_collection.find_one(query):
        destination_collection.insert_one(doc)
        inserted_count += 1

print(f"Successfully moved {inserted_count} new documents. Duplicates were ignored.")

#dropping 'News_Api' database and 'NewsApi' collection to remove redundancy 
client.drop_database("News_Api")
source_collection2.drop()

# Close the connection
client.close()


# In[ ]:




