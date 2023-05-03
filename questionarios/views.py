from django.shortcuts import render
from django.http import HttpResponse
from . models import Avaliacao, Questionario, Resposta, LinkEvidencia, ImagemEvidencia, \
    CriterioItem, Tramitacao
from validacoes.models import RespostaValidacao, Validacao
from usuarios.models import User
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from entidades.models import Entidade
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import datetime
import os


@login_required
def add_questionario(request, id):
    avaliacao = Avaliacao.objects.get(pk=id)
    usuario = User.objects.get(pk=request.user.id)

    if request.method == 'GET':
        entidades = usuario.entidade.all()
        return render(request, 'add_questionario.html', {'id':id, 'entidades':entidades})
        
    elif request.method == 'POST':
        usuario = request.user
        entidade = request.POST.get('entidade')
        site = request.POST.get('site')
        hoje = datetime.datetime.now()
        final = avaliacao.data_final

        if not Questionario.objects.filter(avaliacao_id=avaliacao.id, entidade_id=entidade):

            if hoje.timestamp() < final.timestamp():

                questionario = Questionario(avaliacao_id=avaliacao.id, usuario=usuario, entidade_id=entidade)
                
                if site == 'N':
                    questionario.status = 'NS'
                    questionario.save()
                    tramitacao = Tramitacao(questionario_id=questionario.id, usuario=usuario)
                    tramitacao.save()

                    messages.success(request, "Sua avaliação foi finalizada.")
                    return redirect(reverse('avaliacao'))
                
                else:
                    questionario.save()

                    if request.user.funcao == 'C':
                        tramitacao = Tramitacao(questionario_id=questionario.id, setor='C', motivo='AI', usuario=usuario)
                        tramitacao.save()

                        messages.success(request, "Muito bom! Você iniciou uma avaliação.")

                        # redireciona para página de resposta passando como parâmetro o id criado
                        return redirect(reverse('add_resposta', args=(questionario.id,)))
                    
                    if request.user.funcao == 'A':
                        tramitacao = Tramitacao(questionario_id=questionario.id, setor='T', motivo='IT', usuario=usuario)
                        tramitacao.save()

                        messages.success(request, "Muito bom! Você iniciou uma avaliação pelo Tribunal.")

                         # redireciona para página de resposta passando como parâmetro o id criado
                        return redirect(reverse('add_resposta', args=(questionario.id,)))

            elif hoje.timestamp() > final.timestamp():
                messages.error(request, "Desculpe, o prazo desta avaliação já esgotou.")
                return redirect(reverse('home'))
        else:
            messages.error(request, "Desculpe, esta entidade já possui avaliação respondida.")
            return redirect(reverse('home'))


@login_required
def delete_questionario(request, id):
    questionario = get_object_or_404(Questionario, pk=id)
    questionario.delete()
    
    return redirect(reverse('minhas_avaliacoes'))


@login_required
def view_questionario(request, id):
    questionario = get_object_or_404(Questionario, pk=id)
    tramitacao = Tramitacao.objects.filter(questionario_id=questionario.id)
    respostas = Resposta.objects.filter(questionario_id=id)
    
    return render(request, 'view_questionario.html', {'questionario':questionario, 'tramitacao':tramitacao, 'respostas':respostas})


@login_required
def add_resposta(request, id):
    questionario = Questionario.objects.get(pk=id)

    if request.method == 'GET':
        return render(request, 'add_resposta.html', {'questionario':questionario})
    
    elif request.method == 'POST':
        for c in questionario.avaliacao.criterio_set.all():
            
            links = request.POST.get('link-{}'.format(c.id))

            for d in c.itens_avaliacao.all():
                form = request.POST.get('item_avaliacao-{}-{}'.format(c.id, d.id))
                imagens = request.FILES.getlist('imagem-{}-{}'.format(c.id, d.id))

                criterio_item = CriterioItem.objects.filter(criterio_id=c.id).filter(item_avaliacao_id=d.id)
                
                if form == 'on':
                    resposta = Resposta(questionario_id=questionario.id, criterio_item_id=criterio_item[0].id, resposta=True)
                    resposta.save()

                    if links:
                        #TODO: melhorar essa solução. Aqui estou salvando os links no primeiro item do critério apenas.
                        if d.id == 1:
                            link_evidencia = LinkEvidencia(resposta_id=resposta.id, link=links)
                            link_evidencia.save()

                else: 
                    resposta = Resposta(questionario_id=questionario.id, criterio_item_id=criterio_item[0].id)
                    resposta.save()

                    if imagens:
                        if d.id == 1:
                            for i in imagens:
                                imagem_evidencia = ImagemEvidencia(resposta_id=resposta.id, imagem=i)
                                imagem_evidencia.save()
                
        questionario.status = 'F'
        questionario.save()
            
        messages.success(request, "Resposta cadastrada com sucesso!")

        return redirect(reverse('minhas_avaliacoes'))
    

@login_required
def change_resposta(request, id):
    questionario = Questionario.objects.get(pk=id)
    respostas = Resposta.objects.filter(questionario_id=id)

    if request.method == 'GET':
        questionario.status = 'E'
        questionario.save()

        return render(request, 'resposta_form.html', {'questionario':questionario})
    
    if request.method == 'POST':
        for i in respostas:
            id_resposta = request.POST.get('id_resposta-{}'.format(i.id))            
            form = request.POST.get('resposta-{}'.format(i.id))
            id_link = request.POST.getlist('id_link-{}'.format(i.id))            
            form_link = request.POST.getlist('link-{}'.format(i.id))
            form_link_novo = request.POST.get('link_novo-{}'.format(i.id))
            id_imagens = request.POST.getlist('id_imagem-{}'.format(i.id))            
            imagens = request.FILES.getlist('imagem-{}'.format(i.id))
            imagens_novo = request.FILES.getlist('imagem_novo-{}'.format(i.id))
            
            resposta = get_object_or_404(Resposta, pk=id_resposta)

            if form == 'on':
                resposta.resposta = True
                resposta.save()

                if resposta.criterio_item.item_avaliacao.id == 1:
                    if not resposta.linkevidencia_set.all():
                        if form_link_novo:
                            link_evidencia = LinkEvidencia(resposta_id=resposta.id, link=form_link_novo)
                            link_evidencia.save()
                            
            else:
                resposta.resposta = False
                resposta.save()

                if resposta.criterio_item.item_avaliacao.id == 1:
                    if not resposta.imagemevidencia_set.all():
                        if imagens_novo:
                            for i in imagens_novo:
                                imagem_evidencia = ImagemEvidencia(resposta_id=resposta.id, imagem=i)
                                imagem_evidencia.save()

            if id_link:
                for i, l in zip(id_link,form_link):
                    link = get_object_or_404(LinkEvidencia, pk=i)
                    link.link = l
                    link.save()

            if id_imagens:
                for i, l in zip(id_imagens,imagens):
                    imagem = get_object_or_404(ImagemEvidencia, pk=i)
                    if len(request.FILES) != 0:
                        if len(imagem.imagem) > 0:
                            os.remove(imagem.imagem.path)     
                        imagem.imagem = l
                    imagem.save() 

        questionario.status = 'F'
        questionario.save()

        messages.success(request, "Resposta de avaliação alterada com sucesso!")

        return redirect(reverse('minhas_avaliacoes'))
