# Generated by Django 4.1.7 on 2023-05-29 20:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('entidades', '0003_alter_entidade_poder'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='entidade',
            options={'ordering': ['municipio']},
        ),
    ]