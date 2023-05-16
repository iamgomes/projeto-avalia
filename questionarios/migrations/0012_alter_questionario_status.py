# Generated by Django 4.1.7 on 2023-05-16 13:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('questionarios', '0011_remove_imagemevidencia_justificativa_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='questionario',
            name='status',
            field=models.CharField(choices=[('NS', 'Não possui site'), ('I', 'Iniciado'), ('F', 'Finalizado'), ('E', 'Editando'), ('EV', 'Em Validação'), ('V', 'Validado'), ('ER', 'Em Revisão')], default='I', max_length=2),
        ),
    ]
