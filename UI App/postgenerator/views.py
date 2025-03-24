from django.shortcuts import render
from django.http import JsonResponse
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from bson import json_util, ObjectId
from django.views.decorators.csrf import csrf_exempt
from urllib.parse import unquote
import json

# MongoDB Connection (included in code)
MONGO_URI = "mongodb+srv://Govind:Qwerty1234@projectnewsanalytics.kdevn.mongodb.net/?retryWrites=true&w=majority&appName=ProjectNewsAnalytics"
client = MongoClient(MONGO_URI)
db = client['news_database']
collection = db['master_news_01']


def fetch_news(request):
    try:
        # Get topic and page from query parameters
        topic = request.GET.get('topic', '')
        page = int(request.GET.get('page', 1))
        items_per_page = 10
        skip = (page - 1) * items_per_page

        # Filter by topic if provided
        if topic:
            news_data = list(collection.find({'topic': topic}, {'_id': 1, 'headline': 1, 'summary': 1, 'source': 1})
                             .skip(skip).limit(items_per_page))
        else:
            news_data = list(collection.find({}, {'_id': 1, 'headline': 1, 'summary': 1, 'source': 1})
                             .skip(skip).limit(items_per_page))

        # Convert ObjectId to string for JSON serialization
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
            data = json.loads(request.body)
            user_input = data.get('input', '')

            if not user_input:
                return JsonResponse({'error': 'Input is required'}, status=400)

            llm_output = f"Processed input: {user_input}"

            return JsonResponse({'output': llm_output})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)
