from abc import abstractproperty
from decimal import Decimal

from django.core.exceptions import ObjectDoesNotExist

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
        return Decimal("0.00")

    @property
    def anestesia(self):
        presentacion = self.comprobante.presentacion.all().first()
        if not presentacion:
            return Decimal("0.00")
        estudios = presentacion.estudios.all()
        return sum([estudio.arancel_anestesia for estudio in estudios])

    @property
    def retencion_impositiva(self):
        presentacion = self.comprobante.presentacion.all().first()
        if not presentacion:
            return Decimal("0.00")
        if not presentacion.iva:
            # Algunas presentacionines tienen IVA = Null. Para estos casos, consideramos que debia ser 0.
                return Decimal("0.00")
        return presentacion.iva * presentacion.total_facturado / Decimal("100.00")

    @property
    def retencion_cedir(self):
        '''
        La retencion del cedir depende se guarda en el pago de la presentacion y esos casos conviene sacarla de ahi.
        Pero si no hay pago, es segun Mariana, "un valor fijo que no cambia seguido" y se puede decidir aca.
        Hay que mover esta logica cuando hagamos facturacion, para no duplicar.
        '''
        presentacion = self.comprobante.presentacion.all().first()
        if not presentacion:
            return Decimal("0.00")
        try:
            return presentacion.pago.get().gasto_administrativo * presentacion.total_facturado / Decimal("100.00")
        except ObjectDoesNotExist:
            if presentacion.obra_social.se_presenta_por_AMR == "1":
                # Resulta que bool("0") es True. TODO: arreglar esto, en el model o en algun lado.
                return Decimal("32.00") * presentacion.total_facturado / Decimal("100.00")
            return Decimal("25.00") * presentacion.total_facturado / Decimal("100.00")

    @property
    def sala_recuperacion(self):
        presentacion = self.comprobante.presentacion.all().first()
        if not presentacion:
            return Decimal("0.00")
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
            return Decimal("0.00")
        estudios = presentacion.estudios.all()
        return sum([aux(estudio) for estudio in estudios])

    @property
    def total_material_especifico(self):
        def aux(est):
            try:
                return est.get_total_material_especifico()
            except NotImplementedError:
                return Decimal("0.00")
        presentacion = self.comprobante.presentacion.all().first()
        if not presentacion:
            return Decimal("0.00")
        estudios = presentacion.estudios.all()
        return sum([aux(estudio) for estudio in estudios])


class CalculadorInformeNotaDebito(CalculadorInformeFactura):
    pass


class CalculadorInformeNotaCredito(CalculadorInforme):
    def __init__(self, comprobante):
        self.comprobante = comprobante

    @property
    def honorarios_medicos(self):
        return Decimal("0.00")

    @property
    def anestesia(self):
        return Decimal("0.00")

    @property
    def retencion_impositiva(self):
        return Decimal("0.00")

    @property
    def retencion_cedir(self):
        return Decimal("0.00")

    @property
    def sala_recuperacion(self):
        return Decimal("0.00")

    @property
    def total_medicamentos(self):
        return Decimal("0.00")

    @property
    def total_material_especifico(self):
        return Decimal("0.00")
