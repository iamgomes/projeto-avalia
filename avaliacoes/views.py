from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Avaliacao
from questionarios.models import Questionario, Tramitacao
from validacoes.models import Validacao
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import json
from entidades.uf_choices import UfChoices
from entidades.models import Municipio, Entidade
from django.db.models import Max

@login_required
def avaliacoes_disponiveis(request):
    avaliacoes = Avaliacao.objects.all()

    return render(request, 'avaliacoes.html', {'avaliacoes':avaliacoes})


@login_required
def avaliacao(request):
    if request.method == 'GET':
        questionarios = Questionario.objects.all()
        avaliacoes_recebidas = questionarios.count()
        estados = [c for c in UfChoices.choices if c[0] in (questionarios.values_list('entidade__municipio__uf', flat=True))]
        municipios = Municipio.objects.filter(pk__in=questionarios.values_list('entidade__municipio', flat=True))
        entidades =  Entidade.objects.filter(pk__in=questionarios.values_list('entidade', flat=True))
        status = Questionario.STATUS_CHOICES

        uf_filtro = request.GET.get('uf_filtro', None)
        municipio_filtro = request.GET.get('municipio_filtro', None)
        ug_filtro = request.GET.get('ug_filtro', None)
        setor_filtro = request.GET.get('setor_filtro', None)
        status_filtro = request.GET.get('status_filtro', None)

        if uf_filtro != '' and uf_filtro is not None:
            questionarios = questionarios.filter(entidade__municipio__uf=uf_filtro)
        if municipio_filtro != '' and municipio_filtro is not None:
            questionarios = questionarios.filter(entidade__municipio=municipio_filtro)
        if ug_filtro != '' and ug_filtro is not None:
            questionarios = questionarios.filter(entidade=ug_filtro)
        if setor_filtro != '' and setor_filtro is not None:
            questionarios = questionarios.filter(pk__in=Tramitacao.objects.filter(setor=setor_filtro).values_list('questionario', flat=True))
        if status_filtro != '' and status_filtro is not None:
            questionarios = questionarios.filter(status=status_filtro)
        
        return render(request, 'avaliacoes.html', {'questionarios':questionarios, 
                                                   'avaliacoes_recebidas':avaliacoes_recebidas, 
                                                   'estados':estados,
                                                   'municipios':municipios,
                                                   'entidades':entidades,
                                                   'status':status})

@login_required
def load_motivos(request):
    setor_id = request.GET.get('setor')

    if setor_id == 'C':
        motivos = Tramitacao.MOTIVO_CHOICES[0][1]
    if setor_id == 'T':
        motivos = Tramitacao.MOTIVO_CHOICES[1][1]
    if setor_id == 'A':
        motivos = Tramitacao.MOTIVO_CHOICES[2][1]

    return render(request, 'load_motivos.html', {'motivos':motivos})


@login_required
def minhas_avaliacoes(request):
    if request.method == 'GET':
        questionarios = Questionario.objects.filter(usuario=request.user)
        validacoes = Validacao.objects.filter(usuario=request.user)
    
        return render(request, 'minhas_avaliacoes.html', {'questionarios':questionarios, 
                                                          'validacoes':validacoes,})

@login_required
def avaliacoes_setor(request):
    q = Questionario.objects.filter(entidade__municipio__uf=request.user.municipio.uf)
    # Para vc, meu caro mancebo, aqui temos um belíssimo exemplo de uma gambiarra. Na variavel "ultima_tramitacao", 
    # é feita a verificação do último id na tabela Tramitação para cada questionário. Com o id, na variável "tramitação",
    # utilizo o id retornado para filtrar o setor do usuario logado. e por fim, na variável "questionário", listo os questionários que contem os ids
    # da variável "tramitação".
    ultima_tramitacao = Tramitacao.objects.values('questionario').annotate(id_ultimo=Max('id'))
    tramitacao = Tramitacao.objects.filter(pk__in=[i['id_ultimo'] for i in ultima_tramitacao]).filter(setor=request.user.funcao)
    questionarios = q.filter(pk__in=[t.questionario.id for t in tramitacao])
    avaliacoes_recebidas = questionarios.count()
    validacoes = Validacao.objects.filter(usuario=request.user)
    municipios = Municipio.objects.filter(pk__in=questionarios.values_list('entidade__municipio', flat=True))
    entidades =  Entidade.objects.filter(pk__in=questionarios.values_list('entidade', flat=True))
    status = Questionario.STATUS_CHOICES

    uf_filtro = request.GET.get('uf_filtro', None)
    municipio_filtro = request.GET.get('municipio_filtro', None)
    ug_filtro = request.GET.get('ug_filtro', None)
    setor_filtro = request.GET.get('setor_filtro', None)
    status_filtro = request.GET.get('status_filtro', None)

    if uf_filtro != '' and uf_filtro is not None:
        questionarios = questionarios.filter(entidade__municipio__uf=uf_filtro)
    if municipio_filtro != '' and municipio_filtro is not None:
        questionarios = questionarios.filter(entidade__municipio=municipio_filtro)
    if ug_filtro != '' and ug_filtro is not None:
        questionarios = questionarios.filter(entidade=ug_filtro)
    if setor_filtro != '' and setor_filtro is not None:
        questionarios = questionarios.filter(pk__in=Tramitacao.objects.filter(setor=setor_filtro).values_list('questionario', flat=True))
    if status_filtro != '' and status_filtro is not None:
        questionarios = questionarios.filter(status=status_filtro)
    
    return render(request, 'avaliacoes_setor.html', {'questionarios':questionarios,
                                                     'avaliacoes_recebidas':avaliacoes_recebidas, 
                                                    'validacoes':validacoes,
                                                    'municipios':municipios,
                                                    'entidades':entidades,
                                                    'status':status})