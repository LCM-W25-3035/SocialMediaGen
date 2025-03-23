from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path('', views.index, name='home'), 
    path('fetch-news/', views.fetch_news, name='fetch_news'),
    path('news/<str:news_id>/', views.news_detail, name='news_detail'),  # News detail page
    path('generate-llm-output/', views.generate_llm_output, name='generate_llm_output'),
]
