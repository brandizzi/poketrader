# Generated by Django 3.1.6 on 2021-02-15 08:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('poketrader', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pokemon',
            name='name',
            field=models.CharField(max_length=100, unique=True),
        ),
        migrations.AlterField(
            model_name='pokemon',
            name='pokeapi_id',
            field=models.CharField(max_length=10, unique=True),
        ),
    ]
