from django.shortcuts import render
from django.http import HttpResponse
from . models import UsuarioAvaliacao, Resposta, Avaliacao, Criterio, CriterioDimensao, UsuarioAvaliacaoValidacao, RespostaValidacao
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from entidades.models import Entidade
from django.contrib.auth.decorators import login_required
from django.contrib import messages


@login_required
def avaliacao(request):
    formularios = UsuarioAvaliacao.objects.all()
    avaliacoes_recebidas = UsuarioAvaliacao.objects.all().count()
    
    return render(request, 'avaliacoes.html', {'formularios':formularios, 'avaliacoes_recebidas':avaliacoes_recebidas})


@login_required
def add_usuario_avaliacao(request, id):
    if request.method == 'GET':
        entidades = Entidade.objects.filter(municipio=request.user.municipio)
        return render(request, 'add_usuario_avaliacao.html', {'id':id, 'entidades':entidades})
        
    elif request.method == 'POST':
        usuario = request.user
        avaliacao = request.POST.get('avaliacao')
        entidade = request.POST.get('entidade')
        site = request.POST.get('site')

        identificacao = UsuarioAvaliacao(avaliacao_id=avaliacao, usuario=usuario, entidade_id=entidade)
        
        if site == 'N':
            identificacao.status = 'NS'
            identificacao.save()
            messages.success(request, "Sua avaliação foi finalizada.")
            return redirect(reverse('avaliacao'))
        
        else:
            identificacao.save()
            id_identificaca = identificacao.id

    messages.success(request, "Muito bom! Você iniciou uma avaliação.")

    # redireciona para página de resposta passando como parâmetro o id criado
    return redirect(reverse('add_resposta', args=(id_identificaca,)))


@login_required
def add_resposta(request, id):
    id_avaliacao = UsuarioAvaliacao.objects.get(pk=id)
    criterios = Criterio.objects.filter(avaliacao_id=id_avaliacao.avaliacao.id)

    if request.method == 'GET':
        # retorna as choices (Atende, não atende, parcialmente) do campo RESPOSTA da tabela RESPOSTA
        choices = Resposta.RESPOSTA_CHOICES
        return render(request, 'add_resposta.html', {'id':id, 'criterios':criterios, 'choices':choices, 'id_avaliacao':id_avaliacao})
    
    elif request.method == 'POST':
        usuarioavaliacao = request.POST.get('usuarioavaliacao')
        
        for i in criterios:

            d = Criterio.objects.get(pk=i.id)

            for j in d.dimensoes.all():
                resposta = request.POST.get('resposta-{}-{}'.format(i.id, j.id))

                criterio_dimensao = CriterioDimensao.objects.filter(criterio=i).filter(dimensao=j)

                resposta = Resposta(usuarioavaliacao_id=usuarioavaliacao, criterio_dimensao_id=criterio_dimensao[0].id, resposta=resposta)
                resposta.save()
            
        id_avaliacao.status = 'F'
        id_avaliacao.save()
        
        messages.success(request, "Resposta cadastrada com sucesso!")

        return redirect(reverse('avaliacao'))
    
    
@login_required
def change_resposta(request, id):
    avaliacao = get_object_or_404(UsuarioAvaliacao, pk=id)
    respostas = Resposta.objects.filter(usuarioavaliacao_id=id)
    criterios = Criterio.objects.filter(avaliacao_id=avaliacao.avaliacao.id)
    choices = Resposta.RESPOSTA_CHOICES

    if request.method == 'GET':
        
        avaliacao.status = 'E'
        avaliacao.save()

        return render(request, 'resposta_form.html', {'respostas':respostas, 'avaliacao':avaliacao, 'choices':choices, 'criterios':criterios})
    
    if request.method == 'POST':
        for i in respostas:
            id_resposta = request.POST.get('id_resposta-{}'.format(i.id))
            resposta = get_object_or_404(Resposta, pk=id_resposta)
            choice = request.POST.get('resposta-{}'.format(i.id))
            
            resposta.resposta = choice
            resposta.save()

        avaliacao.status = 'F'
        avaliacao.save()

        messages.success(request, "Resposta de avaliação alterada com sucesso!")

        return redirect(reverse('avaliacao'))


