# Generated by Django 4.1.7 on 2023-06-27 18:12

from django.db import migrations, models
import questionarios.models


class Migration(migrations.Migration):

    dependencies = [
        ('questionarios', '0003_alter_questionario_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='imagemevidencia',
            name='imagem',
            field=models.FileField(upload_to=questionarios.models.get_file_path),
        ),
    ]