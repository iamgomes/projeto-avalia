# Generated by Django 4.1.7 on 2023-05-09 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questionarios', '0008_criterio_matriz'),
    ]

    operations = [
        migrations.AddField(
            model_name='criterio',
            name='cod',
            field=models.CharField(default=1, max_length=10),
            preserve_default=False,
        ),
    ]
