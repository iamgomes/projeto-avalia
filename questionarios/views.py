from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from . models import Avaliacao, Questionario, Resposta, LinkEvidencia, ImagemEvidencia, \
    CriterioItem, Tramitacao, JustificativaEvidencia, Criterio, Resposta
from validacoes.models import RespostaValidacao
from avaliacoes.models import Avaliacao
from usuarios.models import User
from .forms import TramitacaoForm
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from entidades.models import Entidade
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import datetime
import csv
from django.db.models import Q
from notifications.signals import notify
from django.db.models import Prefetch
import pathlib
from django.conf import settings


@login_required
def add_questionario(request, id):
    avaliacao = Avaliacao.objects.get(pk=id)
    usuario = User.objects.get(pk=request.user.id)
    hoje = datetime.datetime.now()
    inicio = avaliacao.data_inicial
    fim = avaliacao.data_final

    if request.method == 'GET':

        if hoje.timestamp() >= inicio.timestamp() and hoje.timestamp() <= fim.timestamp():

            if usuario.funcao == 'A':
                entidades = usuario.entidade.all()
            if usuario.funcao == 'V' or usuario.funcao == 'C':
                entidades = Entidade.objects.filter(municipio__uf=usuario.municipio.uf)

            return render(request, 'add_questionario.html', {'id':id, 'entidades':entidades})
        
        else:
            messages.warning(request, "Desculpe, você está fora do prazo deste projeto.")
            return redirect(reverse('home'))

    elif request.method == 'POST':
        usuario = usuario
        entidade = request.POST.get('entidade')
        site = request.POST.get('site')

        q = Questionario.objects.filter(avaliacao_id=avaliacao.id, entidade_id=entidade)

        if not q:

            questionario = Questionario(avaliacao_id=avaliacao.id, usuario=usuario, entidade_id=entidade)
            
            if site == 'N':
                if request.user.funcao == 'A':
                    questionario.status = 'F'
                    questionario.save()
                    tramitacao = Tramitacao(questionario_id=questionario.id, setor='C', motivo='AI', usuario=usuario)
                    tramitacao.save()

                    messages.success(request, "Sua avaliação foi finalizada.")
                    return redirect(reverse('minhas_avaliacoes'))
                
                if request.user.funcao == 'V' or request.user.funcao == 'C':
                    questionario.status = 'V'
                    questionario.save()
                    tramitacao = Tramitacao(questionario_id=questionario.id, setor='T', motivo='IT', usuario=usuario)
                    tramitacao.save()

                    messages.success(request, "Sua avaliação foi finalizada.")
                    return redirect(reverse('minhas_avaliacoes'))
                
            if site == 'S':
                if request.user.funcao == 'A':
                    questionario.save()
                    tramitacao = Tramitacao(questionario_id=questionario.id, setor='C', motivo='AI', usuario=usuario)
                    tramitacao.save()

                    messages.success(request, "Muito bom! Você iniciou uma avaliação.")

                    # redireciona para página de resposta passando como parâmetro o id criado
                    return redirect(reverse('add_resposta', args=(questionario.id,)))
                
                if request.user.funcao == 'V' or request.user.funcao == 'C':
                    questionario.save()
                    tramitacao = Tramitacao(questionario_id=questionario.id, setor='T', motivo='IT', usuario=usuario)
                    tramitacao.save()

                    messages.success(request, "Muito bom! Você iniciou uma avaliação pelo Tribunal.")

                        # redireciona para página de resposta passando como parâmetro o id criado
                    return redirect(reverse('add_resposta', args=(questionario.id,)))

        else:
            messages.error(request, "Desculpe, esta Unidade Gestora já possui avaliação vinculada ao usuário {} (@{}).".format(q.first().usuario.nome_completo, q.first().usuario))
            return redirect(reverse('home'))


@login_required
def delete_questionario(request, id):
    questionario = get_object_or_404(Questionario, pk=id)
    questionario.delete()
    
    return redirect(reverse('minhas_avaliacoes'))


