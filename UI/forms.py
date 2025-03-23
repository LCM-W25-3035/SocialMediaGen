from django import forms

class NewsForm(forms.Form):
    headline = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-control'}))
    link = forms.URLField(widget=forms.URLInput(attrs={'class': 'form-control'}))
    summary = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    timestamp = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    category = forms.CharField(max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))