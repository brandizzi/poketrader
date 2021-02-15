from django.db import models


class Pokemon(models.Model):
    name = models.CharField(max_length=100, unique=True)
    base_experience = models.IntegerField()
    picture_url = models.URLField()
