from abc import abstractmethod, abstractproperty


def create_calculador_informe(comprobante):
    if comprobante.tipo_comprobante.nombre in ["Factura", "Liquidacion", "Nota De Debito"]:  # REVISAR
        return CalculadorInformeFactura(comprobante)
    elif comprobante.tipo_comprobante.nombre == "Nota De Credito":
        return CalculadorInformeNotaCredito(comprobante)
    else:
        raise Exception(comprobante.tipo_comprobante.nombre)

        
class CalculardorInforme(object):
    @abstractproperty
    def honorarios_medicos(self):
        pass
    
    @abstractproperty
    def anestecia(self):
        pass
    
    @abstractproperty
    def retencion_impositiva(self):
        pass
    
    @abstractproperty
    def retencion_cedir(self):
        pass
    
    @abstractproperty
    def sala_recuperacion(self):
        pass
    
    @abstractproperty
    def total_medicamentos(self):
        pass
    
    @abstractproperty
    def total_material_especifico(self):
        pass

        
class CalculadorInformeFactura(object):
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
    def anestecia(self):
        return 0
        
    @property
    def retencion_impositiva(self):
        return 0
        
    @property
    def retencion_cedir(self):
        return 0
        
    @property
    def sala_recuperacion(self):
        presentacion = self.comprobante.presentacion.all().first()
        if not presentacion:
            return 0
        estudios = presentacion.estudios.all()
        total = 0
        for est in estudios:
            total += est.importe_cobrado_pension
        return total
        
    @property
    def total_medicamentos(self):
        presentacion = self.comprobante.presentacion.all().first()
        if not presentacion:
            return 0
        estudios = presentacion.estudios.all()
        total = 0
        for est in estudios:
            total += est.get_total_medicacion()
        return total
    
    @property
    def total_material_especifico(self):
        presentacion = self.comprobante.presentacion.all().first()
        if not presentacion:
            return 0
        estudios = presentacion.estudios.all()
        # TODO: ver que hacer en el caso de que la presentacion este cobrada y ya no tengamos el listado sino un total
        total = 0
        return total

        
class CalculadorInformeNotaCredito(object):
    def __init__(self, comprobante):
        self.comprobante = comprobante
    
    @property
    def honorarios_medicos(self):
        return 0
    
    @property
    def anestecia(self):
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

