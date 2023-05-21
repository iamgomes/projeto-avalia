from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .notifications import get_all_notifications_user
from notifications.models import Notification
from django.contrib import messages


@login_required
def lista_notificacoes(request):
    notificacoes = get_all_notifications_user(request.user)
    
    return render(request, 'notificacoes.html', {'notificacoes':notificacoes,})


@login_required
def all_notificacao_lida(request):
    Notification.objects.mark_all_as_read(recipient=request.user)
    
    messages.success(request, "Notificações marcadas como lida.")

    return redirect(reverse('home'))


@login_required
def delete_notificacao(request, id):
    notificacao = Notification.objects.get(pk=id)
    notificacao.delete()

    messages.success(request, "Notificação removida com sucesso.")

    return redirect(reverse('lista_notificacoes'))

