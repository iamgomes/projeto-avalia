# Generated by Django 4.1.7 on 2023-05-01 03:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('entidades', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='municipio',
            name='capital',
            field=models.BooleanField(default=False),
        ),
    ]
