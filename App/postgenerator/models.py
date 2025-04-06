from django.db import models

class NewsArticle(models.Model):
    _id = models.AutoField(primary_key=True)
    headline = models.CharField(max_length=255)
    summary = models.TextField()
    source = models.CharField(max_length=100)
    topic = models.CharField(max_length=100, blank=True)  # Add this line