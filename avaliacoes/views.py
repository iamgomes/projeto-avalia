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
from django.core import serializers
import json


@login_required
def avaliacao(request):
    if request.method == 'GET':
        questionarios = Questionario.objects.all()
        avaliacoes_recebidas = Questionario.objects.all().count()
        form = TramitacaoForm()
        setores = Tramitacao.SETOR_CHOICES
        motivos = []
        
        return render(request, 'avaliacoes.html', {'questionarios':questionarios, 
                                                   'avaliacoes_recebidas':avaliacoes_recebidas, 
                                                   'form':form,
                                                   'setores':setores,
                                                   'motivos':motivos})
    
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
    questionarios = Questionario.objects.filter(usuario=request.user)
    validacoes = Validacao.objects.filter(usuario=request.user)
    
    return render(request, 'minhas_avaliacoes.html', {'questionarios':questionarios, 'validacoes':validacoes})



def handler404(request, exception):
    return render(request, "404.html")

def handler500(request, exception=None):
    return render(request, "500.html")

def custom_permission_denied_view(request, exception=None):
    return render(request, "403.html", {})

def custom_bad_request_view(request, exception=None):
    return render(request, "400.html", {})