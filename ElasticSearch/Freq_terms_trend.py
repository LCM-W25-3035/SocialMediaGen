from elasticsearch import Elasticsearch

def get_trending_terms(es, index, start_range="now-3M/d", end_range="now/d", field="headline.keyword", size=10):
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
            "trending_terms": {
                "terms": {
                    "field": field,
                    "size": size
                }
            }
        }
    }
    response = es.search(index=index, body=query)
    buckets = response.get("aggregations", {}).get("trending_terms", {}).get("buckets", [])
    return buckets

if __name__ == "__main__":
    es_host = "https://40.118.170.15:9200"
    es_username = "elastic"
    es_password = "jhaA_lqCTVtvRbR1a0jf"
    
    # Connect to Elasticsearch (disabling certificate verification for self-signed certificates)
    es = Elasticsearch(es_host, basic_auth=(es_username, es_password), verify_certs=False)
    
    index_name = "news_index"
    trending_terms = get_trending_terms(es, index_name)
    
    print("Trending Terms based on Word Frequency:")
    if trending_terms:
        for term in trending_terms:
            print(f"Term: {term['key']}, Count: {term['doc_count']}")
    else:
        print("No trending terms found for the specified time range.")
