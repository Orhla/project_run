from django.db import models
from django.conf import settings

# Create your models here.
class Run(models.Model):
    STATUS_CHOICES = [('init', 'Забег инициализирован'),
                      ('in_progress', 'Забег начат'),
                      ('finished', 'Забег закончен')]

    created_at = models.DateTimeField(auto_now_add=True)
    comment = models.TextField(null=True)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='init')
    athlete = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)