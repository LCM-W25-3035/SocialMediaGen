from django.shortcuts import render
from django.http import JsonResponse
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from bson import ObjectId
from django.views.decorators.csrf import csrf_exempt
from urllib.parse import unquote
import json
import requests

# MongoDB Connection
MONGO_URI = "mongodb+srv://Govind:****234@projectnewsanalytics.kdevn.mongodb.net/?retryWrites=true&w=majority&appName=ProjectNewsAnalytics"
client = MongoClient(MONGO_URI)
db = client['news_database']
collection = db['master_news_01']

# Hugging Face API details
HF_TOKEN = "hf_epIuUPmc********Uvdvam"
MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.3"
API_URL = f"https://api-inference.huggingface.co/models/{MODEL_NAME}"
HEADERS = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}

def fetch_news(request):
    try:
        topic = request.GET.get('topic', '')
        page = int(request.GET.get('page', 1))
        items_per_page = 10
        skip = (page - 1) * items_per_page

        if topic:
            news_data = list(collection.find({'topic': topic}, {'_id': 1, 'headline': 1, 'summary': 1, 'source': 1})
                             .skip(skip).limit(items_per_page))
        else:
            news_data = list(collection.find({}, {'_id': 1, 'headline': 1, 'summary': 1, 'source': 1})
                             .skip(skip).limit(items_per_page))

        for news in news_data:
            news['_id'] = str(news['_id'])

        return JsonResponse(news_data, safe=False)

    except ServerSelectionTimeoutError:
        return JsonResponse({'error': 'Could not connect to MongoDB'}, status=500)
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
            # Parse request data
            data = json.loads(request.body)
            user_input = data.get('input', '').strip()
            headline = data.get('headline', '').strip()

            if not headline:
                return JsonResponse({'error': 'Headline is required'}, status=400)

            # Find news item by headline
            news_item = collection.find_one(
                {'headline': headline},
                {'_id': 0, 'summary': 1}
            )
            
            if not news_item:
                return JsonResponse({'error': 'News not found'}, status=404)

            # Default prompt for LLM
            default_prompt = """
            Create a social media post about this news. Make it engaging with:
            - Perform sentiment analysis and tailor the post accordingly and give me one post only.
            - A catchy opening
            - Key points from the summary
            - 1-2 relevant emojis
            - 2-3 hashtags
            - if user passes a prompt, update post accordingly
            """

            # Prepare input for LLM (excluding full news details)
            llm_input = f"{default_prompt}\n\nSummary: {news_item.get('summary', '')}"

            if user_input:
                llm_input += f"\n\nAdditional user instructions:\n{user_input}"

            # Call Hugging Face API
            response = requests.post(
                API_URL,
                headers=HEADERS,
                json={"inputs": llm_input}
            )
            
            if response.status_code == 200:
                llm_output = response.json()
                generated_text = llm_output[0].get('generated_text', '').strip()

                # Check for both "Post:" and "Additional user instructions:" sections
                post_start = generated_text.find("Post:")
                user_instructions_start = generated_text.find("Additional user instructions:")

                if user_instructions_start != -1:
                    # Extract the content after "Additional user instructions:"
                    instructions_content = generated_text[user_instructions_start + len("Additional user instructions:"):].strip()

                    # Look for "Post:" after the instructions
                    if post_start != -1:
                        social_post = instructions_content + "\n\n" + generated_text[post_start + 5:].strip()
                    else:
                        social_post = instructions_content  # Fallback if no "Post:" section is found
                else:
                    # Fallback: If "Additional user instructions:" isn't found, process as usual
                    if post_start != -1:
                        social_post = generated_text[post_start + 5:].strip()
                    else:
                        social_post = generated_text  # Fallback if "Post:" isn't found

                return JsonResponse({'social_post': social_post})

            else:
                return JsonResponse({'error': 'Error generating LLM output'}, status=500)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)

from bson import ObjectId

def search_news(request):
    query = request.GET.get('q', '').strip()

    if not query:
        return JsonResponse([], safe=False)

    try:
        # Perform the MongoDB query using a case-insensitive search for headline and summary
        news_results = collection.find({
            "$or": [
                {"headline": {"$regex": query, "$options": "i"}},
                {"summary": {"$regex": query, "$options": "i"}}
            ]
        })

        # Convert MongoDB cursor to list of dictionaries
        news_list = [{"_id": str(news["_id"]), "headline": news["headline"], "summary": news["summary"], "source": news["source"]} for news in news_results]

        return JsonResponse(news_list, safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    def fetch_trending_news(request):
    try:
        # Step 1: Retrieve the latest 100 news articles from the MongoDB collection
        # Only fetch '_id', 'headline', 'summary', and 'source' fields for each document
        recent_news = list(
            collection.find({}, {'_id': 1, 'headline': 1, 'summary': 1, 'source': 1})
            .sort([('_id', -1)])  # Sort by '_id' in descending order (most recent first)
            .limit(100)  # Limit the result to 100 items
        )

        # Step 2: Initialize a counter to store keyword frequencies
        keyword_counter = Counter()

        # Step 3: Iterate through each news item to extract keywords
        for news in recent_news:
            # Combine headline and summary text, convert to lowercase
            text = f"{news['headline']} {news.get('summary', '')}".lower()
            # Extract words with 4 or more characters using regex
            words = re.findall(r'\b\w{4,}\b', text)
            # Update the keyword counter with these words
            keyword_counter.update(words)

        # Step 4: Select the top 5 most common keywords
        top_keywords = [kw for kw, _ in keyword_counter.most_common(5)]

        # Step 5: Filter news articles that contain at least one of the top keywords
        trending_news = []
        for news in recent_news:
            text = f"{news['headline']} {news.get('summary', '')}".lower()
            # Check if any of the top keywords are present in the text
            if any(kw in text for kw in top_keywords):
                news['_id'] = str(news['_id'])  # Convert ObjectId to string for JSON serialization
                trending_news.append(news)

        # Step 6: Return the top keywords and the list of trending news articles
        return JsonResponse({'keywords': top_keywords, 'articles': trending_news}, safe=False)

    except Exception as e:
        # In case of any error, return a JSON response with the error message and status 500
        return JsonResponse({'error': str(e)}, status=500)
