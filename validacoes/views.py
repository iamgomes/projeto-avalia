from django.shortcuts import render
from django.http import HttpResponse
from . models import RespostaValidacao, Validacao
from questionarios.models import Questionario, Resposta, Criterio
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages


@login_required
def add_validacao(request, id):
    usuario = request.user
    questionario = get_object_or_404(Questionario, pk=id)

    validacao = Validacao(usuario=usuario, questionario_id=questionario.id)
    validacao.save()
    id_validacao = validacao.id

    questionario.status = 'EV'
    questionario.save()

    messages.success(request, "Ótimo! Vamos começar a validar.")

    return redirect(reverse('add_resposta_validacao', args=(id,id_validacao)))


@login_required
def add_resposta_validacao(request, id, id_validacao):

    questionario = Questionario.objects.get(pk=id)
    validacao = get_object_or_404(Validacao, pk=id_validacao)
    respostas = Resposta.objects.filter(questionario_id=id)

    if request.method == 'GET':
        questionario.status = 'EV'
        questionario.save()

        return render(request, 'add_resposta_validacao.html', {'questionario':questionario})
    
    if request.method == 'POST':
        for i in respostas:
            id_resposta = request.POST.get('id_resposta-{}'.format(i.id))            
            form = request.POST.get('resposta-{}'.format(i.id))

            if form == 'on':
                resposta_validacao = RespostaValidacao(validacao=validacao,resposta_id=id_resposta,resposta_validacao=True)
                resposta_validacao.save()
            else:
                resposta_validacao = RespostaValidacao(validacao=validacao,resposta_id=id_resposta)
                resposta_validacao.save()

        questionario.status = 'V'
        questionario.save()

        messages.success(request, "Validação feita com sucesso!")

        return redirect(reverse('avaliacao'))


@login_required
def change_resposta_validacao(request, id):
    validacao = get_object_or_404(Validacao, pk=id)
    questionario = Questionario.objects.get(pk=validacao.questionario.id)

    if request.method == 'GET':
        questionario.status = 'EV'
        questionario.save()

        return render(request, 'resposta_validacao_form.html', {'validacao':validacao})
    
    if request.method == 'POST':
        for i in validacao.respostavalidacao_set.all():
            id_resposta = request.POST.get('id_resposta-{}'.format(i.id))
            form = request.POST.get('resposta-{}'.format(i.id))

            resposta = get_object_or_404(RespostaValidacao, pk=id_resposta)

            if form == 'on':
                resposta.resposta_validacao = True
                resposta.save()
            else:
                resposta.resposta_validacao = False
                resposta.save()

        questionario.status = 'V'
        questionario.save()

        messages.success(request, "Resposta de validação alterada com sucesso!")

        return redirect(reverse('avaliacao'))
