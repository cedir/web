from abc import abstractproperty
from decimal import Decimal

from medico.calculo_honorarios import CalculadorHonorariosInformeContadora
from comprobante.models import LineaDeComprobante, ID_TIPO_COMPROBANTE_FACTURA, \
    ID_TIPO_COMPROBANTE_LIQUIDACION, ID_TIPO_COMPROBANTE_NOTA_DE_DEBITO, \
    ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO, ID_TIPO_COMPROBANTE_FACTURA_CREDITO_ELECTRONICA, \
    ID_TIPO_COMPROBANTE_NOTA_DE_DEBITO_ELECTRONICA, ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO_ELECTRONICA

def calculador_informe_factory(comprobante):
    if comprobante.tipo_comprobante.id == ID_TIPO_COMPROBANTE_FACTURA:
        return CalculadorInformeFactura(comprobante)
    elif comprobante.tipo_comprobante.id == ID_TIPO_COMPROBANTE_LIQUIDACION:
        return CalculadorInformeFactura(comprobante)
    elif comprobante.tipo_comprobante.id == ID_TIPO_COMPROBANTE_NOTA_DE_DEBITO:
        return CalculadorInformeFactura(comprobante)
    elif comprobante.tipo_comprobante.id == ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO:
        return CalculadorInformeNotaCredito(comprobante)
    elif comprobante.tipo_comprobante.id == ID_TIPO_COMPROBANTE_FACTURA_CREDITO_ELECTRONICA:
        return CalculadorInformeFactura(comprobante)
    elif comprobante.tipo_comprobante.id == ID_TIPO_COMPROBANTE_NOTA_DE_DEBITO_ELECTRONICA:
        return CalculadorInformeFactura(comprobante)
    elif comprobante.tipo_comprobante.id == ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO_ELECTRONICA:
        return CalculadorInformeNotaCredito(comprobante)
    else:
        raise Exception(comprobante.tipo_comprobante.nombre)


class CalculadorInforme(object):
    @abstractproperty
    def total_facturado(self):
        raise NotImplementedError

    @abstractproperty
    def neto(self):
        raise NotImplementedError

    @abstractproperty
    def iva(self):
        raise NotImplementedError

    @abstractproperty
    def honorarios_anestesia(self):
        raise NotImplementedError

    @abstractproperty
    def retencion_anestesia(self):
        raise NotImplementedError

    @abstractproperty
    def retencion_impositiva(self):
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

    @abstractproperty
    def honorarios_medicos(self):
        raise NotImplementedError

    @abstractproperty
    def honorarios_solicitantes(self):
        raise NotImplementedError

    @abstractproperty
    def retencion_cedir(self):
        raise NotImplementedError

    @abstractproperty
    def uso_de_materiales(self):
        raise NotImplementedError


