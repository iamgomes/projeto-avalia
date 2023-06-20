from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from entidades.models import Entidade, Municipio
from questionarios.models import Questionario, Tramitacao
from validacoes.models import Validacao
from usuarios.models import User
from django.db.models import Max
from django.contrib import messages
from notifications.signals import notify
from django.db.models import Q
from rolepermissions.decorators import has_permission_decorator
import datetime
import csv


def tramitar_atricon(request, id):
    questionario = Questionario.objects.filter(pk__in=id)

    for q in questionario:
        tramitacao = Tramitacao(questionario_id=q.id, setor='A', motivo='EC', usuario=request.user)
        tramitacao.save()

        # Envia notificação para o Usuário
        notify.send(request.user, recipient=tramitacao.questionario.usuario, verb=f'{tramitacao.questionario.entidade}', target=tramitacao.questionario, description=f'{tramitacao.get_motivo_display()} por {request.user.first_name}.')

    return messages.success(request, "Questionários tramitados para Atricon com sucesso!")


def atribuir_validador(request, id, auditor_id):
    usuario = User.objects.get(pk=auditor_id)
    questionario = Questionario.objects.filter(pk__in=id)
    hoje = datetime.datetime.now()

    for q in questionario:
        inicio = q.avaliacao.data_inicial_validacao
        fim = q.avaliacao.data_final_validacao
        
        if hoje.timestamp() >= inicio.timestamp() and hoje.timestamp() <= fim.timestamp():

            validacao = Validacao(usuario=usuario, questionario_id=q.id)
            validacao.save()

            q.status = 'AV'
            q.save()

            # Envia notificação para o Usuário
            notify.send(request.user, recipient=[validacao.questionario.usuario, validacao.usuario], verb=f'{validacao.questionario.entidade}', target=validacao.questionario, description=f'Questionário selecionado para validação por {request.user.first_name}.')
        
        else:
            messages.warning(request, "Desculpe, você está fora do prazo de validação.")
            return redirect(reverse('visao_geral'))

    return messages.success(request, "Questionários atribuídos para validação com sucesso!")


@has_permission_decorator('visao_geral')
def visao_geral(request):
    if request.method == 'GET':
        entidades = Entidade.objects.filter(municipio__uf=request.user.municipio.uf).select_related('municipio').prefetch_related('questionario_set')
        municipios = Municipio.objects.filter(uf=request.user.municipio.uf)
        poderes = Entidade.PODER_CHOICES
        setores = Tramitacao.SETOR_CHOICES
        status = Questionario.STATUS_CHOICES
        auditores = User.objects.filter(municipio__uf=request.user.municipio.uf).filter(setor='T')

        questionarios = Questionario.objects.filter(entidade__in=entidades).select_related('avaliacao')
        questionarios_validados = questionarios.filter(status='V')

        ultima_tramitacao = Tramitacao.objects.values('questionario').annotate(id_ultimo=Max('id'))
        tramitacao = Tramitacao.objects.filter(pk__in=[i['id_ultimo'] for i in ultima_tramitacao])
        questionarios_setor = questionarios.filter(status='F').filter(pk__in=tramitacao.filter(setor=request.user.setor).values_list('questionario', flat=True))
        questionarios_tramitar = questionarios.filter(Q(status='V') | Q(status='F')).filter(pk__in=tramitacao.filter(setor=request.user.setor).values_list('questionario', flat=True))

        municipio_filtro = request.GET.get('municipio_filtro', None)
        ug_filtro = request.GET.get('ug_filtro', None)
        poder_filtro = request.GET.get('poder_filtro', None)
        setor_filtro = request.GET.get('setor_filtro', None)
        status_filtro = request.GET.get('status_filtro', None)

        if municipio_filtro != '' and municipio_filtro is not None:
            entidades = entidades.filter(municipio=municipio_filtro)
            municipios = municipios.filter(pk=entidades.first().municipio.pk)
            questionarios = questionarios.filter(entidade__in=entidades)
        if ug_filtro != '' and ug_filtro is not None:
            entidades = entidades.filter(pk=ug_filtro)
            municipios = municipios.filter(pk=entidades.first().municipio.pk)
            questionarios = questionarios.filter(entidade__in=entidades)
        if poder_filtro != '' and poder_filtro is not None:
            entidades = entidades.filter(poder=poder_filtro)
            municipios = municipios.filter(pk=entidades.first().municipio.pk)
            questionarios = questionarios.filter(entidade__in=entidades)
        if setor_filtro != '' and setor_filtro is not None:
            questionarios = questionarios.filter(pk__in=tramitacao.filter(setor=setor_filtro).values_list('questionario', flat=True))
            entidades = entidades.filter(pk__in=[q.entidade.id for q in questionarios])
            municipios = municipios.filter(pk=entidades.first().municipio.pk) if entidades else municipios
        if status_filtro != '' and status_filtro is not None:
            if status_filtro == 'NI':
                questionarios = questionarios.filter(status='NI')
                entidades = entidades.filter(questionario=None)
                municipios = municipios.filter(pk__in=[e.municipio.pk for e in entidades])
            else:
                questionarios = questionarios.filter(status=status_filtro)
                entidades = entidades.filter(pk__in=[q.entidade.id for q in questionarios])
                municipios = municipios.filter(pk__in=[e.municipio.pk for e in entidades])
                questionarios_validados = questionarios.filter(status='V')

        return render(request, 'visao_geral.html', {'entidades':entidades,
                                                    'municipios':municipios,
                                                    'questionarios':questionarios,
                                                    'questionarios_validados':questionarios_validados,
                                                    'questionarios_setor':questionarios_setor,
                                                    'questionarios_tramitar':questionarios_tramitar,
                                                    'poderes':poderes,
                                                    'setores':setores,
                                                    'status':status,
                                                    'auditores':auditores,})
    
    if request.method == 'POST':
        formCheck1 = filter(None, request.POST.getlist('formCheck1', None))
        auditor_id = request.POST.get('auditor_id', None)
        acao = request.POST.get('acao', None)

        if acao == 'Atribuir':
            atribuir_validador(request, formCheck1, auditor_id)

        if acao == 'Tramitar':
            tramitar_atricon(request, formCheck1)

    return redirect(reverse('visao_geral'))


def exporta_csv_visao_geral(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="VisãoGeral.csv"'
    response.write(u'\ufeff'.encode('utf8'))

    entidades = Entidade.objects.filter(municipio__uf=request.user.municipio.uf).select_related('municipio').prefetch_related('questionario_set')

    writer = csv.writer(response, delimiter=';')
    writer.writerow(['Unidade Gestora','Município', 'Poder', 'Status', 'Índice', 'Nível', 'Setor Atual', 'Validação'])

    for e in entidades:
        writer.writerow([e.nome, e.municipio, e.get_poder_display(),
                         e.questionario_set.all().first().get_status_display() if e.questionario_set.all().first() else 'Não Iniciado', 
                         e.questionario_set.all().first().indice if e.questionario_set.all().first() else '', 
                         e.questionario_set.all().first().nivel if e.questionario_set.all().first() else '', 
                         e.questionario_set.all().first().tramitacao_set.all().first().get_setor_display() if e.questionario_set.all().first() else '', 
                        exec('try:e.questionario_set.all().first().validacao.usuario.nome_completo\nexcept:""') 
                        ])
    return response



