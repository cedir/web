from decimal import Decimal


class Porcentajes:
    '''
    #TODO: marco para implementar mas adelante las reglas posta.
    '''
    def __init__(self, estudio):
        if es_consulta(estudio):
            self._actuante = Decimal('100.00')
            self._solicitante = Decimal('0.00')
            self._cedir = Decimal('0.00')
        elif es_ecografia(estudio):
            self._actuante = Decimal('70.00')
            self._solicitante = Decimal('15.00')
            self._cedir = Decimal('15.00')
        elif es_laboratorio(estudio):
            self._actuante = Decimal('70.00')
            self._solicitante = Decimal('10.00')
            self._cedir = Decimal('20.00')
        elif es_ligadura_hemorroides(estudio):
            self._actuante = Decimal('50.00')
            self._solicitante = Decimal('0.00')
            self._cedir = Decimal('50.00')
        elif es_practica_especial(estudio):
            self._actuante = Decimal('75.00')
            self._solicitante = Decimal('25.00')
            self._cedir = Decimal('0.00')
        elif brunetti_es_actuante(estudio):
            pass #TODO
        else:
            self._actuante = Decimal('80.00')
            self._solicitante = Decimal('0.00')
            self._cedir = Decimal('20.00')

    @property
    def actuante(self):
        return self._actuante

    @property
    def solicitante(self):
        return self._solicitante

    @property
    def cedir(self):
        return self._cedir


# Estos se usan tambien en descuentos. Convendra hacerlas @property en los models de estudio?
def es_consulta(estudio):
    pass


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
