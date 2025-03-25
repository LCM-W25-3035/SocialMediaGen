from django.shortcuts import render, redirect, get_object_or_404
from .models import Task
from .forms import TaskForm

# CREATE
def create_task(request):
    """Handles task creation"""
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()  # Save to MongoDB
            return redirect('task_list')  # Redirect to task list
    else:
        form = TaskForm()
    return render(request, 'tasks/create_task.html', {'form': form})

# READ
def task_list(request):
    """Displays all tasks"""
    tasks = Task.objects.all()  # Fetch all tasks from MongoDB
    return render(request, 'tasks/task_list.html', {'tasks': tasks})

# UPDATE
def update_task(request, task_id):
    """Handles task editing"""
    task = get_object_or_404(Task, id=task_id)  # Get task or show 404
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect('task_list')
    else:
        form = TaskForm(instance=task)
    return render(request, 'tasks/update_task.html', {'form': form})

# DELETE
def delete_task(request, task_id):
    """Handles task deletion"""
    task = get_object_or_404(Task, id=task_id)
    if request.method == 'POST':
        task.delete()  # Remove from MongoDB
        return redirect('task_list')
    return render(request, 'tasks/delete_task.html', {'task': task})