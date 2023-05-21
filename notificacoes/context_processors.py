from .notifications import get_unread_notifications_user, total_notificacoes


def notificacoes_unread(request):
    if request.user.is_authenticated:
        notificacoes_unread = get_unread_notifications_user(request.user)
        notificacoes_total_unread = total_notificacoes(request.user)
    else:
        notificacoes_unread = None
        notificacoes_total_unread = None

    context = {'notificacoes_unread':notificacoes_unread,
            'notificacoes_total_unread':notificacoes_total_unread}
        
    return context