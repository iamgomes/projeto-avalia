# Generated by Django 4.1.7 on 2023-05-29 20:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questionarios', '0014_alter_questionario_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='dimensao',
            name='peso',
            field=models.IntegerField(default=1),
        ),
    ]