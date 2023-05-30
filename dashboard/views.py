from django.shortcuts import render, redirect, get_object_or_404
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

    for q in questionario:
        validacao = Validacao(usuario=usuario, questionario_id=q.id)
        validacao.save()

        q.status = 'AV'
        q.save()

        # Envia notificação para o Usuário
        notify.send(request.user, recipient=usuario, verb=f'{validacao.questionario.entidade}', target=validacao.questionario, description=f'Validação atribuída por {request.user.first_name}.')

    return messages.success(request, "Questionários atribuídos para validação com sucesso!")


@login_required
def visao_geral(request):
    if request.method == 'GET':
        entidades = Entidade.objects.filter(municipio__uf=request.user.municipio.uf)
        municipios = Municipio.objects.filter(uf=request.user.municipio.uf)
        setores = Tramitacao.SETOR_CHOICES
        status = Questionario.STATUS_CHOICES
        auditores = User.objects.filter(municipio__uf=request.user.municipio.uf).filter(funcao='T')

        questionarios = Questionario.objects.filter(entidade__in=entidades)
        questionarios_validados = questionarios.filter(status='V')

        ultima_tramitacao = Tramitacao.objects.values('questionario').annotate(id_ultimo=Max('id'))
        tramitacao = Tramitacao.objects.filter(pk__in=[i['id_ultimo'] for i in ultima_tramitacao])
        questionarios_setor = questionarios.filter(validacao=None).filter(pk__in=tramitacao.filter(setor=request.user.funcao).values_list('questionario', flat=True))
        questionarios_tramitar = questionarios.filter(Q(status='V') | Q(status='F')).filter(pk__in=tramitacao.filter(setor=request.user.funcao).values_list('questionario', flat=True))

        municipio_filtro = request.GET.get('municipio_filtro', None)
        ug_filtro = request.GET.get('ug_filtro', None)
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
