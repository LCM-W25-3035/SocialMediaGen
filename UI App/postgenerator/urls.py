# urls.py
from django.contrib import admin
from django.urls import path
from . import views
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('', views.index, name='home'),
    path('fetch-news/', views.fetch_news, name='fetch_news'),
    path('fetch-trending-news/', views.fetch_trending_news, name='fetch-trending-news'),
    path('news/<str:news_id>/', views.news_detail, name='news_detail'),
    
    # Keep the original endpoint name that matches your frontend
    path('generate-llm-output/', csrf_exempt(views.generate_llm_output)), 
    path('generate-llm-output/<str:news_id>/', csrf_exempt(views.generate_llm_output)),
    path('search-news/', views.search_news, name='search-news'),
    path('admin/', admin.site.urls),
]
