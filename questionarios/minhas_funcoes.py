from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys
import boto3
from questionarios.models import ImagemEvidencia


def alterar_nome_imagem_banco(id_imagem):
    # Buscar imagem no banco de dados pelo ID
    imagem = ImagemEvidencia.objects.get(id=id_imagem)
    
    # Obter o nome atual da imagem
    nome_imagem = imagem.imagem.name
    
    # Obter o nome do bucket e a chave da imagem no S3
    bucket = 'avalia-desenvolvimento'
    chave = f'static/{nome_imagem}'

    nome_arquivo = imagem.imagem.name.split('/')[1]
    
    # Definir o novo nome da imagem
    novo_nome_imagem = f'imagem_evidencia/{nome_arquivo}'
    
    # Criar uma nova conexão com o cliente do S3
    s3_client = boto3.client('s3')
    
    # Copiar a imagem com o novo nome no S3
    s3_client.copy_object(
        Bucket=bucket,
        CopySource={'Bucket': bucket, 'Key': chave},
        Key=novo_nome_imagem
    )
    
    # Excluir a imagem antiga no S3
    s3_client.delete_object(Bucket=bucket, Key=chave)
    
    # Atualizar o nome da imagem no banco de dados
    imagem.imagem.name = novo_nome_imagem
    imagem.save()



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