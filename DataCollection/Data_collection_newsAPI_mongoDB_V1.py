#!/usr/bin/env python
# coding: utf-8


# Importing necessary liabraris
from pymongo import MongoClient
from newsapi import NewsApiClient
import pymongo
from datetime import timedelta, datetime
from apscheduler.schedulers.blocking import BlockingScheduler
import time

# connecting to MongoDB clusters
Client = MongoClient('mongodb+srv://Govind:*******@projectnewsanalytics.kdevn.mongodb.net/?retryWrites=true&w=majority&appName=ProjectNewsAnalytics')

# creating a database and collection in mongoDB
db = Client['NewsApi']             # Creating a database in mongoDB 'NewsApi'
collection = db['News_data']       # Creating a collection 'News_data' in database 'NewsApi'

# API keys
api_keys = ['*************************','*************************','*************************']

# defining a new variable to hold the current key index
current_key_index = 0 

# Function to fetch news and store in MongoDB
def fetch_news():
    s_time = time.time() #time function starts at
    
    global current_key_index #Use golbal variable

    # Selecting the current API key
    current_api_key = api_keys[current_key_index]
    print(f"Using API key: {current_api_key}")

    # Initialize NewsApiClient with the current key
    news_api = NewsApiClient(api_key=current_api_key)

    # Changing to next key for next turn
    current_key_index = (current_key_index + 1) % len(api_keys)

    # Specifying from and to dates for news fetching
    today = datetime.now()
    last_week = today - timedelta(days=7)
    from_date = last_week.strftime('%Y-%m-%d')
    to_date = today.strftime('%Y-%m-%d')

    for req in range(1, 101):  # As free limit is 100 requests per key per day
        try:
            # Fetching data from the API
            response = news_api.get_everything(q='news', from_param=from_date, to=to_date, page=req, page_size=100)

            if 'articles' in response and response['articles']:  # Check if articles exist
                for article in response['articles']:
                    # Checking if the article already exists in the collection based on the url
                    if collection.find_one({'url': article['url']}):
                        print(f"Article already exists (duplicate): {article['title']}")
                    else:
                        # Insert the article if it doesn't exist
                        collection.insert_one(article)
                        print(f"Article inserted: {article['title']}")
            else:
                print(f'Page {req}: No articles returned.')
                break

        except Exception as e:
            print(f'Page {req}: Error occurred - {e}')
            break
                      
    e_time = time.time()               # time function ends at
    total_time_taken = s_time - e_time # to calculate time taken in fetching data 
    print('Fetch complete!, time taken:',total_time_taken')


# APScheduler setup
def start_scheduler():
    scheduler = BlockingScheduler()

    # Schedule the fetch_news function to run every 5 minutes
    scheduler.add_job(fetch_news, 'interval', minutes=5)

    print('Scheduler started. Fetching news every 5 minutes...')
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print('Scheduler stopped.')
        Client.close()


if __name__ == '__main__':
    start_scheduler()
