from abc import abstractproperty
from decimal import Decimal


def calculador_informe_factory(comprobante):
    if comprobante.tipo_comprobante.nombre in "Factura":
        return CalculadorInformeFactura(comprobante)
    elif comprobante.tipo_comprobante.nombre == "Nota De Debito":
        return CalculadorInformeNotaDebito(comprobante)
    elif comprobante.tipo_comprobante.nombre == "Nota De Credito":
        return CalculadorInformeNotaCredito(comprobante)
    else:
        raise Exception(comprobante.tipo_comprobante.nombre)


class CalculadorInforme(object):
    @abstractproperty
    def honorarios_medicos(self):
        raise NotImplementedError

    @abstractproperty
    def anestesia(self):
        raise NotImplementedError

    @abstractproperty
    def retencion_impositiva(self):
        raise NotImplementedError

    @abstractproperty
    def retencion_cedir(self):
        raise NotImplementedError

    @abstractproperty
    def sala_recuperacion(self):
        raise NotImplementedError

    @abstractproperty
    def total_medicamentos(self):
        raise NotImplementedError

    @abstractproperty
    def total_material_especifico(self):
        raise NotImplementedError


class CalculadorInformeFactura(CalculadorInforme):
    '''
    En todos los casos, se toman los importes FACTURADOS.
    '''
    def __init__(self, comprobante):
        self.comprobante = comprobante

    @property
    def honorarios_medicos(self):
        # No implementado aun.
        return 0

    @property
    def anestesia(self):
        presentacion = self.comprobante.presentacion.all().first()
        if not presentacion:
            return 0
        estudios = presentacion.estudios.all()
        return sum([estudio.arancel_anestesia for estudio in estudios])

    @property
    def retencion_impositiva(self):
        presentacion = self.comprobante.presentacion.all().first()
        if not presentacion:
            return 0
        if not presentacion.iva:
            # Algunas presentacionines tienen IVA = Null. Para estos casos, consideramos que debia ser 0.
            return 0
        return presentacion.iva * presentacion.total_facturado / Decimal(100)

    @property
    def retencion_cedir(self):
        '''
        La retencion del cedir depende se guarda en el pago de la presentacion y esos casos conviene sacarla de ahi.
        Pero si no hay pago, es segun Mariana, "un valor fijo que no cambia seguido" y se puede decidir aca.
        Hay que mover esta logica cuando hagamos facturacion, para no duplicar.
        '''
        presentacion = self.comprobante.presentacion.all().first()
        if not presentacion:
            return 0
        if presentacion.pago:
            return presentacion.pago.get().gasto_administrativo * presentacion.total_facturado / Decimal(100)
        if presentacion.obra_social.se_presenta_por_AMR:
            return Decimal(32) * presentacion.total_facturado / Decimal(100)
        return Decimal(25) * presentacion.total_facturado / Decimal(100)

    @property
    def sala_recuperacion(self):
        presentacion = self.comprobante.presentacion.all().first()
        if not presentacion:
            return 0
        estudios = presentacion.estudios.all()
        return sum([estudio.pension for estudio in estudios])

    @property
    def total_medicamentos(self):
        '''
        Para las presentacion ya cobradas, se borran los registros que dividen los medicamentos por tipo y queda solo el
        total. En esos casos, se suma todo en esta columna y se deja en 0 el material especifico.
        Cuando implementemos facturacion aca, no vamos a eleminar ese registro y podemos corregir esto.
        '''
        def aux(est):
            try:
                return est.get_total_medicacion()
            except NotImplementedError:
                return est.importe_medicacion
        presentacion = self.comprobante.presentacion.all().first()
        if not presentacion:
            return 0
        estudios = presentacion.estudios.all()
        return sum([aux(estudio) for estudio in estudios])

    @property
    def total_material_especifico(self):
        def aux(est):
            try:
                return est.get_total_material_especifico()
            except NotImplementedError:
                return 0
        presentacion = self.comprobante.presentacion.all().first()
        if not presentacion:
            return 0
        estudios = presentacion.estudios.all()
        return sum([aux(estudio) for estudio in estudios])


class CalculadorInformeNotaDebito(CalculadorInformeFactura):
    pass


class CalculadorInformeNotaCredito(CalculadorInforme):
    def __init__(self, comprobante):
        self.comprobante = comprobante

    @property
    def honorarios_medicos(self):
        return 0

    @property
    def anestesia(self):
        return 0

    @property
    def retencion_impositiva(self):
        return 0

    @property
    def retencion_cedir(self):
        return 0

    @property
    def sala_recuperacion(self):
        return 0

    @property
    def total_medicamentos(self):
        return 0

    @property
    def total_material_especifico(self):
        return 0
