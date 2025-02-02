from kafka import KafkaProducer
from pynytimes import NYTAPI
from datetime import datetime, timedelta
import json

# Kafka Producer
producer = KafkaProducer(bootstrap_servers='localhost:9092', value_serializer=lambda v: json.dumps(v).encode('utf-8'))

# NYT API Key
NYT_API_KEY = "15MPlclMxKGuTa7WreSZ9IYcbjoo45sL"

def extract_news():
    nyt = NYTAPI(NYT_API_KEY, parse_dates=True)
    start_date = datetime.now() - timedelta(days=30)
    end_date = datetime.now()

    try:
        articles = nyt.article_search(
            query="news",
            dates={"begin": start_date, "end": end_date}
        )

        if articles:
            for article in articles:
                producer.send('news_topic', article)  
                print(f"Sent to Kafka: {article.get('headline', {}).get('main', 'No Title')}")
        else:
            print("No new articles found.")
    except Exception as e:
        print("Error fetching articles:", e)

if __name__ == "__main__":
    extract_news()
