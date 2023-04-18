from django.shortcuts import render
from django.http import HttpResponse
from . models import Avaliacao
from questionarios.models import Questionario
from validacoes.models import Validacao
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages


@login_required
def avaliacao(request):
    questionarios = Questionario.objects.all()
    avaliacoes_recebidas = Questionario.objects.all().count()
    
    return render(request, 'avaliacoes.html', {'questionarios':questionarios, 'avaliacoes_recebidas':avaliacoes_recebidas})


@login_required
def envia_para_validacao(request, id):
    avaliacao = get_object_or_404(Questionario, pk=id)

    avaliacao.status = 'A'
    avaliacao.save()

    messages.success(request, "Parabéns! Sua avaliação foi enviada para validação.")

    return redirect(reverse('avaliacao'))
    

@login_required
def minhas_avaliacoes(request):
    questionario = Questionario.objects.filter(usuario=request.user)
    validacoes = Validacao.objects.filter(usuario=request.user)
    
    return render(request, 'minhas_avaliacoes.html', {'questionario':questionario, 'validacoes':validacoes})


def handler404(request, exception):
    return render(request, "404.html")

def handler500(request, exception=None):
    return render(request, "500.html")

def custom_permission_denied_view(request, exception=None):
    return render(request, "403.html", {})

def custom_bad_request_view(request, exception=None):
    return render(request, "400.html", {})