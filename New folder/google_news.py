from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time

# Step 1: Set up Selenium WebDriver
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode (no UI)
chrome_service = Service("path/to/chromedriver")  # Replace with your ChromeDriver path
driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

# Step 2: Navigate to Google News
GOOGLE_NEWS_URL = "https://news.google.com"
driver.get(GOOGLE_NEWS_URL)
time.sleep(3)  # Wait for JavaScript to load

# Step 3: Extract trending news titles and URLs
news_elements = driver.find_elements(By.XPATH, '//a[@class="DY5T1d"]')  # Find elements by dynamic tag class
trending_news = []

for item in news_elements:
    title = item.text
    url = item.get_attribute("href")
    trending_news.append({"title": title, "url": url})

# Step 4: Print the results
print("Trending News from Google News:")
for news in trending_news:
    print(f"Title: {news['title']}")
    print(f"URL: {news['url']}\n")

# Step 5: Close the browser
driver.quit()
