from django.urls import path
from . import views

urlpatterns = [
    path('', views.task_list, name='task_list'),  # List all tasks
    path('create/', views.create_task, name='create_task'),  # Create new task
    path('update/<int:task_id>/', views.update_task, name='update_task'),  # Edit task
    path('delete/<int:task_id>/', views.delete_task, name='delete_task'),  # Delete task
]