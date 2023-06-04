from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views


urlpatterns = [    
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('usuarios/', include('usuarios.urls')),
    path('entidades/', include('entidades.urls')),
    path('avaliacoes/', include('avaliacoes.urls')),
    path('questionarios/', include('questionarios.urls')),
    path('validacoes/', include('validacoes.urls')),
    path('notificacoes/', include('notificacoes.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('chaining/', include('smart_selects.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = 'Avalia'
admin.site.index_title = 'Administração'