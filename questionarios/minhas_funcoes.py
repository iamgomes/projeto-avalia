from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys


def altera_imagem(imagem, resposta):
    nome_arquivo = f'{resposta.questionario.usuario}-{resposta.id}-{resposta.questionario.id}-{imagem}'
    img = Image.open(imagem)
    img = img.convert('RGB')
    output = BytesIO()
    img.save(output, format='JPEG', quality=80)
    output.seek(0)
    img_final = InMemoryUploadedFile(output,'ImageField',nome_arquivo,'image/jpeg',sys.getsizeof(output),None)
    return img_final


def altera_imagem_validacao(imagem, resposta_validacao):
    nome_arquivo = f'{resposta_validacao.validacao.usuario}-{resposta_validacao.id}-{resposta_validacao.validacao.id}-{imagem}'
    img = Image.open(imagem)
    img = img.convert('RGB')
    output = BytesIO()
    img.save(output, format='JPEG', quality=80)
    output.seek(0)
    img_final = InMemoryUploadedFile(output,'ImageField',nome_arquivo,'image/jpeg',sys.getsizeof(output),None)
    return img_final