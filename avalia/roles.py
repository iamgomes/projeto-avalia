from rolepermissions.roles import AbstractUserRole

class Controladores(AbstractUserRole):
    available_permissions = {'avaliar': True}

class Coordenadores(AbstractUserRole):
    available_permissions = {'avaliar': True, 'validar': True, 'atribuir_validador': True, 'visao_geral': True}

class Auditores(AbstractUserRole):
    available_permissions = {'avaliar': True, 'validar': True, 'visao_geral': True}