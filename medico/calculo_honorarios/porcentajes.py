from decimal import Decimal

CONSULTA = 100

ACT_ECOGRAFIA = 70
SOL_ECOGRAFIA = 15

ACT_LABORATORIO = 70
SOL_LABORATORIO = 10

ACT_LIGADURA_HEMORROIDES = 50
SOL_LIGADURA_HEMORROIDES = 0

ACT_PRACTICA_ESPECIAL = 75
SOL_PRACTICA_ESPECIAL = 75

ACTUANTE = 80
SOLICITANTE = 0

COMB_MED_ACT_BRUNETTI = 2


class Porcentajes:
    '''
    #TODO: marco para implementar mas adelante las reglas posta.
    '''
    def __init__(self, estudio):
        pass

    @property
    def actuante(self):
        return Decimal('70.00')

    @property
    def solicitante(self):
        return Decimal('20.00')

    @property
    def cedir(self):
        return Decimal('10.00')


# Estos se usan tambien en descuentos. Convendra hacerlas @property en los models de estudio?
def es_ecografia(estudio):
    pass


def es_laboratorio(estudio):
    pass


def es_ligadura_de_hemorroides(estudio):
    pass


def es_practica_especial(estudio):
    pass


def brunetti_es_actuante(estudio):
    pass
