from django.urls import path
from . import views

urlpatterns = [
    path('', views.news_home, name='news_home'),
    path('add/', views.add_news, name='add_news'),
    path('edit/<str:news_id>/', views.edit_news, name='edit_news'),
    path('delete/<str:news_id>/', views.delete_news, name='delete_news'),
]
