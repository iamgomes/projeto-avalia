from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from avaliacoes.models import Avaliacao
from questionarios.models import Questionario
from validacoes.models import Validacao
from usuarios.models import User
from avisos.models import Aviso


@login_required
def home(request):
    avaliacoes = Avaliacao.objects.all()
    questionarios = Questionario.objects.all()[0:10]
    total_usuarios = User.objects.filter(is_active=True).count()
    avaliacoes_recebidas = Questionario.objects.all().count()
    avaliacoes_respondidas = Questionario.objects.filter(usuario=request.user).count()
    validacoes_respondidas = Validacao.objects.filter(usuario=request.user).count()
    avisos = Aviso.objects.filter(ativo=True)[:1]

    context = {
        'avaliacoes':avaliacoes, 
        'questionarios':questionarios,
        'total_usuarios':total_usuarios,
        'avaliacoes_recebidas':avaliacoes_recebidas,
        'avaliacoes_respondidas':avaliacoes_respondidas,
        'validacoes_respondidas':validacoes_respondidas,
        'avisos':avisos,
    }
    
    return render(request, 'home.html', context)