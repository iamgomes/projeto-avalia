# Generated by Django 4.1.7 on 2023-04-13 04:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('entidades', '0001_initial'),
        ('avaliacoes', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='usuarioavaliacaovalidacao',
            name='usuario',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='usuarioavaliacaovalidacao',
            name='usuario_avaliacao',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='avaliacoes.usuarioavaliacao'),
        ),
        migrations.AddField(
            model_name='usuarioavaliacao',
            name='avaliacao',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='avaliacoes.avaliacao'),
        ),
        migrations.AddField(
            model_name='usuarioavaliacao',
            name='entidade',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='entidades.entidade'),
        ),
        migrations.AddField(
            model_name='usuarioavaliacao',
            name='usuario',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='respostavalidacao',
            name='resposta',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='avaliacoes.resposta'),
        ),
        migrations.AddField(
            model_name='respostavalidacao',
            name='usuario_avaliacao_validacao',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='avaliacoes.usuarioavaliacaovalidacao'),
        ),
        migrations.AddField(
            model_name='resposta',
            name='criterio_dimensao',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='avaliacoes.criteriodimensao'),
        ),
        migrations.AddField(
            model_name='resposta',
            name='usuarioavaliacao',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='avaliacoes.usuarioavaliacao'),
        ),
        migrations.AddField(
            model_name='imagemevidencia',
            name='resposta',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='avaliacoes.resposta'),
        ),
        migrations.AddField(
            model_name='criteriodimensao',
            name='criterio',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='avaliacoes.criterio'),
        ),
        migrations.AddField(
            model_name='criteriodimensao',
            name='dimensao',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='avaliacoes.dimensao'),
        ),
        migrations.AddField(
            model_name='criterio',
            name='avaliacao',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='avaliacoes.avaliacao'),
        ),
        migrations.AddField(
            model_name='criterio',
            name='dimensoes',
            field=models.ManyToManyField(through='avaliacoes.CriterioDimensao', to='avaliacoes.dimensao'),
        ),
        migrations.AddField(
            model_name='criterio',
            name='grupo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='avaliacoes.grupocriterio'),
        ),
        migrations.AddField(
            model_name='avaliacao',
            name='grupo',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='avaliacoes.grupoavaliacao'),
        ),
        migrations.AlterUniqueTogether(
            name='usuarioavaliacao',
            unique_together={('avaliacao', 'entidade')},
        ),
        migrations.AlterUniqueTogether(
            name='criteriodimensao',
            unique_together={('criterio', 'dimensao')},
        ),
    ]