@login_required
def view_questionario(request, id):
    q = Questionario.objects.filter(pk=id)\
        .select_related('avaliacao','usuario','entidade','validacao').prefetch_related('tramitacao_set','resposta_set',).first()
    #questionario = q.avaliacao.criterio_set.filter(matriz__in=['C', q.entidade.poder])
    try:
        if  q.validacao.set_all():
            questionario = Criterio.objects.filter(avaliacao__questionario=q.id).filter(matriz__in=['C', q.entidade.poder])\
                .select_related('avaliacao','dimensao')\
                .prefetch_related('criterioitem_set',
                                'criterioitem_set__item_avaliacao',
                                Prefetch('criterioitem_set__resposta_set', queryset=Resposta.objects.filter(questionario=q)),
                                Prefetch('criterioitem_set__resposta_set__linkevidencia_set', queryset=Resposta.objects.filter(questionario=q)),
                                'criterioitem_set__resposta_set__justificativaevidencia_set',
                                'criterioitem_set__resposta_set__imagemevidencia_set',
                                Prefetch('criterioitem_set__respostavalidacao_set', queryset=RespostaValidacao.objects.filter(validacao=q.validacao)),
                                'criterioitem_set__respostavalidacao_set__linkevidenciavalidacao_set',
                                'criterioitem_set__respostavalidacao_set__justificativaevidenciavalidacao_set',
                                'criterioitem_set__respostavalidacao_set__imagemevidenciavalidacao_set',
                                )
    except:
        questionario = Criterio.objects.filter(avaliacao__questionario=q.id).filter(matriz__in=['C', q.entidade.poder])\
            .select_related('avaliacao','dimensao')\
            .prefetch_related('criterioitem_set',
                    'criterioitem_set__item_avaliacao',
                    Prefetch('criterioitem_set__resposta_set', queryset=Resposta.objects.filter(questionario=q)),
                    'criterioitem_set__resposta_set__linkevidencia_set',
                    'criterioitem_set__resposta_set__justificativaevidencia_set',
                    'criterioitem_set__resposta_set__imagemevidencia_set',
                    )

    if request.method == 'GET':
        tramitacao = Tramitacao.objects.filter(questionario_id=q.id).select_related('usuario', 'questionario')
        form = TramitacaoForm()
        setores = Tramitacao.SETOR_CHOICES
        motivos = []
        
        return render(request, 'view_questionario.html', {'questionario':questionario,
                                                          'q':q,
                                                        'tramitacao':tramitacao, 
                                                        'form':form,
                                                        'setores':setores,
                                                        'motivos':motivos,})
    if request.method == 'POST':
        form = TramitacaoForm(request.POST)
        if form.is_valid():
            tramitacao = form.save(commit=False)
            tramitacao.usuario_id = request.user.id
            tramitacao.questionario_id = request.POST.get('id_questionario')
            tramitacao.save()

            # Envia notificação para o Usuário
            notify.send(request.user, recipient=tramitacao.questionario.usuario, verb=f'{tramitacao.questionario.entidade}', target=tramitacao.questionario, url='T', description=f'{tramitacao.get_motivo_display()} por {request.user.first_name}.')
            
        messages.success(request, "Questionário tramitado com sucesso!")
        return redirect(reverse('view_questionario', args=(q.id,)))


