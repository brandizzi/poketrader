# Generated by Django 3.1.6 on 2021-02-17 22:28

from django.db import migrations, models
import django.db.models.deletion


def convert_to_list_item(apps, schema_editor):
    PokemonComparison = apps.get_model('poketrader', 'PokemonComparison')
    PokemonListItem = apps.get_model('poketrader', 'PokemonListItem')
    for comparison in PokemonComparison.objects.all():
        for pokemon in comparison.list1.all():
            item = PokemonListItem(pokemon=pokemon)
            item.save()
            comparison.list_items1.add(item)
        for pokemon in comparison.list2.all():
            item = PokemonListItem(pokemon=pokemon)
            item.save()
            comparison.list_items2.add(item)
        comparison.save()


class Migration(migrations.Migration):

    dependencies = [
        ('poketrader', '0004_pokemoncomparison'),
    ]

    operations = [
        migrations.CreateModel(
            name='PokemonListItem',
            fields=[
                ('id', models.AutoField(auto_created=True,
                                        primary_key=True, serialize=False, verbose_name='ID')),
                ('pokemon', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE, to='poketrader.pokemon')),
            ],
        ),
        migrations.AddField(
            model_name='pokemoncomparison',
            name='list_items1',
            field=models.ManyToManyField(
                related_name='list1', to='poketrader.PokemonListItem'),
        ),
        migrations.AddField(
            model_name='pokemoncomparison',
            name='list_items2',
            field=models.ManyToManyField(
                related_name='list2', to='poketrader.PokemonListItem'),
        ),
        migrations.RunPython(convert_to_list_item),
        migrations.RemoveField(
            model_name='pokemoncomparison',
            name='list1',
        ),
        migrations.RemoveField(
            model_name='pokemoncomparison',
            name='list2',
        ),
    ]
