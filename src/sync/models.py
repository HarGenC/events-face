from django.db import models

# Create your models here.


class SyncLog(models.Model):
    run_at = models.DateTimeField(auto_now_add=True)
    time_execution = models.FloatField()
    created_count = models.PositiveIntegerField(default=0)
    updated_count = models.PositiveIntegerField(default=0)
