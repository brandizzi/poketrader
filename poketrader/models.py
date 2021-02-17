from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Pokemon(models.Model):
    name = models.CharField(max_length=100, unique=True)
    base_experience = models.IntegerField()
    picture_url = models.URLField()

    def as_dict(self):
        return {
            'name': self.name,
            'base_experience': self.base_experience,
            'picture_url': self.picture_url
        }


class PokemonComparison(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    list1 = models.ManyToManyField(Pokemon, related_name='list1')
    list2 = models.ManyToManyField(Pokemon, related_name='list2')

    def as_list_of_dicts(self):
        return (
            [p.as_dict() for p in self.list1.all()],
            [p.as_dict() for p in self.list2.all()]
        )
