from django.shortcuts import render
from django.http import JsonResponse
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from bson import ObjectId
from django.views.decorators.csrf import csrf_exempt
from urllib.parse import unquote
import json
import requests
import re
from collections import Counter
from decouple import config
from elasticsearch import Elasticsearch

# connect to elastic search
es = Elasticsearch(
    config("ES_URL"),
    basic_auth=(config("ES_USER"), config("ES_PASSWORD")),
    verify_certs=False
)

INDEX_NAME = "news_index"  # Replace with your actual index name


# MongoDB Connection
MONGO_URI = config("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client['news_database']
collection = db['master_news_cleaned']


# Hugging Face
HF_TOKEN = config("HF_TOKEN")
MODEL_NAME = config("MODEL_NAME")
API_URL = f"https://api-inference.huggingface.co/models/{MODEL_NAME}"
HEADERS = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}

from django.http import JsonResponse
from pymongo.errors import ServerSelectionTimeoutError

def fetch_news(request):
    try:
        topic = request.GET.get('topic', '')
        page = int(request.GET.get('page', 1))
        items_per_page = 10
        skip = (page - 1) * items_per_page

        # Sort by timestamp in descending order to get the latest news first
        sort_order = [('timestamp', -1)]

        # Create the filter to exclude news from 'cnn_news'
        query_filter = {'source': {'$ne': 'cnn_news'}}  # Exclude news with source 'cnn_news'

        if topic:
            # Fetch news based on topic, excluding cnn_news and sorted by timestamp
            news_data = list(collection.find(
                {**query_filter, 'topic': topic},
                {'_id': 1, 'headline': 1, 'summary': 1, 'source': 1, 'link': 1, 'timestamp': 1}
            ).skip(skip).limit(items_per_page).sort(sort_order))
        else:
            # Fetch all news if no topic provided, excluding cnn_news and sorted by timestamp
            news_data = list(collection.find(
                query_filter,
                {'_id': 1, 'headline': 1, 'summary': 1, 'source': 1, 'link': 1, 'timestamp': 1}
            ).skip(skip).limit(items_per_page).sort(sort_order))

        # Convert ObjectId to string for JSON response
        for news in news_data:
            news['_id'] = str(news['_id'])

        return JsonResponse(news_data, safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def fetch_trending_news(request):
    try:
        # Get the latest 100 news items
        recent_news = list(collection.find({}, {'_id': 1, 'headline': 1, 'summary': 1, 'source': 1})
                           .sort([('_id', -1)]).limit(100))

        keyword_counter = Counter()

        for news in recent_news:
            text = f"{news['headline']} {news.get('summary', '')}".lower()
            words = re.findall(r'\b\w{4,}\b', text)  # extract words with length ≥ 4
            keyword_counter.update(words)

        top_keywords = [kw for kw, _ in keyword_counter.most_common(5)]

        trending_news = []
        for news in recent_news:
            text = f"{news['headline']} {news.get('summary', '')}".lower()
            if any(kw in text for kw in top_keywords):
                news['_id'] = str(news['_id'])
                trending_news.append(news)

        return JsonResponse({'keywords': top_keywords, 'articles': trending_news}, safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def index(request):
    return render(request, 'postgenerator/home.html')

def news_detail(request, news_id):
    try:
        news_item = collection.find_one({'_id': ObjectId(news_id)}, {'_id': 0})
        if not news_item:
            return JsonResponse({'error': 'News not found'}, status=404)
        return render(request, 'postgenerator/news_detail.html', {'news_item': news_item})
    except ServerSelectionTimeoutError:
        return JsonResponse({'error': 'Could not connect to MongoDB'}, status=500)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def generate_llm_output(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_input = data.get('input', '').strip()
            headline = data.get('headline', '').strip()

            if not headline:
                return JsonResponse({'error': 'Headline is required'}, status=400)

            news_item = collection.find_one({'headline': headline}, {'_id': 0, 'summary': 1})
            if not news_item:
                return JsonResponse({'error': 'News not found'}, status=404)

            default_prompt = """
            Create a social media post about this news. Make it engaging with:
            - Perform sentiment analysis and tailor the post accordingly
            - give me one post only.
            - A catchy opening
            - Key points from the summary
            - 1-2 relevant emojis
            - 2-3 hashtags
            - update post accordingly the users passed prompt, if any
            - don't show anything extra besides the final post generated
            """

            llm_input = f"{default_prompt}\n\nSummary: {news_item.get('summary', '')}"

            if user_input:
                llm_input += f"\n\nAdditional user instructions:\n{user_input}"

            response = requests.post(API_URL, headers=HEADERS, json={"inputs": llm_input})
            print("DEBUG API Response Text:", response.text)
            if response.status_code == 200:
                llm_output = response.json()
                generated_text = llm_output[0].get('generated_text', '').strip()
                post_start = generated_text.find("Post:")
                user_instructions_start = generated_text.find("Additional user instructions:")

                if user_instructions_start != -1:
                    instructions_content = generated_text[user_instructions_start + len("Additional user instructions:"):].strip()
                    social_post = instructions_content + "\n\n" + generated_text[post_start + 5:].strip() if post_start != -1 else instructions_content
                else:
                    social_post = generated_text[post_start + 5:].strip() if post_start != -1 else generated_text

                return JsonResponse({'social_post': social_post})
            else:
                return JsonResponse({'error': 'Error generating LLM output'}, status=500)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)

def search_news(request):
    query = request.GET.get('q', '').strip()
    if not query:
        return JsonResponse([], safe=False)

    try:
        es_query = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["headline", "summary"],
                    "fuzziness": "auto"
                }
            }
        }

        print("Running Elasticsearch Query:", es_query)

        es_response = es.search(index=INDEX_NAME, body=es_query)
        print("Elasticsearch response:", es_response)

        hits = es_response.get('hits', {}).get('hits', [])

        news_list = [{
            "_id": hit["_id"],
            "headline": hit["_source"].get("headline"),
            "summary": hit["_source"].get("summary"),
            "source": hit["_source"].get("source")
        } for hit in hits]

        return JsonResponse(news_list, safe=False)

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'error': str(e)}, status=500)


