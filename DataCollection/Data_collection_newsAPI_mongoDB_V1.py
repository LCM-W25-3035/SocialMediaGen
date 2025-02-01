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
db = Client['News_Api']             # Creating a database in mongoDB 'NewsApi'
collection = db['News_data']       # Creating a collection 'News_data' in database 'NewsApi'

# API keys
api_keys = ['*************************','*************************','*************************','*****************************','******************************','***********************']

# Categories and Sources
categories = ['technology', 'sports', 'entertainment', 'politics', 'business']
category_sources = {
    'technology': ['techcrunch', 'the-verge', 'wired', 'ars-technica', 'engadget', 'gruenderszene'],
    'sports': ['espn', 'bbc-sport', 'fox-sports', 'four-four-two', 'bleacher-report', 'nfl-news'],
    'entertainment': ['buzzfeed', 'mtv-news', 'entertainment-weekly', 'polygon', 'ign', 'the-lad-bible'],
    'politics': ['cnn', 'bbc-news', 'reuters', 'politico', 'the-hill', 'the-washington-times'],
    'business': ['business-insider', 'the-wall-street-journal', 'bloomberg', 'fortune', 'financial-post', 'les-echos']
}


def fetch_news():
    s_time = time.time()
    today = datetime.now()
    last_week = today - timedelta(days=7)
    from_date = last_week.strftime('%Y-%m-%d')
    to_date = today.strftime('%Y-%m-%d')

    total_keys = len(api_keys)
    key_index = 0
    source_indices = {category: 0 for category in categories}  # Track source index per category
    
    while True:  # This will run the process in a loop every 5 minutes
        for category in categories:
            sources = category_sources[category]
            num_sources = len(sources)

            for _ in range(num_sources):
                source_index = source_indices[category] % num_sources  # Rotate sources per category
                source = sources[source_index]
                source_indices[category] += 1  # Move to next source in next iteration
                
                api_key = api_keys[key_index % total_keys]
                print(f"Using API key {key_index + 1}: {api_key}, Source: {source}")
                news_api = NewsApiClient(api_key=api_key)

                articles_fetched = False

                print(f"Fetching articles from source {source} for category {category}")
                try:
                    response = news_api.get_everything(
                        sources=source,         # Specify sources directly
                        from_param=from_date,    # Date range for fetching news
                        to=to_date,             # Date range for fetching news
                        page=1,                 # Start from page 1
                        page_size=16,           # Fetch 16 articles per page
                        language='en'           # Specifying language as english
                    )
                    if 'articles' in response and response['articles']:
                        for article in response['articles']:
                            # Add category field to article
                            article['category'] = category

                            # Check for duplicate URL in the database
                            if not collection.find_one({'url': article['url']}):
                                collection.insert_one(article)
                                print(f"Inserted: {article['title']}")
                            else:
                                print(f"Duplicate: {article['title']}")
                        articles_fetched = True
                    else:
                        print(f"No articles found for source: {source}")
                except Exception as e:
                    print(f"Error fetching articles from source {source} for category {category}: {e}")

                if not articles_fetched:
                    print(f"No articles found for category {category} from source {source}, switching to next source.")
                key_index = (key_index + 1) % total_keys  # Rotate API keys

        e_time = time.time()
        print(f'Fetch complete! Time taken: {e_time - s_time:.2f} seconds')


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
