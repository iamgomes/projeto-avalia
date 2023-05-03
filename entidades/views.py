from django.shortcuts import render
import requests
from django.http import HttpResponse
from .models import Municipio, Entidade
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse


class MunicipioBulk(LoginRequiredMixin, View):
    def get(self, request):
        
        municipios_api = requests.get('https://servicodados.ibge.gov.br/api/v1/localidades/municipios')
        capitais = [1200401,2704302,1302603,1600303,2927408,2304400,5300108,3205309,5208707,
                    2111300,3106200,5103403,1501402,2507507,2611606,2211001,4106902,3304557,
                    2408102,1100205,1400100,4314902,4205407,2800308,3550308,1721000]
        
        #Inserindo os municípios do Brasil
        lista_municipios = []

        for municipio in municipios_api.json():
            if municipio['id'] in capitais:
                m = Municipio(ibge=municipio['id'], nome=municipio['nome'], uf=municipio['microrregiao']['mesorregiao']['UF']['sigla'], capital=True)
                lista_municipios.append(m)
            else:
                m = Municipio(ibge=municipio['id'], nome=municipio['nome'], uf=municipio['microrregiao']['mesorregiao']['UF']['sigla'])
                lista_municipios.append(m)
        Municipio.objects.bulk_create(lista_municipios)
        messages.success(request, "Municípios inseridos com sucesso!")

        #Inserindo prefeituras
        municipios = Municipio.objects.all()
        lista_prefeituras = []

        for municipio in municipios:
            if municipio.ibge != '5300108':
                nome = 'Prefeitura Municipal de {}'.format(municipio.nome)
                entidade = Entidade(nome=nome, municipio=municipio, poder='E', esfera='M')
                lista_prefeituras.append(entidade)
        Entidade.objects.bulk_create(lista_prefeituras)
        messages.success(request, "Prefeituras inseridas com sucesso!")

        #Inserindo câmaras
        lista_camaras = []

        for municipio in municipios:
            if municipio.ibge != '5300108':
                nome = 'Câmara Municipal de {}'.format(municipio.nome)
                entidade = Entidade(nome=nome, municipio=municipio, poder='L', esfera='M')
                lista_camaras.append(entidade)
        Entidade.objects.bulk_create(lista_camaras)
        messages.success(request, "Câmaras inseridas com sucesso!")

        #Inserindo governo do estado
        lista_governo = []

        for municipio in municipios:
            if municipio.capital == True and municipio.ibge != '5300108':
                nome = 'Governo do Estado de {}'.format(municipio.get_uf_display())
                entidade = Entidade(nome=nome, municipio=municipio, poder='E', esfera='E')
                lista_governo.append(entidade)
        Entidade.objects.bulk_create(lista_governo)
        messages.success(request, "Governos inseridos com sucesso!")

        #Inserindo tribunais de contas do estado
        lista_tces = []

        for municipio in municipios:
            if municipio.capital == True and municipio.ibge != '5300108':
                nome = 'Tribunal de Contas do Estado de {}'.format(municipio.get_uf_display())
                entidade = Entidade(nome=nome, municipio=municipio, poder='T', esfera='E')
                lista_tces.append(entidade)
        Entidade.objects.bulk_create(lista_tces)
        messages.success(request, "TCEs inseridos com sucesso!")

        #Inserindo tribunais de justiça do estado
        lista_tjs = []

        for municipio in municipios:
            if municipio.capital == True and municipio.ibge != '5300108':
                nome = 'Tribunal de Justiça do Estado de {}'.format(municipio.get_uf_display())
                entidade = Entidade(nome=nome, municipio=municipio, poder='J', esfera='E')
                lista_tjs.append(entidade)
        Entidade.objects.bulk_create(lista_tjs)
        messages.success(request, "TJs inseridos com sucesso!")

        #Inserindo assembleias
        lista_assembleias = []

        for municipio in municipios:
            if municipio.capital == True and municipio.ibge != '5300108':
                nome = 'Assembleia Legislativa do Estado de {}'.format(municipio.get_uf_display())
                entidade = Entidade(nome=nome, municipio=municipio, poder='L', esfera='E')
                lista_assembleias.append(entidade)
        Entidade.objects.bulk_create(lista_assembleias)
        messages.success(request, "Assembleias Legislativas inseridas com sucesso!")

        #Inserindo defensorias
        lista_defensorias = []

        for municipio in municipios:
            if municipio.capital == True and municipio.ibge != '5300108':
                nome = 'Defensoria Pública do Estado de {}'.format(municipio.get_uf_display())
                entidade = Entidade(nome=nome, municipio=municipio, poder='D', esfera='E')
                lista_defensorias.append(entidade)
        Entidade.objects.bulk_create(lista_defensorias)
        messages.success(request, "Defensorias inseridas com sucesso!")

        #Inserindo ministerios publicos
        lista_mps = []

        for municipio in municipios:
            if municipio.capital == True and municipio.ibge != '5300108':
                nome = 'Ministério Público do Estado de {}'.format(municipio.get_uf_display())
                entidade = Entidade(nome=nome, municipio=municipio, poder='M', esfera='E')
                lista_mps.append(entidade)
        Entidade.objects.bulk_create(lista_mps)
        messages.success(request, "Ministérios Públicos inseridas com sucesso!")

        #inserindo distrital e federal
        lista_bsb = []

        for municipio in municipios:
            if municipio.capital == True and municipio.ibge == '5300108':
                nome = 'Governo Distrital do {}'.format(municipio.get_uf_display())
                entidade = Entidade(nome=nome, municipio=municipio, poder='E', esfera='D')
                lista_bsb.append(entidade)

                defensoria = 'Defensoria Pública Distrital do {}'.format(municipio.get_uf_display())
                entidade = Entidade(nome=defensoria, municipio=municipio, poder='D', esfera='D')
                lista_bsb.append(entidade)

                tc = 'Tribunal de Contas do {}'.format(municipio.get_uf_display())
                entidade = Entidade(nome=tc, municipio=municipio, poder='T', esfera='D')
                lista_bsb.append(entidade)

                tj = 'Tribunal de Justiça Distrital do {}'.format(municipio.get_uf_display())
                entidade = Entidade(nome=tj, municipio=municipio, poder='J', esfera='D')
                lista_bsb.append(entidade)

                mp = 'Ministério Público Distrital do {}'.format(municipio.get_uf_display())
                entidade = Entidade(nome=mp, municipio=municipio, poder='M', esfera='D')
                lista_bsb.append(entidade)

                camara = 'Câmara Legislativa do {}'.format(municipio.get_uf_display())
                entidade = Entidade(nome=camara, municipio=municipio, poder='L', esfera='D')
                lista_bsb.append(entidade)

                presidencia = 'Presidência da República'
                entidade = Entidade(nome=presidencia, municipio=municipio, poder='E', esfera='F')
                lista_bsb.append(entidade)

                defensoria = 'Defensoria Pública da União'
                entidade = Entidade(nome=defensoria, municipio=municipio, poder='D', esfera='F')
                lista_bsb.append(entidade)

                tc = 'Tribunal de Contas da União'
                entidade = Entidade(nome=tc, municipio=municipio, poder='T', esfera='F')
                lista_bsb.append(entidade)

                stj = 'Supremo Tribunal Federal'
                entidade = Entidade(nome=stj, municipio=municipio, poder='J', esfera='F')
                lista_bsb.append(entidade)

                mp = 'Ministério Público Federal'
                entidade = Entidade(nome=mp, municipio=municipio, poder='M', esfera='F')
                lista_bsb.append(entidade)

                camara = 'Câmara dos Deputados'
                entidade = Entidade(nome=camara, municipio=municipio, poder='L', esfera='F')
                lista_bsb.append(entidade)

                senado = 'Senado Federal'
                entidade = Entidade(nome=senado, municipio=municipio, poder='L', esfera='F')
                lista_bsb.append(entidade)
        Entidade.objects.bulk_create(lista_bsb)
        messages.success(request, "Governo Distrital e Federal inseridos com sucesso!")

        return redirect(reverse('home'))
