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
from .minhas_funcoes import altera_imagem
from .tasks import add_resposta_task, change_resposta_task, add_img_task
import pickle
import time


@login_required
def add_resposta(request, id):
    start_time = time.time()

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
            imagem = request.FILES.get('imagem-{}'.format(c.id))
            justificativa = request.POST.get('justificativa-{}'.format(c.id))           
            
            for d in c.itens_avaliacao.all():
                form = request.POST.get('item_avaliacao-{}-{}'.format(c.id, d.id))

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

                if imagem:
                    if d.id == 1:
                        dados_imagem = {
                            'nome': imagem.name,
                            'conteudo': imagem.read(),
                            'tipo_conteudo': imagem.content_type,
                            'tamanho': imagem.size,
                            'charset': imagem.charset,
                        }
                        pickle.dumps(dados_imagem)
                            
                        add_img_task.delay(pickle.dumps(dados_imagem), resposta.id)

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
                end_time = time.time()
                duration = end_time - start_time
                print(f'Tempo de execução: {round(duration, 2)} segundos')
                return redirect(reverse('minhas_avaliacoes'))
            else:
                q.status = 'F'
                q.save()
                messages.success(request, "Avaliação finalizada com sucesso!")
                end_time = time.time()
                duration = end_time - start_time
                print(f'Tempo de execução: {round(duration, 2)} segundos')               
                return redirect(reverse('minhas_avaliacoes'))
        if request.user.funcao == 'V' or request.user.funcao == 'C':
            if acao == 'Salvar':
                q.status = 'E'
                q.save()
                messages.info(request, "Avaliação salva com sucesso! Para retornar, basta editá-la.")
                end_time = time.time()
                duration = end_time - start_time
                print(f'Tempo de execução: {round(duration, 2)} segundos')
                return redirect(reverse('minhas_avaliacoes'))
            else:
                q.status = 'V'
                q.save()
                messages.success(request, "Avaliação finalizada com sucesso!")  
                end_time = time.time()
                duration = end_time - start_time
                print(f'Tempo de execução: {round(duration, 2)} segundos')              
                return redirect(reverse('minhas_avaliacoes'))
            

@login_required
def add_resposta2(request, id):
    start_time = time.time()

    q = Questionario.objects.get(pk=id)
    questionario = Criterio.objects.filter(avaliacao=q.avaliacao).filter(matriz__in=['C', q.entidade.poder])\
    .select_related('avaliacao','dimensao')\
    .prefetch_related('criterioitem_set','itens_avaliacao')

    if request.method == 'GET':
        return render(request, 'add_resposta.html', {'questionario':questionario, 'q':q})
    
    elif request.method == 'POST':
        data = request.POST
        files = request.FILES

        #serializando as imagens
        dicionario_imagens = {}
        for chave, valor in files.lists():
            dados_imagem = {
                'nome': valor[0].name,
                'conteudo': valor[0].read(),
                'tipo_conteudo': valor[0].content_type,
                'tamanho': valor[0].size,
                'charset': valor[0].charset,
            }

            dicionario_imagens[chave] = pickle.dumps(dados_imagem)

        result = add_resposta_task.delay(data, dicionario_imagens, id)

        end_time = time.time()
        duration = end_time - start_time
        print(f'Tempo de execução: {round(duration, 2)} segundos')

        request.session["task_id"] = result.task_id
        request.session["id_questionario"] = q.id

        messages.info(request, "Estamos salvando sua avaliação...")
        return redirect(reverse('minhas_avaliacoes'))
    

@login_required
def change_resposta(request, id):
    start_time = time.time()

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

    if request.method == 'GET':
        q.status = 'E'
        q.save()
        return render(request, 'resposta_form.html', {'questionario':questionario, 'q':q})

    
    if request.method == 'POST':
        data = request.POST
        files = request.FILES

        #serializando as imagens
        dicionario_imagens = {}
        for chave, valor in files.lists():
            dados_imagem = {
                'nome': valor[0].name,
                'conteudo': valor[0].read(),
                'tipo_conteudo': valor[0].content_type,
                'tamanho': valor[0].size,
                'charset': valor[0].charset,
            }

            dicionario_imagens[chave] = pickle.dumps(dados_imagem)

        result = change_resposta_task.delay(data, dicionario_imagens, id)

        end_time = time.time()
        duration = end_time - start_time
        print(f'Tempo de execução: {round(duration, 2)} segundos')

        request.session["task_id"] = result.task_id
        request.session["id_questionario"] = q.id

        messages.info(request, "Estamos salvando sua avaliação...")
        return redirect(reverse('minhas_avaliacoes'))
        
    

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