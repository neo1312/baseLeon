from django.db import models

class PageCounter(models.Model):
    count = models.PositiveIntegerField(default=1)

