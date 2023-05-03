from django.shortcuts import render
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from .models import User
from django.contrib.auth.decorators import login_required
from .forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
import os


def add_usuario(request):
    if request.method == 'GET':
        form = UserCreationForm()
        return render(request, 'add_usuario.html', {'form':form})
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            entidade = form.cleaned_data['entidade']
            user_entidade = User.objects.filter(entidade__in=entidade)

            if user_entidade:
                messages.error(request, "Esta UG já está vinculada a outro usuário! Tente outra, por favor.")
                return redirect(reverse('add_usuario'))
            else:
                user.save()
                # this will save by itself
                user.entidade.set(entidade)
                login(request, user)
                messages.success(request, "Usuário cadastrado com sucesso!")
                return redirect(reverse('home'))
            
        messages.error(request, "Este usuário já existe! Tente outro, por favor.")
        return redirect(reverse('add_usuario'))


@login_required
def perfil(request):
    if request.method == 'GET':
        return render(request, 'perfil.html')
    
    if request.method == 'POST':
        user = get_object_or_404(User, pk=request.user.id)
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')

        user.first_name = first_name
        user.last_name = last_name
        user.email = email
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


    