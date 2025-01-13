#!/usr/bin/env python
# coding: utf-8


from newsapi import NewsApiClient
import pandas as pd
import requests
from pymongo import MongoClient
from datetime import datetime, timedelta



# MongoDB connection
client = MongoClient("mongodb+srv://Govind:*******@projectnewsanalytics.kdevn.mongodb.net/?retryWrites=true&w=majority&appName=ProjectNewsAnalytics")
db = client["NewsApi_data"] #Created a database 'NewsApi_data'
collection = db["news_data"] #Created a collection 'News_data'



# News API
news_api = NewsApiClient(api_key = '***************')  #fill API key  
MAX_REQUESTS = 100                                                       # As free limit is 100 pages per day
REQUESTS_MADE = 0                                                        # Track requests made



# Date range for the past week
today = datetime.now()
last_week = today - timedelta(days=7)
from_date = last_week.strftime("%Y-%m-%d")
to_date = today.strftime("%Y-%m-%d")


# Fetch news article
for req in range(1, 101): # as we have max 100 requests
    try:
        # Fetching data from the API
        response = news_api.get_everything(q="news", from_param=from_date, to=to_date, page=1, page_size=100) 

        if "articles" in response and response["articles"]:              # To check if we have key called article in response
            # Save articles to MongoDB
            collection.insert_many(response["articles"])                 # inserting key 'article' in our collection
            print(f"Page {page}: {len(response['articles'])} articles saved.")
        else:
            print(f"Page {page}: No articles returned.")
            break

    except Exception as e:
        print(f"Page {page}: Error occurred - {e}")
        break
        
print('Done!!!!')


client.close()

