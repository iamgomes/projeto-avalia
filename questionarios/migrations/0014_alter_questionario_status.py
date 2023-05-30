# Generated by Django 4.1.7 on 2023-05-23 14:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questionarios', '0013_alter_questionario_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='questionario',
            name='status',
            field=models.CharField(choices=[('NS', 'Não possui site'), ('I', 'Iniciado'), ('F', 'Finalizado UG'), ('E', 'Editando'), ('EV', 'Em Validação'), ('V', 'Validado')], default='I', max_length=2),
        ),
    ]
