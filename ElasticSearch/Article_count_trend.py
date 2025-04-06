from elasticsearch import Elasticsearch
import json

def get_trending_articles(es, index, start_range="now-3M/d", end_range="now/d", interval="day"):
    # Build the aggregation query for a date histogram on the timestamp field
    query = {
        "size": 0,
        "query": {
            "range": {
                "timestamp": {
                    "gte": start_range,
                    "lte": end_range
                }
            }
        },
        "aggs": {
            "articles_over_time": {
                "date_histogram": {
                    "field": "timestamp",
                    "calendar_interval": interval
                }
            }
        }
    }
    response = es.search(index=index, body=query)
    buckets = response.get("aggregations", {}).get("articles_over_time", {}).get("buckets", [])
    return buckets

if __name__ == "__main__":
    # Elasticsearch connection settings - update these with your actual values
    es_host = "https://40.118.170.15:9200"
    es_username = "elastic"
    es_password = "jhaA_lqCTVtvRbR1a0jf"  

    # Connect to Elasticsearch (disabling cert verification for self-signed certs)
    es = Elasticsearch(es_host, basic_auth=(es_username, es_password), verify_certs=False)
    
    # Define your index name
    index_name = "news_index"

    # Query trending articles over the last 3 months, grouped by day
    buckets = get_trending_articles(es, index_name)
    
    print("Trending Articles (Count per Day):")
    for bucket in buckets:
        print(f"Date: {bucket['key_as_string']}, Count: {bucket['doc_count']}")
