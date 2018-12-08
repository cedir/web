from abc import abstractproperty


def calculador_informe_factory(comprobante):
    if comprobante.tipo_comprobante.nombre in ["Factura", "Liquidacion", "Nota De Debito"]:
        return CalculadorInformeFactura(comprobante)
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
    def __init__(self, comprobante):
        self.comprobante = comprobante

    @property
    def honorarios_medicos(self):
        # self.context.get('calculador')
        # presentacion = comprobante.presentacion
        #
        # return presentacion.get_total_honorarios()
        #
        # # TODO: decir si mover esto a presentacion. Me parece que no debido a que solo se utiliza aca y no es atributo de Presentacion.
        # estudios = presentacion.estudios.all()
        #
        # total = 0
        # for estudio in estudios:
        #     honorario = calculate_honorario(estudio)
        #     total +=honorario
        #
        # return total
        return 0

    @property
    def anestesia(self):
        estudios  = self.comprobante.presentacion.estudios.all()
        return sum([estudio.arancel_anestesia for estudio in estudios])

    @property
    def retencion_impositiva(self):
        presentacion = self.comprobante.presentacion
        return presentacion.iva * presentacion.total_facturado

    @property
    def retencion_cedir(self):
        presentacion = self.comprobante.presentacion
        return presentacion.pago.gasto_administrativo

    @property
    def sala_recuperacion(self):
        estudios  = self.comprobante.presentacion.estudios.all()
        return sum([estudio.pension for estudio in estudios])

    @property
    def total_medicamentos(self):
        estudios  = self.comprobante.presentacion.estudios.all()
        return sum([estudio.get_total_medicacion() for estudio in estudios])

    @property
    def total_material_especifico(self):
        estudios  = self.comprobante.presentacion.estudios.all()
        return sum([estudio.importe_medicacion - estudio.get_total_medicacion() for estudio in estudios])


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
