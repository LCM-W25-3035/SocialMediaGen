import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import datetime

# Function to connect to MongoDB
def connect_mongo():
    try:
        client = MongoClient("mongodb+srv://Muskan:MUSKAN25@newsanalytics.rzmco.mongodb.net/?retryWrites=true&w=majority&appName=NEWSANALYTICS")
        db = client["news_database"]
        collection = db["bbc_headlines"]
        return collection
    except Exception as e:
        print("Error connecting to MongoDB:", e)
        return None

# Function to scrape description from an individual article
def scrape_article_description(link):
    try:
        response = requests.get(link)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Extract description from meta tag
            description_tag = soup.find('meta', attrs={"name": "description"})
            if description_tag and description_tag.get("content"):
                return description_tag["content"]
            else:
                return "No description available."
        else:
            return "Failed to fetch article."
    except Exception as e:
        print(f"Error scraping description for {link}: {e}")
        return "Error fetching description."

# Function to scrape BBC News headlines
def scrape_bbc_news():
    url = "https://www.bbc.com/news"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # Find all headline elements (assumed to be in <h2> tags)
            headlines = soup.select('h2')
            if not headlines:
                print("No headlines found. The page structure may have changed.")
                return []
            
            news_list = []
            for headline in headlines:
                title = headline.get_text(strip=True)
                link_tag = headline.find_parent('a')  # Get the parent anchor tag for the link
                link = link_tag['href'] if link_tag else ''
                full_link = f"https://www.bbc.com{link}" if link.startswith('/') else link
                
                # Skip empty links
                if full_link.strip():
                    summary = scrape_article_description(full_link)
                    news_item = {
                        "Headline": title,
                        "Link": full_link,
                        "Summary": summary,
                        "Timestamp": datetime.datetime.now().isoformat()
                    }
                    news_list.append(news_item)
            
            return news_list
        else:
            print(f"Failed to retrieve BBC News. Status code: {response.status_code}")
            return []
    
    except Exception as e:
        print("Error occurred while scraping BBC News:", e)
        return []

# Function to store news in MongoDB 
def store_in_mongo(news_data):
    collection = connect_mongo()
    if collection is not None:
        inserted_count = 0
        for news in news_data:
            collection.insert_one(news)
            inserted_count += 1
        print(f"Inserted {inserted_count} new articles into MongoDB.")
    else:
        print("Failed to connect to MongoDB.")

# Callable function to run the scraper and store data
def run_bbc_scraper():
    print("Starting BBC News scraping...")
    news_data = scrape_bbc_news()
    
    if news_data:
        for news in news_data:
            print(f"Headline: {news['Headline']}\nLink: {news['Link']}\nSummary: {news['Summary']}\nTimestamp: {news['Timestamp']}\n")
        store_in_mongo(news_data)
    else:
        print("No news articles scraped.")

# This allows the function to be called when running the script directly
if __name__ == "__main__":
    run_bbc_scraper()
