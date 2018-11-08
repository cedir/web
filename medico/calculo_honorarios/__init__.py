from .imp import ImpPCF, ImpComun

__all__ = ['CalcHonorarios']


class CalcHonorarios():
    """
    Dado un estudio, aplica todas las reglas de negocio para calcular los honorarios de los medicos.
    Template (una variante con composicion en vez de herencia): Los detalles de cada regla quedan
    a cargo de un ImpCalcHonorarios concreto, dependiendo de como se facturo el estudio.
    """
    def __init__(self, estudio):
        if estudio.esPagoContraFactura:
            imp = ImpPCF()
        else:
            imp = ImpComun()
            
        gastos_administrativos = imp.gastos_administrativos(estudio)
        importe = imp.importe(estudio, gastos_administrativos)
        importe_actualizado = max(0, importe - imp.descuentos.aplicar(estudio, importe))
        self._pagos_correspondientes = imp.correspondientes(estudio, importe_actualizado)
    
    def totales(self):
        return sum(self._pagos_correspondientes.values())

    def correspondiente(self, medico):
        return self._pagos_correspondientes[medico.id]
        
