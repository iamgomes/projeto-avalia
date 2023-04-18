from django.shortcuts import render
import requests
from django.http import HttpResponse
from .models import Municipio
from django.views.generic import View


class MunicipioBulk(View):
    def get(self, request):
        municipios = requests.get('https://servicodados.ibge.gov.br/api/v1/localidades/municipios')
        lista_municipios = []

        for municipio in municipios.json():
            m = Municipio(ibge=municipio['id'], nome=municipio['nome'], uf=municipio['microrregiao']['mesorregiao']['UF']['sigla'])
            lista_municipios.append(m)

        Municipio.objects.bulk_create(lista_municipios)

        return HttpResponse('Dados Inseridos com SUCESSO!')
