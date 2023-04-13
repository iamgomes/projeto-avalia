from django.shortcuts import render
from django.http import HttpResponse
from .models import Municipio
from django.views.generic import View
from django.contrib.auth.decorators import login_required



class MunicipioBulk(View):
    def get(self, request):
        municipios = [['5103403', 'Cuiabá', 'MT'], 
                      ['5108402', 'Várzea Grande', 'MT'], 
                      ['5107909', 'Sinop', 'MT'], 
                      ['5107958', 'Tangará da Serra', 'MT']
                    ]
        lista_municipios = []

        for municipio in municipios:
            m = Municipio(ibge=municipio[0], nome=municipio[1], uf=municipio[2])
            lista_municipios.append(m)

        Municipio.objects.bulk_create(lista_municipios)

        return HttpResponse('Dados Inseridos com SUCESSO!')
