
from .imp import CalculadorPorPagoContraFactura, CalculadorPorPresentacion


class CalculadorHonorarios():
    """
    Dado un estudio, aplica todas las reglas de negocio para calcular los honorarios de los medicos.
    Template (una variante con composicion en vez de herencia): Los detalles de cada regla quedan
    a cargo de un ImpCalcHonorarios concreto, dependiendo de como se facturo el estudio.
    """
    def __init__(self, estudio):
        if estudio.es_pago_contra_factura:
            imp = CalculadorPorPagoContraFactura()
        else:
            imp = CalculadorPorPresentacion()

        # gastos_administrativos = imp.gastos_administrativos(estudio)
        # importe = imp.importe(estudio, gastos_administrativos)
        # importe_actualizado = max(0, importe - imp.descuentos.aplicar(estudio, importe))
        # self._pagos_correspondientes = imp.correspondientes(estudio, importe_actualizado)

    def total(self):
        # return sum(self._pagos_correspondientes.values())

        return 35

    def correspondiente(self, medico):
        return self._pagos_correspondientes[medico.id]