from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from avaliacoes.models import Avaliacao
from questionarios.models import Questionario
from usuarios.models import User


@login_required
def home(request):
    avaliacoes = Avaliacao.objects.all()
    questionarios = Questionario.objects.all()[0:10]
    total_usuarios = User.objects.filter(is_active=True).count()
    avaliacoes_recebidas = Questionario.objects.all().count()
    avaliacoes_respondidas = Questionario.objects.filter(usuario=request.user).count()

    context = {
        'avaliacoes':avaliacoes, 
        'questionarios':questionarios,
        'total_usuarios':total_usuarios,
        'avaliacoes_recebidas':avaliacoes_recebidas,
        'avaliacoes_respondidas':avaliacoes_respondidas}
    
    return render(request, 'home.html', context)