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


class PokemonListItem(models.Model):
    pokemon = models.ForeignKey(Pokemon, on_delete=models.CASCADE)


class PokemonComparison(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    list_items1 = models.ManyToManyField(PokemonListItem, related_name='list1')
    list_items2 = models.ManyToManyField(PokemonListItem, related_name='list2')

    def as_list_of_dicts(self):
        return (
            [p.as_dict() for p in self.list1.all()],
            [p.as_dict() for p in self.list2.all()]
        )

    def list1_as_string(self):
        return ", ".join(p.name for p in self.list1.all())

    def list2_as_string(self):
        return ", ".join(p.name for p in self.list2.all())
