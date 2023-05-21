from notifications.models import Notification

def get_unread_notifications_user(user):
    unread_notifications = Notification.objects.unread().filter(recipient=user)
    return unread_notifications

def total_notificacoes(user):
    return get_unread_notifications_user(user).count()


def get_all_notifications_user(user):
    all_notifications = Notification.objects.filter(recipient=user)
    return all_notifications