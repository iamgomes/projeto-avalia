# Generated by Django 4.1.7 on 2023-06-07 03:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0009_user_setor_alter_user_funcao'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'ordering': ('first_name',)},
        ),
    ]
