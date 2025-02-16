{
 "cells": [
  {
   "cell_type": "markdown",
   "id": "0c0ab217-5c7e-45e1-a941-2272cd079d43",
   "metadata": {},
   "source": [
    "code is leveraged from Chatgpt AI\n",
    "prompt:-\n",
    "<section class=\"story-wrapper\"><a class=\"css-9mylee\" href=\"https://www.nytimes.com/live/2025/01/30/us/president-trump-news\" data-uri=\"nyt://legacycollection/d74d7a3b-90cc-5476-8a88-97c05fc5812d\" aria-hidden=\"false\"><div class=\"css-xdandi\"><div class=\"css-1a3ibh4\"><p class=\"css-ae0yjg\"><span class=\"css-12tlih8\">LIVE</span></p><span class=\"css-1ufpbe9\"><time class=\"css-16lxk39\" datetime=\"2025-02-01T03:02:35.187Z\"><div class=\"css-ki347z\"><span aria-hidden=\"true\" data-time=\"abs\" class=\"css-1stvlmo\">Jan. 31, 2025, 10:02 p.m. ET</span><span data-time=\"rel\" class=\"css-kpxlkr\">3m ago</span></div></time></span></div><p class=\"indicate-hover css-1gg6cw2\">Justice Dept. Fires Jan. 6 Prosecutors Amid Campaign of Retribution by Trump</p></div><p class=\"summary-class css-ofqxyv\">The administration also plans to scrutinize thousands of F.B.I. agents tied to the investigations of President Trump and his supporters, according to people familiar with the matter.</p><p class=\"css-ih99h\">See more updates ›</p></a></section>\n",
    "\n",
    "this is my html code for this website for a particular headline I want to fetch all the news articles ,headlines and summary ,links and time stamps of the following site\n",
    "can you make me a python script for web scrapping the data from the site \n",
    "if any of the conditions doesnt fulfill make it null\n",
    "and this is the url of the site - \"https://www.nytimes.com/\"\n",
    "\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "id": "cbcc4267-845b-4809-adfb-56970899507b",
   "metadata": {},
   "outputs": [],
   "source": [
    "import requests  # Library for making HTTP requests\n",
    "from bs4 import BeautifulSoup  # Library for parsing HTML content\n",
    "from pymongo import MongoClient  # Library for interacting with MongoDB"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 6,
   "id": "726f8584-00bf-4be4-b64f-ad9ec5646010",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Function to fetch news from NYTimes and store it in MongoDB\n",
    "def fetch_and_store_nytimes_news():\n",
    "    try:\n",
    "        # Connecting to MongoDB\n",
    "        client = MongoClient(\"mongodb+srv://shlokshah2897:Qwerty1234@cluster0.z8pxj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0\")\n",
    "        db = client[\"news_db\"]  # Create or access the database\n",
    "        collection = db[\"nytimes_news\"]  # Create or access the collection\n",
    "        \n",
    "        # Defining the NYTimes homepage URL\n",
    "        url = \"https://www.nytimes.com/\"\n",
    "        headers = {'User-Agent': 'Mozilla/5.0'}  # Set headers to avoid blocking\n",
    "        response = requests.get(url, headers=headers)  # Make a GET request to the website\n",
    "        \n",
    "        # Checking if the request was successful\n",
    "        if response.status_code != 200:\n",
    "            print(\"Failed to retrieve the webpage\")\n",
    "            return\n",
    "        \n",
    "        # Parsing the HTML content of the page\n",
    "        soup = BeautifulSoup(response.text, 'html.parser')\n",
    "        articles = []  # List to store extracted articles\n",
    "        \n",
    "        # Finding all sections containing news articles\n",
    "        for item in soup.find_all('section', class_='story-wrapper'):\n",
    "            headline = item.find('p', class_='indicate-hover')  # Extract headline\n",
    "            summary = item.find('p', class_='summary-class')  # Extract summary\n",
    "            link = item.find('a', href=True)  # Extract link to the article\n",
    "            timestamp = item.find('time', class_='css-16lxk39')  # Extract timestamp\n",
    "            \n",
    "            # Creating a dictionary to store article details\n",
    "            article = {\n",
    "                'headline': headline.text.strip() if headline else None,  # Store headline if found\n",
    "                'summary': summary.text.strip() if summary else None,  # Store summary if found\n",
    "                'link': f\"https://www.nytimes.com{link['href']}\" if link else None,  # Store full article link\n",
    "                'timestamp': timestamp.text.strip() if timestamp else None  # Store timestamp if found\n",
    "            }\n",
    "            \n",
    "            # Add only articles that have a headline\n",
    "            if article['headline']:\n",
    "                articles.append(article)\n",
    "        \n",
    "        # Insert the extracted articles into MongoDB if there are any\n",
    "        if articles:\n",
    "            collection.insert_many(articles)\n",
    "            print(\"Data successfully inserted into MongoDB.\")\n",
    "        else:\n",
    "            print(\"No valid data to insert.\")\n",
    "        \n",
    "    except Exception as e:\n",
    "        print(\"Error:\", e)  # Print any exceptions that occur\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 8,
   "id": "2d385812-1355-4a0c-943c-1270a8893d75",
   "metadata": {},
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "C:\\Users\\User\\anaconda3\\Lib\\site-packages\\pymongo\\ocsp_support.py:228: CryptographyDeprecationWarning: Properties that return a naïve datetime object have been deprecated. Please switch to this_update_utc.\n",
      "  if response.this_update > now:\n",
      "C:\\Users\\User\\anaconda3\\Lib\\site-packages\\pymongo\\ocsp_support.py:232: CryptographyDeprecationWarning: Properties that return a naïve datetime object have been deprecated. Please switch to next_update_utc.\n",
      "  if response.next_update and response.next_update < now:\n",
      "C:\\Users\\User\\anaconda3\\Lib\\site-packages\\pymongo\\ocsp_cache.py:54: CryptographyDeprecationWarning: Properties that return a naïve datetime object have been deprecated. Please switch to next_update_utc.\n",
      "  if value.next_update is None:\n",
      "C:\\Users\\User\\anaconda3\\Lib\\site-packages\\pymongo\\ocsp_cache.py:59: CryptographyDeprecationWarning: Properties that return a naïve datetime object have been deprecated. Please switch to this_update_utc.\n",
      "  if not (value.this_update <= _datetime.utcnow()\n",
      "C:\\Users\\User\\anaconda3\\Lib\\site-packages\\pymongo\\ocsp_cache.py:60: CryptographyDeprecationWarning: Properties that return a naïve datetime object have been deprecated. Please switch to next_update_utc.\n",
      "  < value.next_update):\n",
      "C:\\Users\\User\\anaconda3\\Lib\\site-packages\\pymongo\\ocsp_cache.py:67: CryptographyDeprecationWarning: Properties that return a naïve datetime object have been deprecated. Please switch to next_update_utc.\n",
      "  cached_value.next_update < value.next_update):\n",
      "C:\\Users\\User\\anaconda3\\Lib\\site-packages\\pymongo\\ocsp_cache.py:82: CryptographyDeprecationWarning: Properties that return a naïve datetime object have been deprecated. Please switch to this_update_utc.\n",
      "  if (value.this_update <= _datetime.utcnow() <\n",
      "C:\\Users\\User\\anaconda3\\Lib\\site-packages\\pymongo\\ocsp_cache.py:83: CryptographyDeprecationWarning: Properties that return a naïve datetime object have been deprecated. Please switch to next_update_utc.\n",
      "  value.next_update):\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Data successfully inserted into MongoDB.\n"
     ]
    }
   ],
   "source": [
    "# Call the function to execute the scraping and storage process\n",
    "fetch_and_store_nytimes_news()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "7ecd42b9-d647-43c8-8369-011cb90b8a96",
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python [conda env:base] *",
   "language": "python",
   "name": "conda-base-py"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.12.7"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
