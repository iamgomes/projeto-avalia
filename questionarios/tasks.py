from celery import shared_task
from . models import Avaliacao, Questionario, Resposta, LinkEvidencia, ImagemEvidencia, \
    CriterioItem, Tramitacao, JustificativaEvidencia, Criterio, Resposta
import datetime
from .minhas_funcoes import altera_imagem, desserializar_imagem
from django.db.models import Prefetch
from django.shortcuts import redirect, get_object_or_404



@shared_task
def add_resposta_task(form_data, form_files, id):

    q = Questionario.objects.get(pk=id)
    questionario = Criterio.objects.filter(avaliacao=q.avaliacao).filter(matriz__in=['C', q.entidade.poder])\
    .select_related('avaliacao','dimensao')\
    .prefetch_related('criterioitem_set','itens_avaliacao')

    for c in questionario:

        links = form_data['link-{}'.format(c.id)]

        try:
            imagens = form_files['imagem-{}'.format(c.id)]
        except:
            imagens = None
            
        justificativa = form_data['justificativa-{}'.format(c.id)]

        for d in c.itens_avaliacao.all():
            try:
                form = form_data['item_avaliacao-{}-{}'.format(c.id, d.id)]
            except:
                form = None

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
                    imagem_evidencia = ImagemEvidencia(resposta_id=resposta.id, imagem=altera_imagem(desserializar_imagem(imagens), resposta))
                    imagem_evidencia.save()

            if justificativa:
                if d.id == 1:
                    justifica = JustificativaEvidencia(resposta_id=resposta.id, justificativa=justificativa)
                    justifica.save()

    try:
        acao = form_data['acao']
    except:
        acao = None
        
    if q.usuario.funcao == 'A':
        if acao == 'Salvar':
            q.status = 'E'
            q.save()
        else:
            q.status = 'F'
            q.save()
    if q.usuario.funcao == 'V' or q.usuario.funcao == 'C':
        if acao == 'Salvar':
            q.status = 'E'
            q.save()
        else:
            q.status = 'V'
            q.save()

    return {'response':'Succes', 'questionario':q.id}

@shared_task
def change_resposta_task(form_data, form_files, id):

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
    
    for i in q.resposta_set.all():
        id_resposta = form_data['id_resposta-{}'.format(i.id)]

        try:         
            form = form_data['resposta-{}'.format(i.id)]
        except:
            form = None

        try:
            id_link = form_data['id_link-{}'.format(i.id)]
            form_link = form_data['link-{}'.format(i.id)]
        except:
            id_link = None
            form_link = None

        try:    
            form_link_novo = form_data['link_novo-{}'.format(i.id)]
        except:
            form_link_novo = None

        try:
            id_justificativa = form_data['id_justificativa-{}'.format(i.id)]
            justificativa = form_data['justificativa-{}'.format(i.id)]
        except:
            id_justificativa = None
            justificativa = None

        try:
            justificativa_novo = form_data['justificativa_novo-{}'.format(i.id)]
        except:
            justificativa_novo = None

        try:
            id_imagens = form_data['id_imagem-{}'.format(i.id)]         
            imagens = form_files['imagem-{}'.format(i.id)]
        except:
            id_imagens = None        
            imagens = None

        try:
            imagens_novo = form_files['imagem_novo-{}'.format(i.id)]
        except:
            imagens_novo = None
        
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
                    imagem_evidencia = ImagemEvidencia(resposta_id=resposta.id, imagem=altera_imagem(desserializar_imagem(imagens_novo), resposta))
                    imagem_evidencia.save()

        if id_imagens != None and imagens:
            imagem = get_object_or_404(ImagemEvidencia, pk=id_imagens)

            if len(form_files) != 0:
                if len(imagem.imagem) > 0:
                    imagem.delete()    
                imagem.imagem = altera_imagem(desserializar_imagem(imagens), resposta)
            imagem.save()
        elif imagens != None:
            imagem_evidencia = ImagemEvidencia(resposta_id=resposta.id, imagem=altera_imagem(desserializar_imagem(imagens), resposta))
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

    try:
        acao = form_data['acao']
    except:
        acao = None
        
    if q.usuario.funcao == 'A':
        if acao == 'Salvar':
            q.status = 'E'
            q.save()
        else:
            q.status = 'F'
            q.save()
    if q.usuario.funcao == 'V' or q.usuario.funcao == 'C':
        if acao == 'Salvar':
            q.status = 'E'
            q.save()
        else:
            q.status = 'V'
            q.save()

    return {'response':'Succes', 'questionario':q.id}