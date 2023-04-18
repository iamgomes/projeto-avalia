from django.shortcuts import render
from django.http import HttpResponse
from . models import Avaliacao, Questionario, Resposta, LinkEvidencia, ImagemEvidencia, \
    CriterioItem, Tramitacao
from usuarios.models import User
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from entidades.models import Entidade
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import datetime


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

                identificacao = Questionario(avaliacao_id=avaliacao.id, usuario=usuario, entidade_id=entidade)
                
                if site == 'N':
                    identificacao.status = 'NS'
                    identificacao.save()
                    messages.success(request, "Sua avaliação foi finalizada.")
                    return redirect(reverse('avaliacao'))
                
                else:
                    identificacao.save()
                    id_identificaca = identificacao.id

                    tramitacao = Tramitacao(questionario_id=id_identificaca, usuario=usuario)
                    tramitacao.save()

                    messages.success(request, "Muito bom! Você iniciou uma avaliação.")

                    # redireciona para página de resposta passando como parâmetro o id criado
                    return redirect(reverse('add_resposta', args=(id_identificaca,)))               

                
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
    
    return redirect(reverse('avaliacao'))


@login_required
def view_questionario(request, id):
    questionario = get_object_or_404(Questionario, pk=id)
    tramitacao = Tramitacao.objects.filter(questionario_id=questionario.id)
    
    return render(request, 'view_questionario.html', {'questionario':questionario, 'tramitacao':tramitacao})


@login_required
def add_resposta(request, id):
    questionario = Questionario.objects.get(pk=id)

    if request.method == 'GET':
        return render(request, 'add_resposta.html', {'questionario':questionario})
    
    elif request.method == 'POST':
        for c in questionario.avaliacao.criterio_set.all():
            
            links = request.POST.getlist('link-{}'.format(c.id))

            for d in c.itens_avaliacao.all():
                form = request.POST.get('item_avaliacao-{}-{}'.format(c.id, d.id))
                imagens = request.FILES.getlist('imagem-{}-{}'.format(c.id, d.id))

                criterio_item = CriterioItem.objects.filter(criterio_id=c.id).filter(item_avaliacao_id=d.id)
                
                if form == 'on':
                    resposta = Resposta(questionario_id=questionario.id, criterio_item_id=criterio_item[0].id, resposta=True)
                    resposta.save()

                    if links:
                        for l in links:
                            link_evidencia = LinkEvidencia(resposta_id=resposta.id, link=l)
                            link_evidencia.save()

                else: 
                    resposta = Resposta(questionario_id=questionario.id, criterio_item_id=criterio_item[0].id)
                    resposta.save()

                    if imagens:
                        for i in imagens:
                            imagem_evidencia = ImagemEvidencia(resposta_id=resposta.id, imagem=i)
                            imagem_evidencia.save()
                
        questionario.status = 'F'
        questionario.save()
            
        messages.success(request, "Resposta cadastrada com sucesso!")

        return redirect(reverse('avaliacao'))
    

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

            resposta = get_object_or_404(Resposta, pk=id_resposta)

            if form == 'on':
                resposta.resposta = True
                resposta.save()
            else:
                resposta.resposta = False
                resposta.save()

        questionario.status = 'F'
        questionario.save()

        messages.success(request, "Resposta de avaliação alterada com sucesso!")

        return redirect(reverse('avaliacao'))
