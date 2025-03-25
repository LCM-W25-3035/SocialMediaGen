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
MONGO_URI = "mongodb+srv://Govind:@projectnewsanalytics.kdevn.mongodb.net/?retryWrites=true&w=majority&appName=ProjectNewsAnalytics"
client = MongoClient(MONGO_URI)
db = client['news_database']
collection = db['master_news_01']

# Hugging Face API details
HF_TOKEN = "hf_epIuUPmcd**mSAKkUvdvam"  # Replace with your actual token
MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.3"
API_URL = f"https://api-inference.huggingface.co/models/{MODEL_NAME}"
HEADERS = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
}


def fetch_news(request):
    """
    Fetches news articles from the MongoDB database based on the given topic and pagination.
    """
    try:
        topic = request.GET.get('topic', '')  # Get topic from query parameters
        page = int(request.GET.get('page', 1))  # Get page number (default is 1)
        items_per_page = 10  # Number of news articles per page
        skip = (page - 1) * items_per_page  # Calculate how many records to skip

        # Fetch news articles from the database based on the topic filter
        if topic:
            news_data = list(collection.find(
                {'topic': topic},
                {'_id': 1, 'headline': 1, 'summary': 1, 'source': 1}
            ).skip(skip).limit(items_per_page))
        else:
            news_data = list(collection.find(
                {},
                {'_id': 1, 'headline': 1, 'summary': 1, 'source': 1}
            ).skip(skip).limit(items_per_page))

        # Convert ObjectId to string for JSON serialization
        for news in news_data:
            news['_id'] = str(news['_id'])

        return JsonResponse(news_data, safe=False)
    
    except ServerSelectionTimeoutError:
        return JsonResponse({'error': 'Could not connect to MongoDB'}, status=500)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def index(request):
    """
    Renders the home page for the news post generator application.
    """
    return render(request, 'postgenerator/home.html')


def news_detail(request, news_id):
    """
    Retrieves details of a specific news article based on the provided news_id.
    """
    try:
        news_item = collection.find_one({'_id': ObjectId(news_id)}, {'_id': 0})

        if not news_item:
            return JsonResponse({'error': 'News not found'}, status=404)

        return render(request, 'postgenerator/news_detail.html', {'news_item': news_item})
    
    except ServerSelectionTimeoutError:
        return JsonResponse({'error': 'Could not connect to MongoDB'}, status=500)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt  # Disable CSRF protection for this endpoint
def generate_llm_output(request, news_id):
    """
    Generates a social media post from a news article using an LLM model.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  # Parse JSON request body
            user_input = data.get('input', '').strip()  # Get user input if provided

            # Default prompt for generating social media posts
            default_prompt = (
                "Determine the sentiment (positive, negative, neutral) of this news. "
                "Generate a short social media post based on the sentiment: "
                "Positive: Exciting, highlight good news. "
                "Negative: Serious, sensitive, informative. "
                "Neutral: Factual, engaging. "
                "Give me only one post based on sentiment type of the news. "
                "Include a catchy hook, key insight, emojis, and relevant hashtags."
            )

            # Fetch news item from database
            news_item = collection.find_one(
                {'_id': ObjectId(news_id)},
                {'_id': 0, 'headline': 1, 'summary': 1}
            )

            if not news_item:
                return JsonResponse({'error': 'News not found'}, status=404)

            headline = news_item.get('headline')
            summary = news_item.get('summary')

            # Construct input for the LLM model
            input_to_send = f"{headline} {summary} {default_prompt}"
            if user_input:
                input_to_send += f" {user_input}"

            # Send request to Hugging Face API
            response = requests.post(API_URL, headers=HEADERS, json={"inputs": input_to_send})
            
            if response.status_code == 200:
                llm_output = response.json()
                social_post = llm_output[0].get('generated_text', "Error generating text.")
                return JsonResponse({'social_post': social_post})
            else:
                return JsonResponse({'error': 'Error generating LLM output'}, status=500)
        
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=400)
