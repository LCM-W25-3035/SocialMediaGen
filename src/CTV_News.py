import requests
from bs4 import BeautifulSoup
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# MongoDB Connection
uri = "mongodb+srv://katharotiyaashish9:Mongodb2025@newsdata.mlwzc.mongodb.net/?retryWrites=true&w=majority&appName=Newsdata"

# Create a MongoDB client with Server API version 1
client = MongoClient(uri, server_api=ServerApi('1'))

# Check if the connection to MongoDB is successful
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(f"MongoDB Connection Error: {e}")

# Select the database and collection
db = client['Newsdata']
collection = db['articles']

def is_duplicate(headline):
    """
    Checks if an article with the same headline already exists in the database.
    Returns True if the article is already present, otherwise False.
    """
    return collection.find_one({"headline": headline}) is not None

def web_scraping(url):
    """
    Scrapes news articles from the given website URL.
    
    Parameters:
        url (str): The URL of the news website to scrape.

    Returns:
        list: A list of dictionaries containing news articles' data (headline, link, image, and summary).
    """
    # Send a GET request to fetch the HTML content of the webpage
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code != 200:
        print("Failed to retrieve the webpage")
        return None
    
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find all article containers (adjust class name based on the actual website structure)
    articles = soup.find_all('div', class_='c-stack')
    
    news_list = []  # List to store the scraped news articles

    for article in articles:
        # Extract headline
        headline_tag = article.find('h2', class_='c-heading')
        headline = headline_tag.text.strip() if headline_tag else None

        # Skip if no headline or if the article is already in the database
        if not headline or is_duplicate(headline):
            continue
        
        # Extract article link
        link_tag = article.find('a', class_='c-link')
        link = link_tag['href'] if link_tag and 'href' in link_tag.attrs else None

        # Extract image URL
        img_tag = article.find('img', class_='c-image')
        img_url = img_tag['src'] if img_tag and 'src' in img_tag.attrs else None

        # Extract article summary
        summary_tag = article.find('p', class_='c-paragraph')
        summary = summary_tag.text.strip() if summary_tag else None

        # Skip articles containing videos
        if article.find('video'):
            continue

        # Create a dictionary to store article details
        news_item = {
            'headline': headline,
            'link': link,
            'image_url': img_url,
            'summary': summary
        }
        
        news_list.append(news_item)  # Add the article to the list

    return news_list  # Return the list of scraped articles

def data_upload(news_list):
    """
    Uploads the scraped news articles to MongoDB.

    Parameters:
        news_list (list): A list of dictionaries containing news articles.
    """
    if not news_list:
        print("No new articles to upload.")
        return
    
    try:
        # Insert the list of articles into MongoDB in bulk
        collection.insert_many(news_list)
        print(f"Successfully inserted {len(news_list)} articles into MongoDB.")
    except Exception as e:
        print(f"Error inserting data into MongoDB: {e}")

# Example usage
url = "https://www.ctvnews.ca/"  # News website URL to scrape
news_data = web_scraping(url)  # Scrape the news data
data_upload(news_data)  # Upload the data to MongoDB
