
from .reglas import ReglasPorPagoContraFactura, ReglasPorPresentacion, \
                    ReglasPorFacturado


class CalculadorHonorarios():
    """
    Dado un estudio, aplica todas las reglas de negocios para calcular los
    honorarios de los medicos implicados en el mismo.
    Template (una variante con composicion en vez de herencia):
    Los detalles de cada regla quedan a cargo de un heredero de
    CalculadorHonorariosAbstracto, dependiendo de como se facturo
    el estudio.
    """
    def _calcular(self):
        gastos_administrativos = self.reglas.get_gastos_administrativos(self.estudio)
        importe = self.reglas.get_importe(self.estudio, gastos_administrativos)
        importe_actualizado = max(0, importe - self.reglas.descuentos.aplicar(self.estudio, importe))
        self.honorarios_medicos = self.reglas.get_honorarios_medicos(self.estudio, importe_actualizado)


class CalculadorHonorariosInformeContadora(CalculadorHonorarios):
    def __init__(self, estudio):
        self.reglas = ReglasPorFacturado()
        self._calcular()

    def total(self):
        return sum(self.honorarios_medicos.values())


class CalculadorHonorariosPagoMedico(CalculadorHonorarios):
    def __init__(self, estudio):
        self.estudio = estudio
        if estudio.es_pago_contra_factura:
            self.reglas = ReglasPorPagoContraFactura()
        else:
            self.reglas = ReglasPorPresentacion()
        self._calcular()

    def actuante(self):
        pass

    def solicitante(self):
        pass
