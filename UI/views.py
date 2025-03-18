from django.shortcuts import render, redirect
from django.conf import settings
from .forms import NewsForm

def add_news(request):
    if request.method == 'POST':
        form = NewsForm(request.POST)
        if form.is_valid():
            # Insert new news into MongoDB
            news_data = {
                'headline': form.cleaned_data['headline'],
                'link': form.cleaned_data['link'],
                'summary': form.cleaned_data['summary'],
                'timestamp': form.cleaned_data['timestamp'],
                'category': form.cleaned_data['category'],
            }
            settings.news_collection.insert_one(news_data)
            return redirect('news_home')
    else:
        form = NewsForm()
    return render(request, 'news/add_news.html', {'form': form})


def news_home(request):
    # Fetch all news from MongoDB
    news_list = list(settings.news_collection.find())
    return render(request, 'news/news_home.html', {'news_list': news_list})

from bson.objectid import ObjectId

def edit_news(request, news_id):
    news = settings.news_collection.find_one({'_id': ObjectId(news_id)})
    if request.method == 'POST':
        form = NewsForm(request.POST)
        if form.is_valid():
            # Update news in MongoDB
            updated_data = {
                'headline': form.cleaned_data['headline'],
                'link': form.cleaned_data['link'],
                'summary': form.cleaned_data['summary'],
                'timestamp': form.cleaned_data['timestamp'],
                'category': form.cleaned_data['category'],
            }
            settings.news_collection.update_one({'_id': ObjectId(news_id)}, {'$set': updated_data})
            return redirect('news_home')
    else:
        # Pre-fill the form with existing data
        form = NewsForm(initial={
            'headline': news['headline'],
            'link': news['link'],
            'summary': news['summary'],
            'timestamp': news['timestamp'],
            'category': news['category'],
        })
    return render(request, 'news/edit_news.html', {'form': form, 'news_id': news_id})

def delete_news(request, news_id):
    if request.method == 'POST':
        # Delete news from MongoDB
        settings.news_collection.delete_one({'_id': ObjectId(news_id)})
        return redirect('news_home')
    return render(request, 'news/confirm_delete.html', {'news_id': news_id})