class CalculadorInformeFactura(CalculadorInforme):
    '''
    En todos los casos, se toman los importes FACTURADOS.
    '''
    def __init__(self, comprobante):
        self.comprobante = comprobante
        self.presentacion = self.comprobante.presentacion.first()
        self.lineas = LineaDeComprobante.objects.filter(comprobante=self.comprobante)
        if self.presentacion is not None:
            self.estudios = self.presentacion.estudios.all()
            self.calculadores_honorarios = [CalculadorHonorariosInformeContadora(estudio) for estudio in self.estudios]

    @property
    def total_facturado(self):
        return self.comprobante.total_facturado

    @property
    def neto(self):
        return sum([l.importe_neto for l in self.lineas])

    @property
    def iva(self):
        return sum([l.iva for l in self.lineas])

    @property
    def honorarios_anestesia(self):
        if not self.presentacion:
            return Decimal("0.00")
        return sum([estudio.arancel_anestesia * (1 - estudio.retencion_impositiva) for estudio in self.estudios]) * Decimal('0.9')

    @property
    def retencion_anestesia(self):
        if not self.presentacion:
            return Decimal("0.00")
        return sum([estudio.arancel_anestesia * (1 - estudio.retencion_impositiva) for estudio in self.estudios]) * Decimal('0.1')

    @property
    def honorarios_medicos(self):
        if not self.presentacion:
            return Decimal("0.00")
        return sum([calculador.actuante for calculador in self.calculadores_honorarios])

    @property
    def honorarios_solicitantes(self):
        if not self.presentacion:
            return Decimal("0.00")
        return sum([calculador.solicitante for calculador in self.calculadores_honorarios])

    @property
    def retencion_cedir(self):
        if not self.presentacion:
            return Decimal("0.00")
        return sum([calculador.cedir for calculador in self.calculadores_honorarios])

    @property
    def uso_de_materiales(self):
        if not self.presentacion:
            return Decimal("0.00")
        return sum([calculador.uso_de_materiales for calculador in self.calculadores_honorarios])

    @property
    # gasto administrativo
    def retencion_impositiva(self):
        if not self.presentacion:
            return Decimal("0.00")
        if self.presentacion.obra_social.se_presenta_por_AMR == "1" or self.presentacion.obra_social.se_presenta_por_AMR == 1:
            return Decimal("32.00") * self.presentacion.total_facturado / Decimal("100.00")
        return Decimal("25.00") * self.presentacion.total_facturado / Decimal("100.00")

    @property
    def sala_recuperacion(self):
        if not self.presentacion:
            return Decimal("0.00")
        return sum([estudio.pension * (1 - estudio.retencion_impositiva) for estudio in self.estudios])

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
        if not self.presentacion:
            return Decimal("0.00")
        return sum([aux(estudio) * (1 - estudio.retencion_impositiva) for estudio in self.estudios])

    @property
    def total_material_especifico(self):
        def aux(est):
            try:
                return est.get_total_material_especifico()
            except NotImplementedError:
                return Decimal("0.00")
        if not self.presentacion:
            return Decimal("0.00")
        return sum([aux(estudio) * (1 - estudio.retencion_impositiva) for estudio in self.estudios])

class CalculadorInformeNotaCredito(CalculadorInforme):
    """
    Las notas de credito tienen la misma logica que las facturas pero los valores se muestran en negativo.
    Por lo tanto, definimos esta clase que aplica la logica de un calculador de facturas pero devuelve el valor negativo.
    """
    def __init__(self, comprobante):
        self.comprobante = comprobante
        self.calculador_aux = CalculadorInformeFactura(comprobante)

    @property
    def total_facturado(self):
        return Decimal("-1") * self.calculador_aux.total_facturado

    @property
    def neto(self):
        return Decimal("-1") * self.calculador_aux.neto

    @property
    def iva(self):
        return Decimal("-1") * self.calculador_aux.iva

    @property
    def honorarios_medicos(self):
        return Decimal("-1") * self.calculador_aux.honorarios_medicos

    @property
    def honorarios_solicitantes(self):
        return Decimal("-1") * self.calculador_aux.honorarios_solicitantes

    @property
    def retencion_cedir(self):
        return Decimal("-1") * self.calculador_aux.retencion_cedir

    @property
    def uso_de_materiales(self):
        return Decimal("-1") * self.calculador_aux.uso_de_materiales

    @property
    def honorarios_anestesia(self):
        return Decimal("-1") * self.calculador_aux.honorarios_anestesia

    @property
    def retencion_anestesia(self):
        return Decimal("-1") * self.calculador_aux.retencion_anestesia

    @property
    def retencion_impositiva(self):
        return Decimal("-1") * self.calculador_aux.retencion_impositiva

    @property
    def sala_recuperacion(self):
        return Decimal("-1") * self.calculador_aux.sala_recuperacion

    @property
    def total_medicamentos(self):
        return Decimal("-1") * self.calculador_aux.total_medicamentos

    @property
    def total_material_especifico(self):
        return Decimal("-1") * self.calculador_aux.total_material_especifico
