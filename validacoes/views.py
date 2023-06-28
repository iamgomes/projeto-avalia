from django.shortcuts import render
from django.http import JsonResponse
from . models import RespostaValidacao, Validacao, LinkEvidenciaValidacao, ImagemEvidenciaValidacao,\
    JustificativaEvidenciaValidacao, RespostaValidacao
from questionarios.models import Questionario, Resposta, Criterio
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import os
from django.db.models import Q
import datetime
from notifications.signals import notify
from django.db.models import Prefetch
from questionarios.minhas_funcoes import altera_imagem_validacao


@login_required
def add_validacao(request, id):
    usuario = request.user
    questionario = get_object_or_404(Questionario, pk=id)

    validacao = Validacao(usuario=usuario, questionario_id=questionario.id)
    validacao.save()

    questionario.status = 'EV'
    questionario.save()

    messages.success(request, "Ótimo! Vamos começar a validar.")

    return redirect(reverse('add_resposta_validacao', args=(id,validacao.id)))


@login_required
def add_resposta_validacao(request, id, id_validacao):
    q = Questionario.objects.get(pk=id)
    #questionario = q.avaliacao.criterio_set.filter(Q(matriz='C') | Q(matriz=q.entidade.poder))
    questionario = Criterio.objects.filter(avaliacao=q.avaliacao.id).filter(matriz__in=['C', q.entidade.poder])\
    .select_related('avaliacao','dimensao')\
    .prefetch_related('criterioitem_set',
                        'criterioitem_set__item_avaliacao',
                        Prefetch('criterioitem_set__resposta_set', queryset=Resposta.objects.filter(questionario=q)),
                        'criterioitem_set__resposta_set__linkevidencia_set',
                        'criterioitem_set__resposta_set__justificativaevidencia_set',
                        'criterioitem_set__resposta_set__imagemevidencia_set',
                        )
    validacao = get_object_or_404(Validacao, pk=id_validacao)
    respostas = Resposta.objects.filter(questionario_id=id)
    hoje = datetime.datetime.now()
    inicio = q.avaliacao.data_inicial_validacao
    fim = q.avaliacao.data_final_validacao

    if request.method == 'GET':
        if hoje.timestamp() >= inicio.timestamp() and hoje.timestamp() <= fim.timestamp():
            return render(request, 'add_resposta_validacao.html', {'questionario':questionario, 'q':q, 'respostas':respostas})
        else:
            messages.warning(request, "Desculpe, você está fora do prazo de validação.")
            return redirect(reverse('minhas_validacoes'))
    
    if request.method == 'POST':
        for i in respostas:
            id_resposta = request.POST.get('id_resposta-{}'.format(i.id))            
            form = request.POST.get('resposta-{}'.format(i.id))
            form_link = request.POST.get('link-{}'.format(i.id))
            imagens = request.FILES.getlist('imagem-{}'.format(i.id))
            justificativa = request.POST.get('justificativa-{}'.format(i.id))

            if form == 'on':
                resposta_validacao = RespostaValidacao(validacao=validacao,criterio_item_id=i.criterio_item_id, resposta_id=id_resposta,resposta_validacao=True)
                resposta_validacao.save()
                    
                if form_link:
                    link_evidencia = LinkEvidenciaValidacao(resposta_validacao_id=resposta_validacao.id, link_validacao=form_link)
                    link_evidencia.save()

            else:
                resposta_validacao = RespostaValidacao(validacao=validacao,criterio_item_id=i.criterio_item_id,resposta_id=id_resposta)
                resposta_validacao.save()

            if imagens:
                for i in imagens:
                    imagem_validacao = ImagemEvidenciaValidacao(resposta_validacao_id=resposta_validacao.id, imagem_validacao=altera_imagem_validacao(i,resposta_validacao))
                    imagem_validacao.save()

            if justificativa:
                justifica = JustificativaEvidenciaValidacao(resposta_validacao_id=resposta_validacao.id, justificativa_validacao=justificativa)
                justifica.save()

        acao = request.POST.get('acao') 
            
        if acao == 'Salvar':
            q.status = 'EV'
            q.save()
            validacao.save()
            messages.info(request, "Validação salva com sucesso! Para retornar, basta editá-la.")
            return redirect(reverse('minhas_validacoes'))

        else:
            q.status = 'V'
            q.save()
            validacao.save()
            # Envia notificação para o Usuário
            notify.send(request.user, recipient=q.usuario, verb=f'{q.entidade}', target=q, description=f'Questionário validado por {request.user.first_name}.')
            messages.success(request, "Validação finalizada com sucesso!")
            return redirect(reverse('minhas_validacoes'))



