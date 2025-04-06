from django import forms
from .models import Task

class TaskForm(forms.ModelForm):
    """Form for creating/editing tasks"""
    class Meta:
        model = Task
        fields = ['title', 'description', 'completed']  # Fields to include in form
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),  # Textarea for description
        }