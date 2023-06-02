from django.shortcuts import render
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from .models import User
from entidades.models import Municipio
from django.contrib.auth.decorators import login_required
from .forms import UserCreationForm, UserChangeForm
from django.contrib.auth import login
from django.contrib import messages
import os


def add_usuario(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            entidade = form.cleaned_data['entidade']
            usuario_entidade = User.objects.exclude(entidade__poder='T').filter(entidade__in=entidade)
            
            if usuario_entidade.exists():
                messages.warning(request, "Esta UG já está vinculada a outro usuário! Tente outra, por favor.")
                return render(request, 'add_usuario.html', {'form': form})
            
            user = form.save()
            user.entidade.set(entidade)
            login(request, user)
            messages.success(request, "Usuário cadastrado com sucesso!")
            return redirect(reverse('home'))

    else:
        form = UserCreationForm()
    
    return render(request, 'add_usuario.html', {'form': form})
        

@login_required
def perfil(request):
    if request.method == 'GET':
        return render(request, 'perfil.html')
    
    if request.method == 'POST':
        user = get_object_or_404(User, pk=request.user.id)
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        celular = request.POST.get('celular')

        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.celular = celular
        user.save()

        messages.success(request, "Usuário alterado com sucesso!")

        return redirect(reverse('perfil'))
    

@login_required
def change_foto(request):
    user = User.objects.get(pk=request.user.id)

    if request.method == 'GET':
        return render(request, 'change_foto.html')
    
    if request.method == 'POST':
        if len(request.FILES) != 0:
            if user.foto:
                if len(user.foto) > 0:
                    os.remove(user.foto.path)     
            user.foto = request.FILES['foto']
        user.save()   

        messages.success(request, "Foto de Usuário alterada com sucesso!")

        return redirect(reverse('perfil'))
    

@login_required
def usuarios(request):
    users = User.objects.filter(municipio__uf=request.user.municipio.uf)

    return render(request, 'usuarios.html', {'users':users})


@login_required
def change_usuario(request, id):
    usuario = get_object_or_404(User, id=id)
    
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuário alterado com sucesso!")
            return redirect(reverse('usuarios'))
    else:
        form = UserChangeForm(instance=usuario)
        form.fields["municipio"].queryset = Municipio.objects.filter(uf=request.user.municipio.uf)
        form.fields["setor"].choices = (f for f in User.SETOR_CHOICES if f[0] != 'A')
        
    return render(request, 'change_usuario.html', {'form': form})
    