@login_required
def change_resposta_validacao(request, id):
    v = Validacao.objects.filter(pk=id).select_related('questionario','usuario').first()
    #validacao = v.questionario.avaliacao.criterio_set.filter(Q(matriz='C') | Q(matriz=v.questionario.entidade.poder))
    validacao = Criterio.objects.filter(avaliacao=v.questionario.avaliacao.id).filter(matriz__in=['C', v.questionario.entidade.poder])\
    .select_related('avaliacao','dimensao')\
    .prefetch_related('criterioitem_set',
                        'criterioitem_set__item_avaliacao',
                        Prefetch('criterioitem_set__resposta_set', queryset=Resposta.objects.filter(questionario=v.questionario)),
                        'criterioitem_set__resposta_set__linkevidencia_set',
                        'criterioitem_set__resposta_set__justificativaevidencia_set',
                        'criterioitem_set__resposta_set__imagemevidencia_set',
                        Prefetch('criterioitem_set__respostavalidacao_set', queryset=RespostaValidacao.objects.filter(validacao=v)),
                        'criterioitem_set__respostavalidacao_set__linkevidenciavalidacao_set',
                        'criterioitem_set__respostavalidacao_set__justificativaevidenciavalidacao_set',
                        'criterioitem_set__respostavalidacao_set__imagemevidenciavalidacao_set',
                        )
    hoje = datetime.datetime.now()
    inicio = v.questionario.avaliacao.data_inicial_validacao
    fim = v.questionario.avaliacao.data_final_validacao

    if request.method == 'GET':
        if hoje.timestamp() >= inicio.timestamp() and hoje.timestamp() <= fim.timestamp():
            v.questionario.status = 'EV'
            v.questionario.save()
            return render(request, 'resposta_validacao_form.html', {'validacao':validacao, 'v':v})
        else:
            messages.warning(request, "Desculpe, você está fora do prazo de validação.")
            return redirect(reverse('view_questionario', args=(v.questionario.id,))) 
           
    if request.method == 'POST':
        for i in v.respostavalidacao_set.all():
            id_resposta = request.POST.get('id_resposta-{}'.format(i.id))
            form = request.POST.get('resposta-{}'.format(i.id))
            id_link = request.POST.get('id_link-{}'.format(i.id))            
            form_link = request.POST.get('link-{}'.format(i.id))
            form_link_novo = request.POST.get('link_novo-{}'.format(i.id))
            id_imagens = request.POST.getlist('id_imagem-{}'.format(i.id))            
            imagens = request.FILES.getlist('imagem-{}'.format(i.id))
            imagens_novo = request.FILES.getlist('imagem_novo-{}'.format(i.id))
            id_justificativa = request.POST.get('id_justificativa-{}'.format(i.id))
            justificativa = request.POST.get('justificativa-{}'.format(i.id))
            justificativa_novo = request.POST.get('justificativa_novo-{}'.format(i.id))

            resposta = get_object_or_404(RespostaValidacao, pk=id_resposta)

            if form == 'on':
                resposta.resposta_validacao = True
                resposta.save()

                if resposta.criterio_item.item_avaliacao.id == 1:
                    if not resposta.linkevidenciavalidacao_set.all():
                        if form_link_novo:
                            link_evidencia = LinkEvidenciaValidacao(resposta_validacao_id=resposta.id, link_validacao=form_link_novo)
                            link_evidencia.save()

                if id_link:
                    link = get_object_or_404(LinkEvidenciaValidacao, pk=id_link)
                    link.link_validacao = form_link
                    link.save()

            else:
                if resposta.criterio_item.item_avaliacao.id == 1:
                    if resposta.linkevidenciavalidacao_set.all():
                        resposta.linkevidenciavalidacao_set.all().delete()

                resposta.resposta_validacao = False
                resposta.save()

            if resposta.criterio_item.item_avaliacao.id == 1:
                if not resposta.imagemevidenciavalidacao_set.all():
                    if imagens_novo:
                        for i in imagens_novo:
                            imagem_evidencia = ImagemEvidenciaValidacao(resposta_validacao_id=resposta.id, imagem_validacao=altera_imagem_validacao(i,resposta))
                            imagem_evidencia.save()

            if id_imagens and imagens:
                for i, l in zip(id_imagens,imagens):
                    imagem = get_object_or_404(ImagemEvidenciaValidacao, pk=i)
                    if len(request.FILES) != 0:
                        if len(imagem.imagem_validacao) > 0:
                            imagem.delete()   
                        imagem.imagem_validacao = altera_imagem_validacao(l,resposta)
                    imagem.save()
            else:
                for i in imagens:
                    imagem_evidencia = ImagemEvidenciaValidacao(resposta_validacao_id=resposta.id, imagem_validacao=altera_imagem_validacao(i,resposta))
                    imagem_evidencia.save()

            if resposta.criterio_item.item_avaliacao.id == 1:
                if not resposta.justificativaevidenciavalidacao_set.all():
                    if justificativa_novo:
                        justifica = JustificativaEvidenciaValidacao(resposta_validacao_id=resposta.id, justificativa_validacao=justificativa_novo)
                        justifica.save()

            if id_justificativa:
                justifica = get_object_or_404(JustificativaEvidenciaValidacao, pk=id_justificativa)
                justifica.justificativa_validacao = justificativa
                justifica.save()

        acao = request.POST.get('acao') 
            
        if acao == 'Salvar':
            v.questionario.status = 'EV'
            v.questionario.save()
            v.save()
            messages.info(request, "Validação salva com sucesso! Para retornar, basta editá-la.")
            return redirect(reverse('minhas_validacoes'))

        else:
            v.questionario.status  = 'V'
            v.questionario.save()
            v.save()
            # Envia notificação para o Usuário
            notify.send(request.user, recipient=v.questionario.usuario, verb=f'{v.questionario.entidade}', target=v.questionario, description=f'Questionário validado por {request.user.first_name}.')
            messages.success(request, "Validação alterada com sucesso!")
            return redirect(reverse('minhas_validacoes'))


@login_required
def delete_validacao(request, id):
    validacao = get_object_or_404(Validacao, pk=id)
    questionario = Questionario.objects.get(pk=validacao.questionario.id)

    validacao.delete()

    questionario.status = 'F'
    questionario.save()
    
    return redirect(reverse('minhas_validacoes'))


@login_required
def delete_imagem_validacao(request, id):
    imagem = get_object_or_404(ImagemEvidenciaValidacao, pk=id)
    imagem.delete()
    return JsonResponse({'mensagem':'Imagem removida com sucesso!'})