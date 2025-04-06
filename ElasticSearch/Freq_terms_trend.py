from elasticsearch import Elasticsearch
import json

def get_top_terms(es, index, start_range="now-3M/d", end_range="now/d", field="headline.keyword", size=10):
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
            "top_headline_terms": {
                "terms": {
                    "field": field,
                    "size": size
                }
            }
        }
    }
    response = es.search(index=index, body=query)
    buckets = response.get("aggregations", {}).get("top_headline_terms", {}).get("buckets", [])
    return buckets

if __name__ == "__main__":
    es_host = "https://40.118.170.15:9200"
    es_username = "elastic"
    es_password = "jhaA_lqCTVtvRbR1a0jf"  

    # Connect to Elasticsearch (disabling certificate verification for self-signed certs)
    es = Elasticsearch(es_host, basic_auth=(es_username, es_password), verify_certs=False)
    
    index_name = "news_index"
    top_terms = get_top_terms(es, index_name)
    
    print("Top Terms from Headlines (using terms aggregation):")
    for term in top_terms:
        print(f"Term: {term['key']}, Doc Count: {term['doc_count']}")
