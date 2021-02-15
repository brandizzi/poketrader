from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Pokemon(models.Model):
    name = models.CharField(max_length=100, unique=True)
    base_experience = models.IntegerField()
    picture_url = models.URLField()


class PokemonComparison(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    list1 = models.ManyToManyField(Pokemon, related_name='list1')
    list2 = models.ManyToManyField(Pokemon, related_name='list2')
