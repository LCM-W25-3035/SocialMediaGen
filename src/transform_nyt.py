def transform_data(article):
    """
    Cleans and deduplicates the news article before loading it into MongoDB and Elasticsearch.
    """

    
    cleaned_data = {key: value for key, value in article.items() if value not in [None, '', 'NaN']}

    
    important_fields = ['headline', 'pub_date', 'source', 'abstract', 'web_url']
    for field in important_fields:
        if field not in cleaned_data:
            cleaned_data[field] = 'N/A'

   
    if 'uri' in cleaned_data:
        cleaned_data['_id'] = cleaned_data.pop('uri')  

    return cleaned_data
