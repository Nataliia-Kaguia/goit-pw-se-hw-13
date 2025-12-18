from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Author(models.Model):
    name = models.CharField(max_length=200, unique=True)
    born_date = models.CharField(max_length=100, blank=True, null=True)
    born_location = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Quote(models.Model):
    text = models.TextField()
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='quotes')
    tags = models.ManyToManyField(Tag, related_name='quotes', blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.text[:60]}… — {self.author.name}'
