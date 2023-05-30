from django.shortcuts import render
from django.http import HttpResponse
from . models import RespostaValidacao, Validacao, LinkEvidenciaValidacao, ImagemEvidenciaValidacao, JustificativaEvidenciaValidacao
from questionarios.models import Questionario, Resposta, Criterio
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import os


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
    questionario = Questionario.objects.get(pk=id)
    validacao = get_object_or_404(Validacao, pk=id_validacao)
    respostas = Resposta.objects.filter(questionario_id=id)

    if request.method == 'GET':
        questionario.status = 'EV'
        questionario.save()

        return render(request, 'add_resposta_validacao.html', {'questionario':questionario, 'respostas':respostas})
    
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
                    imagem_validacao = ImagemEvidenciaValidacao(resposta_validacao_id=resposta_validacao.id, imagem_validacao=i)
                    imagem_validacao.save()

            if justificativa:
                justifica = JustificativaEvidenciaValidacao(resposta_validacao_id=resposta_validacao.id, justificativa_validacao=justificativa)
                justifica.save()

        questionario.status = 'V'
        questionario.save()

        messages.success(request, "Validação feita com sucesso!")

        return redirect(reverse('minhas_validacoes'))


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
            id_link = request.POST.getlist('id_link-{}'.format(i.id))            
            form_link = request.POST.getlist('link-{}'.format(i.id))
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
                    for i, l in zip(id_link,form_link):
                        link = get_object_or_404(LinkEvidenciaValidacao, pk=i)
                        link.link = l
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
                            imagem_evidencia = ImagemEvidenciaValidacao(resposta_validacao_id=resposta.id, imagem_validacao=i)
                            imagem_evidencia.save()

            if id_imagens:
                for i, l in zip(id_imagens,imagens):
                    imagem = get_object_or_404(ImagemEvidenciaValidacao, pk=i)
                    if len(request.FILES) != 0:
                        if len(imagem.imagem_validacao) > 0:
                            os.remove(imagem.imagem_validacao.path)     
                        imagem.imagem_validacao = l
                    imagem.save()
            

            if resposta.criterio_item.item_avaliacao.id == 1:
                if not resposta.justificativaevidenciavalidacao_set.all():
                    if justificativa_novo:
                        justifica = JustificativaEvidenciaValidacao(resposta_validacao_id=resposta.id, justificativa_validacao=justificativa_novo)
                        justifica.save()

            if id_justificativa:
                justifica = get_object_or_404(JustificativaEvidenciaValidacao, pk=id_justificativa)
                justifica.justificativa_validacao = justificativa
                justifica.save()

        questionario.status = 'V'
        questionario.save()

        messages.success(request, "Resposta de validação alterada com sucesso!")

        return redirect(reverse('minhas_validacoes'))


@login_required
def delete_validacao(request, id):
    validacao = get_object_or_404(Validacao, pk=id)
    questionario = Questionario.objects.get(pk=validacao.questionario.id)

    validacao.delete()

    questionario.status = 'F'
    questionario.save()
    
    return redirect(reverse('minhas_validacoes'))