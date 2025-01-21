# import requests

# # BBC News API endpoint and headers
# url = "https://bbc-api3.p.rapidapi.com/search"

# querystring = {"q":"Electronic","page":"1"}
# headers = {
# 	"x-rapidapi-key": "4f6781ee86msh390a0839c5dd4cdp143c19jsn2c9fea16fd2c",
# 	"x-rapidapi-host": "bbc-api3.p.rapidapi.com"# Replace with your RapidAPI key
# }

# # Query parameters (optional based on API documentation)


# # Fetching data
# try:
#     response = requests.get(url, headers=headers, params=querystring)
#     response.raise_for_status()  # Raise an error for HTTP error codes
#     news_data = response.json()  # Parse the JSON response
#     print("Fetched News Data:")
#     for article in news_data.get("articles", []):  # Assuming 'articles' is part of the response
#         print(f"- {article['title']}: {article['description']}")
# except requests.exceptions.RequestException as e:
#     print(f"An error occurred: {e}")

# ---------------------------------------------------(rapid api limited data)
# import requests
# import csv

# url = "https://bbc-api3.p.rapidapi.com/live"

# querystring = {"q": "Electronic", "page": 1, "category": "world"}

# headers = {
# 	"x-rapidapi-key": "4f6781ee86msh390a0839c5dd4cdp143c19jsn2c9fea16fd2c",
# 	"x-rapidapi-host": "bbc-api3.p.rapidapi.com"
# }

# # response = requests.get(url, headers=headers)

# # print(response.json())

# # Fetch data
# try:
#     response = requests.get(url, headers=headers, params=querystring)
#     response.raise_for_status()  # Raise error for HTTP issues
#     data = response.json()  # Parse JSON response

#     # Print data to understand structure (optional for debugging)
#     print("API Response:", data)

#     # Handle data as a list
#     articles = data  # Assume the response is directly a list of articles

#     # CSV file name
#     csv_file = "bbc_news_data.csv"

#     # Write data to CSV
#     with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
#         writer = csv.writer(file)

#         # Write the header row (adjust based on response structure)
#         writer.writerow(["Title", "Description", "URL", "Published Date"])

#         # Write each article's data
#         for article in articles:
#             writer.writerow([
#                 article.get("title", ""),          # Title of the article
#                 article.get("description", ""),    # Description or summary
#                 article.get("url", ""),            # URL of the article
#                 article.get("published_at", "")    # Published date (if available)
#             ])

#     print(f"Data saved to {csv_file}")

# except requests.exceptions.RequestException as e:
#     print(f"An error occurred: {e}")


# ----------------------------------------------Newsdata.io (200 credit limit 10 per req)

import requests
import csv

# API endpoint and your API key
url = "https://newsdata.io/api/1/news"
api_key = "pub_659321ce53328c0ba5de64c71d23a805e2691"  # Replace with your NewsData.io API key

# Parameters to fetch the latest news
params = {
    "apikey": api_key,
    "language": "en",  # Language filter (English)
    # "category": "top",  # Fetch top/latest news
    # "country": "us",    # Country filter (United States)
    "page": 2,        # Fetch 50 articles per request
              
}

try:
    # Make the API request
    response = requests.get(url, params=params)
    response.raise_for_status()  # Raise exception for HTTP errors
    data = response.json()  # Parse the JSON response

    # Debugging: Print the response structure
    print("Response JSON:", data)

    # Extract articles from the response
    articles = data.get("results", [])

    # Check if articles are available
    if not articles:
        print("No articles found.")
        exit()

    # CSV file to save the data
    csv_file = "latest_news.csv"

    # Write data to CSV
    with open(csv_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        
        # Write the header row
        writer.writerow(["Title", "Description", "URL", "Source", "Published Date"])

        # Write each article's data
        for article in articles:
            writer.writerow([
                article.get("title", ""),          # Article title
                article.get("description", ""),    # Article description
                article.get("link", ""),           # Article URL
                article.get("source_id", ""),      # Source name
                article.get("pubDate", ""),        # Published date
            ])

    print(f"Data saved to {csv_file}")

except requests.exceptions.RequestException as e:
    print(f"An error occurred: {e}")
