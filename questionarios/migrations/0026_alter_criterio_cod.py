# Generated by Django 4.1.7 on 2023-06-01 18:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questionarios', '0025_alter_criterio_cod'),
    ]

    operations = [
        migrations.AlterField(
            model_name='criterio',
            name='cod',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5),
        ),
    ]
