# Generated by Django 4.1.7 on 2023-04-19 21:19

from django.db import migrations
import smart_selects.db_fields


class Migration(migrations.Migration):

    dependencies = [
        ('entidades', '0001_initial'),
        ('usuarios', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='entidade',
            field=smart_selects.db_fields.ChainedManyToManyField(blank=True, chained_field='municipio', chained_model_field='municipio', null=True, to='entidades.entidade'),
        ),
    ]
