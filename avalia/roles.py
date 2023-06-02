from rolepermissions.roles import AbstractUserRole

class Avaliadores(AbstractUserRole):
    available_permissions = {'avaliar': True}

class Validadores(AbstractUserRole):
    available_permissions = {'avaliar': True, 'validar': True, 'visao_geral': True}

class Coordenadores(AbstractUserRole):
    available_permissions = {'avaliar': True, 'validar': True, 'atribuir_validador': True, 'visao_geral': True}