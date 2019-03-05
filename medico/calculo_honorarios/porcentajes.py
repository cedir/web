from decimal import Decimal


class Porcentajes:
    def __init__(self, estudio):
        if es_consulta(estudio):
            self._actuante = Decimal('100.00')
            self._solicitante = Decimal('0.00')
            self._cedir = Decimal('0.00')
            return

        if es_ecografia(estudio):
            self._actuante = Decimal('70.00')
            self._solicitante = Decimal('15.00')
            self._cedir = Decimal('15.00')
            return

        if es_laboratorio(estudio):
            self._actuante = Decimal('70.00')
            self._solicitante = Decimal('10.00')
            self._cedir = Decimal('20.00')
            return

        if es_ligadura_de_hemorroides(estudio):
            self._actuante = Decimal('50.00')
            self._solicitante = Decimal('0.00')
            self._cedir = Decimal('50.00')
            return

        if es_practica_especial(estudio):
            self._actuante = Decimal('75.00')
            self._solicitante = Decimal('25.00')
            self._cedir = Decimal('0.00')
            return

        if brunetti_es_actuante(estudio):
            if tiene_acuerdo_al_10(estudio):
                self._actuante = Decimal('80.00') * Decimal('0.9')
                self._solicitante = Decimal('80.00')  * Decimal('0.1')
                self._cedir = Decimal('20.00')
                return

            if tiene_acuerdo_al_40(estudio):
                self._actuante = Decimal('80.00') * Decimal('0.8')
                self._solicitante = Decimal('80.00') * Decimal('0.2')
                self._cedir = Decimal('20.00')
                return

            if tiene_acuerdo_al_50(estudio):
                self._actuante = Decimal('80.00')  * Decimal('0.5')
                self._solicitante = Decimal('80.00')  * Decimal('0.5')
                self._cedir = Decimal('20.00')
                return

            if tiene_acuerdo_al_80(estudio):
                self._actuante = Decimal('80.00')  * Decimal('0.2')
                self._solicitante = Decimal('80.00')  * Decimal('0.8')
                self._cedir = Decimal('20.00')
                return

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
    return estudio.practica.id == 20

def es_ecografia(estudio):
    return estudio.practica.id in \
        [55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 82, 83, 84, 89,
         90, 99, 100, 101, 103, 108, 109, 114, 115, 117, 123, 126, 127, 132, 134, 135,
         136, 137, 141, 142, 144, 145, 154, 160, 164]

def es_laboratorio(estudio):
    return estudio.practica.id == 91

def es_ligadura_de_hemorroides(estudio):
    return estudio.practica.id == 3

def es_practica_especial(estudio):
    return estudio.practica.id in [33, 38, 37, 88, 102, 110, 111, 112, 113, 114, 133, 119]

def brunetti_es_actuante(estudio):
    return estudio.medico.id == 2

def tiene_acuerdo_al_10(estudio):
    return estudio.medico_solicitante.id in [74, 259]

def tiene_acuerdo_al_40(estudio):
    return estudio.medico_solicitante.id in [78, 89, 529, 585]

def tiene_acuerdo_al_50(estudio):
    return estudio.medico_solicitante.id in [578]

def tiene_acuerdo_al_80(estudio):
    return estudio.medico_solicitante.id in [4, 528]