@login_required
def add_resposta(request, id):
    q = Questionario.objects.get(pk=id)
    questionario = Criterio.objects.filter(avaliacao=q.avaliacao).filter(matriz__in=['C', q.entidade.poder])\
    .select_related('avaliacao','dimensao')\
    .prefetch_related('criterioitem_set','itens_avaliacao')
    hoje = datetime.datetime.now()
    inicio = q.avaliacao.data_inicial
    fim = q.avaliacao.data_final

    if request.method == 'GET':
        if hoje.timestamp() >= inicio.timestamp() and hoje.timestamp() <= fim.timestamp():
            return render(request, 'add_resposta.html', {'questionario':questionario, 'q':q})
        else:
            messages.warning(request, "Desculpe, você está fora do prazo deste projeto.")
            return redirect(reverse('minhas_avaliacoes'))
    
    elif request.method == 'POST':

        for c in questionario:

            links = request.POST.get('link-{}'.format(c.id))

            for d in c.itens_avaliacao.all():
                form = request.POST.get('item_avaliacao-{}-{}'.format(c.id, d.id))
                imagens = request.FILES.getlist('imagem-{}-{}'.format(c.id, d.id))
                justificativa = request.POST.get('justificativa-{}-{}'.format(c.id, d.id))

                criterio_item = CriterioItem.objects.filter(criterio_id=c.id).filter(item_avaliacao_id=d.id)
                
                if form == 'on':
                    resposta = Resposta(questionario_id=q.id, criterio_item_id=criterio_item[0].id, resposta=True)
                    resposta.save()

                    if links:
                        #TODO: melhorar essa solução. Aqui estou salvando os links no primeiro item do critério apenas.
                        if d.id == 1:
                            link_evidencia = LinkEvidencia(resposta_id=resposta.id, link=links)
                            link_evidencia.save()

                else: 
                    resposta = Resposta(questionario_id=q.id, criterio_item_id=criterio_item[0].id)
                    resposta.save()

                if imagens:
                    if d.id == 1:
                        for i in imagens:
                            imagem_evidencia = ImagemEvidencia(resposta_id=resposta.id, imagem=i)
                            imagem_evidencia.save()

                if justificativa:
                    if d.id == 1:
                        justifica = JustificativaEvidencia(resposta_id=resposta.id, justificativa=justificativa)
                        justifica.save()

        acao = request.POST.get('acao') 
            
        if request.user.funcao == 'A':
            if acao == 'Salvar':
                q.status = 'E'
                q.save()
                messages.info(request, "Avaliação salva com sucesso! Para retornar, basta editá-la.")
                return redirect(reverse('minhas_avaliacoes'))
            else:
                q.status = 'F'
                q.save()
                messages.success(request, "Avaliação finalizada com sucesso!")                
                return redirect(reverse('minhas_avaliacoes'))
        if request.user.funcao == 'V' or request.user.funcao == 'C':
            if acao == 'Salvar':
                q.status = 'E'
                q.save()
                messages.info(request, "Avaliação salva com sucesso! Para retornar, basta editá-la.")
                return redirect(reverse('minhas_avaliacoes'))
            else:
                q.status = 'V'
                q.save()
                messages.success(request, "Avaliação finalizada com sucesso!")                
                return redirect(reverse('minhas_avaliacoes'))
                