@login_required
def delete_usuario_avaliacao(request, id):
    usuarioavaliacao = get_object_or_404(UsuarioAvaliacao, pk=id)
    usuarioavaliacao.delete()
    
    return redirect(reverse('avaliacao'))


@login_required
def envia_para_validacao(request, id):
    avaliacao = get_object_or_404(UsuarioAvaliacao, pk=id)

    avaliacao.status = 'A'
    avaliacao.save()

    messages.success(request, "Parabéns! Sua avaliação foi enviada para validação.")

    return redirect(reverse('avaliacao'))


@login_required
def add_usuario_validacao(request, id):
    usuario = request.user
    usuario_avaliacao = get_object_or_404(UsuarioAvaliacao, pk=id)

    validacao = UsuarioAvaliacaoValidacao(usuario=usuario, usuario_avaliacao_id=id)
    validacao.save()
    id_validacao = validacao.id

    usuario_avaliacao.status = 'EV'
    usuario_avaliacao.save()

    messages.success(request, "Ótimo! Vamos começar a validar.")

    return redirect(reverse('add_resposta_validacao', args=(id,id_validacao)))


@login_required
def add_resposta_validacao(request, id, id_validacao):
    avaliacao = get_object_or_404(UsuarioAvaliacao, pk=id)
    validacao = get_object_or_404(UsuarioAvaliacaoValidacao, pk=id_validacao)
    respostas = Resposta.objects.filter(usuarioavaliacao_id=id)
    criterios = Criterio.objects.filter(avaliacao_id=avaliacao.avaliacao.id)

    if request.method == 'GET':
        # retorna as choices (Atende, não atende, parcialmente) do campo RESPOSTA da tabela RESPOSTA
        choices = Resposta.RESPOSTA_CHOICES

        return render(request, 'add_resposta_validacao.html', {'respostas':respostas, 'validacao':validacao, 'choices':choices, 'criterios':criterios})
    
    if request.method == 'POST':
        usuario_avaliacao_validacao = request.POST.get('validacao')

        for i in respostas:
            id_resposta = request.POST.get('id_resposta-{}'.format(i.id))
            resposta_validacao = request.POST.get('resposta-{}'.format(i.id))

            avaliacaoresposta = RespostaValidacao(usuario_avaliacao_validacao_id=usuario_avaliacao_validacao,\
                                                  resposta_id=id_resposta,resposta_validacao=resposta_validacao)
            
            avaliacaoresposta.save()

        avaliacao.status = 'V'
        avaliacao.save()

        messages.success(request, "Validação feita com sucesso!")

        return redirect(reverse('avaliacao'))


@login_required
def change_resposta_validacao(request, id):
    validacao = get_object_or_404(UsuarioAvaliacaoValidacao, pk=id)
    choices = Resposta.RESPOSTA_CHOICES

    if request.method == 'GET':

        return render(request, 'resposta_validacao_form.html', {'validacao':validacao, 'choices':choices})
    
    if request.method == 'POST':
        for i in validacao.respostavalidacao_set.all():
            id_resposta = request.POST.get('id_resposta-{}'.format(i.id))
            resposta = get_object_or_404(RespostaValidacao, pk=id_resposta)
            choice = request.POST.get('resposta-{}'.format(i.id))
            
            resposta.resposta_validacao = choice
            resposta.save()

        messages.success(request, "Resposta de validação alterada com sucesso!")

        return redirect(reverse('avaliacao'))
    

def minhas_avaliacoes(request):
    avaliacoes = UsuarioAvaliacao.objects.filter(usuario=request.user)
    validacoes = UsuarioAvaliacaoValidacao.objects.filter(usuario=request.user)
    
    return render(request, 'minhas_avaliacoes.html', {'avaliacoes':avaliacoes, 'validacoes':validacoes})