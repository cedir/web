from .constantes import *


class Porcentajes(object):
    def __init__(self, estudio):
        if es_consulta(estudio):
            self._actuante = PORCENTAJE_CONSULTA_ACTUANTE
            self._solicitante = PORCENTAJE_CONSULTA_SOLICITANTE
            self._cedir = PORCENTAJE_CONSULTA_CEDIR
            return

        if es_ecografia(estudio):
            self._actuante = PORCENTAJE_ECOGRAFIA_ACTUANTE
            self._solicitante = PORCENTAJE_ECOGRAFIA_SOLICITANTE
            self._cedir = PORCENTAJE_ECOGRAFIA_CEDIR
            return

        if es_laboratorio(estudio):
            self._actuante = PORCENTAJE_LABORATORIO_ACTUANTE
            self._solicitante = PORCENTAJE_LABORATORIO_SOLICITANTE
            self._cedir = PORCENTAJE_LABORATORIO_CEDIR
            return

        if es_ligadura_de_hemorroides(estudio):
            self._actuante = PORCENTAJE_LIGADURA_ACTUANTE
            self._solicitante = PORCENTAJE_LIGADURA_SOLICITANTE
            self._cedir = PORCENTAJE_LIGADURA_CEDIR
            return

        if es_practica_especial(estudio):
            self._actuante = PORCENTAJE_ESPECIAL_ACTUANTE
            self._solicitante = PORCENTAJE_ESPECIAL_SOLICITANTE
            self._cedir = PORCENTAJE_ESPECIAL_CEDIR
            return

        if brunetti_es_actuante(estudio):
            if tiene_acuerdo_al_10(estudio):
                self._actuante = PORCENTAJE_ACUERDO_10_ACTUANTE
                self._solicitante = PORCENTAJE_ACUERDO_10_SOLICITANTE
                self._cedir = PORCENTAJE_ACUERDO_10_CEDIR
                return

            if tiene_acuerdo_al_40(estudio):
                self._actuante = PORCENTAJE_ACUERDO_40_ACTUANTE
                self._solicitante = PORCENTAJE_ACUERDO_40_SOLICITANTE
                self._cedir = PORCENTAJE_ACUERDO_40_CEDIR
                return

            if tiene_acuerdo_al_50(estudio):
                self._actuante = PORCENTAJE_ACUERDO_50_ACTUANTE
                self._solicitante = PORCENTAJE_ACUERDO_50_SOLICITANTE
                self._cedir = PORCENTAJE_ACUERDO_50_CEDIR
                return

            if tiene_acuerdo_al_80(estudio):
                self._actuante = PORCENTAJE_ACUERDO_80_ACTUANTE
                self._solicitante = PORCENTAJE_ACUERDO_80_SOLICITANTE
                self._cedir = PORCENTAJE_ACUERDO_80_CEDIR
                return

        self._actuante = PORCENTAJE_POR_DEFECTO_ACTUANTE
        self._solicitante = PORCENTAJE_POR_DEFECTO_SOLICITANTE
        self._cedir = PORCENTAJE_POR_DEFECTO_CEDIR
        return

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
    return estudio.practica.id in ID_CONSULTA

def es_ecografia(estudio):
    return estudio.practica.id in ID_ECOGRAFIA

def es_laboratorio(estudio):
    return estudio.practica.id in ID_LABORATORIO

def es_ligadura_de_hemorroides(estudio):
    return estudio.practica.id in ID_LIGADURA

def es_practica_especial(estudio):
    return estudio.practica.id in ID_ESPECIAL

def brunetti_es_actuante(estudio):
    return estudio.medico.id in ID_BRUNETTI

def tiene_acuerdo_al_10(estudio):
    return estudio.medico_solicitante.id in ID_ACUERDO_10

def tiene_acuerdo_al_40(estudio):
    return estudio.medico_solicitante.id in ID_ACUERDO_40

def tiene_acuerdo_al_50(estudio):
    return estudio.medico_solicitante.id in ID_ACUERDO_50

def tiene_acuerdo_al_80(estudio):
    return estudio.medico_solicitante.id in ID_ACUERDO_80
