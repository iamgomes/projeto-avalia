from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from . models import Avaliacao
from questionarios.models import Questionario, Tramitacao
from validacoes.models import Validacao
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import TramitacaoForm
import json
from entidades.uf_choices import UfChoices
from entidades.models import Municipio, Entidade



@login_required
def avaliacao(request):
    if request.method == 'GET':
        questionarios = Questionario.objects.all()
        avaliacoes_recebidas = questionarios.count()
        form = TramitacaoForm()
        setores = Tramitacao.SETOR_CHOICES
        motivos = []
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
                                                   'form':form,
                                                   'setores':setores,
                                                   'motivos':motivos,
                                                   'estados':estados,
                                                   'municipios':municipios,
                                                   'entidades':entidades,
                                                   'status':status})
    
    if request.method == 'POST':
        form = TramitacaoForm(request.POST)
        if form.is_valid():
            tramitacao = form.save(commit=False)
            tramitacao.usuario_id = request.user.id
            tramitacao.questionario_id = request.POST.get('id_questionario')
            tramitacao.save()
            
        messages.success(request, "Questionário tramitado com sucesso!")
        return redirect(reverse('avaliacao'))


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
        form = TramitacaoForm()
        setores = Tramitacao.SETOR_CHOICES
        motivos = []
    
        return render(request, 'minhas_avaliacoes.html', {'questionarios':questionarios, 
                                                          'validacoes':validacoes,
                                                            'form':form,
                                                            'setores':setores,
                                                            'motivos':motivos,})
    if request.method == 'POST':
        form = TramitacaoForm(request.POST)
        if form.is_valid():
            tramitacao = form.save(commit=False)
            tramitacao.usuario_id = request.user.id
            tramitacao.questionario_id = request.POST.get('id_questionario')
            tramitacao.save()
            
        messages.success(request, "Questionário tramitado com sucesso!")
        return redirect(reverse('minhas_avaliacoes'))


@login_required
def avaliacoes_setor(request):
    questionarios = Questionario.objects.filter(entidade__municipio__uf=request.user.municipio.uf).\
        filter(pk__in=Tramitacao.objects.filter(setor=request.user.funcao).values_list('questionario', flat=True))
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



def handler404(request, exception):
    return render(request, "404.html")

def handler500(request, exception=None):
    return render(request, "500.html")

def custom_permission_denied_view(request, exception=None):
    return render(request, "403.html", {})

def custom_bad_request_view(request, exception=None):
    return render(request, "400.html", {})