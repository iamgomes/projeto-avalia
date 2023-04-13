from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from avaliacoes.models import Avaliacao, UsuarioAvaliacao
from usuarios.models import User


@login_required
def home(request):
    avaliacoes = Avaliacao.objects.all()
    formularios = UsuarioAvaliacao.objects.all()[0:10]
    total_usuarios = User.objects.filter(is_active=True).count()
    avaliacoes_recebidas = UsuarioAvaliacao.objects.all().count()
    avaliacoes_respondidas = UsuarioAvaliacao.objects.filter(usuario=request.user).count()

    context = {
        'avaliacoes':avaliacoes, 
        'formularios':formularios,
        'total_usuarios':total_usuarios,
        'avaliacoes_recebidas':avaliacoes_recebidas,
        'avaliacoes_respondidas':avaliacoes_respondidas}
    
    return render(request, 'home.html', context)