@login_required
def change_resposta(request, id):
    q = Questionario.objects.get(pk=id)
    #questionario = q.avaliacao.criterio_set.filter(Q(matriz='C') | Q(matriz=q.entidade.poder))
    questionario = Criterio.objects.filter(avaliacao=q.avaliacao).filter(matriz__in=['C', q.entidade.poder])\
    .select_related('avaliacao','dimensao')\
    .prefetch_related('criterioitem_set',
                        'criterioitem_set__item_avaliacao',
                        Prefetch('criterioitem_set__resposta_set', queryset=Resposta.objects.filter(questionario=q)),
                        'criterioitem_set__resposta_set__linkevidencia_set',
                        'criterioitem_set__resposta_set__justificativaevidencia_set',
                        'criterioitem_set__resposta_set__imagemevidencia_set',
                        )
    hoje = datetime.datetime.now()
    inicio = q.avaliacao.data_inicial
    fim = q.avaliacao.data_final

    if request.method == 'GET':
        if hoje.timestamp() >= inicio.timestamp() and hoje.timestamp() <= fim.timestamp():
            q.status = 'E'
            q.save()
            return render(request, 'resposta_form.html', {'questionario':questionario, 'q':q})
        else:
            messages.warning(request, "Desculpe, você está fora do prazo deste projeto.")
            return redirect(reverse('view_questionario', args=(q.id,)))
    
    if request.method == 'POST':
        for i in q.resposta_set.all():
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
            
            resposta = get_object_or_404(Resposta, pk=id_resposta)

            if form == 'on':
                resposta.resposta = True
                resposta.save()

                if resposta.criterio_item.item_avaliacao.id == 1:
                    if not resposta.linkevidencia_set.all():
                        if form_link_novo:
                            link_evidencia = LinkEvidencia(resposta_id=resposta.id, link=form_link_novo)
                            link_evidencia.save()

                if id_link:
                    link = get_object_or_404(LinkEvidencia, pk=id_link)
                    link.link = form_link
                    link.save()
                            
            else:
                if resposta.criterio_item.item_avaliacao.id == 1:
                    if resposta.linkevidencia_set.all():
                        resposta.linkevidencia_set.all().delete()

                resposta.resposta = False
                resposta.save()

            if resposta.criterio_item.item_avaliacao.id == 1:
                if not resposta.imagemevidencia_set.all():
                    if imagens_novo:
                        for i in imagens_novo:
                            imagem_evidencia = ImagemEvidencia(resposta_id=resposta.id, imagem=i)
                            imagem_evidencia.save()

            if id_imagens and imagens:
                for i, l in zip(id_imagens,imagens):
                    imagem = get_object_or_404(ImagemEvidencia, pk=i)

                    if len(request.FILES) != 0:
                        if len(imagem.imagem) > 0:
                            imagem.delete()    
                        imagem.imagem = l
                    imagem.save()
            else:
                for i in imagens:
                    imagem_evidencia = ImagemEvidencia(resposta_id=resposta.id, imagem=i)
                    imagem_evidencia.save()


            if resposta.criterio_item.item_avaliacao.id == 1:
                if not resposta.justificativaevidencia_set.all():
                    if justificativa_novo:
                        justifica = JustificativaEvidencia(resposta_id=resposta.id, justificativa=justificativa_novo)
                        justifica.save()

            if id_justificativa:
                justifica = get_object_or_404(JustificativaEvidencia, pk=id_justificativa)
                justifica.justificativa = justificativa
                justifica.save()

        acao = request.POST.get('acao') 
            
        if request.user.funcao == 'A':
            if acao == 'Salvar':
                q.status = 'E'
                q.save()
                messages.info(request, "Avaliação salva com sucesso! Para retornar, basta editá-la.")
                return redirect(reverse('minhas_avaliacoes'))
            else:
                q.status = 'F'
                q.save()
                messages.success(request, "Avaliação alterada com sucesso!")                
                return redirect(reverse('minhas_avaliacoes'))
        if request.user.funcao == 'V' or request.user.funcao == 'C':
            if acao == 'Salvar':
                q.status = 'E'
                q.save()
                messages.info(request, "Avaliação salva com sucesso! Para retornar, basta editá-la.")
                return redirect(reverse('minhas_avaliacoes'))
            else:
                q.status = 'V'
                q.save()
                messages.success(request, "Avaliação alterada com sucesso!")                
                return redirect(reverse('minhas_avaliacoes'))


def exporta_csv(request, id):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="Questionário-{}.csv"'.format(id)
    response.write(u'\ufeff'.encode('utf8'))

    q = Questionario.objects.get(pk=id)

    questionario = Criterio.objects.filter(avaliacao=q.avaliacao).filter(matriz__in=['C', q.entidade.poder])\
    .select_related('avaliacao','dimensao')\
    .prefetch_related('criterioitem_set',
                        'criterioitem_set__item_avaliacao',
                        Prefetch('criterioitem_set__resposta_set', queryset=Resposta.objects.filter(questionario=q)),
                        'criterioitem_set__resposta_set__linkevidencia_set',
                        'criterioitem_set__resposta_set__justificativaevidencia_set',
                        'criterioitem_set__resposta_set__imagemevidencia_set',
                        )

    writer = csv.writer(response, delimiter=';')
    writer.writerow(['Matriz','Dimensão', 'Cod.', 'Critério', 'Classificação', 'Item de Avaliação', 'Resposta'])

    for i in questionario:
        for c in i.criterioitem_set.all():
            for r in c.resposta_set.all():
                if r.questionario.id == q.id:
                    writer.writerow([i.get_matriz_display(), i.dimensao, i.cod, i.criterio_texto, 
                                        i.get_exigibilidade_display(), r.criterio_item.item_avaliacao, 
                                    'Atende' if r.resposta == True else 'Não Atende'])

    return response


@login_required
def delete_imagem(request, id):
    imagem = get_object_or_404(ImagemEvidencia, pk=id)
    imagem.delete()
    return JsonResponse({'mensagem':'Imagem removida com sucesso!'})