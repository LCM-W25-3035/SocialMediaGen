from djongo import models  # Djongo for MongoDB integration

class Task(models.Model):
    """MongoDB model for storing task data"""
    title = models.CharField(max_length=200)  # Task title field
    description = models.TextField()          # Detailed task description
    completed = models.BooleanField(default=False)  # Completion status
    created_at = models.DateTimeField(auto_now_add=True)  # Auto-set creation timestamp

    def __str__(self):
        return self.title  # Human-readable representation