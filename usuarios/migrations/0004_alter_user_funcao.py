# Generated by Django 4.1.7 on 2023-05-01 01:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('usuarios', '0003_alter_user_entidade'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='funcao',
            field=models.CharField(choices=[('C', 'Controlador Interno'), ('T', 'Tribunal de Contas')], default='C', max_length=1),
        ),
    ]
