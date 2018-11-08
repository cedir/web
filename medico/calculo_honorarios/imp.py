from .descuento import DescuentosVarios, DescuentoColangios, DescuentoStent, DescuentoRadiofrecuencia \
                       DescuentoPorPolipectomia, 
from .porcentajes import Porcentajes


class ImpCalcHonorarios(ABC):
    """
    Reglas de negocio de calculo de honorarios para un tipo de facturación.
    CalcHonorarios usa un heredero concreto para implementar cada paso de su algoritmo.
    Strategy: cada heredero debe definir una propiedad instancia de Descuento.
    """
        
    @abstractmethod
    def gastos_administrativos(self, estudio):
        pass
    
    @abstractmethod
    def importe(self, estudio, gastos_administrativos):
        pass
    
    @abstractcmethod
    @property
    def descuentos(self):
        pass
            
    @abstractmethod
    def correspondientes(self, estudio, importe):
        pass
    
        
class ImpComun(ImpCalcHonorarios):
    """
    Reglas de negocio cuando el estudio NO es pago contra factura.
    """

    def gastos_administrativos(self, estudio):
        # TODO
        pass
    
    def importe(self, estudio, gastos_administrativos):
        # Esta bien usar importe_estudio_cobrado???
        return estudio.importe_estudio_cobrado - gastos_administrativos
    
    @property
    def descuentos(self):
        return DescuentosVarios(DescuentoPorPolipectomia(), DescuentoColangios(), DescuentoStent(), DescuentoRadiofrecuencia())
            
    def correspondientes(self, estudio, importe):
        porcentajes = Porcentajes(estudio)
        idactuante = estudio.medico_solicitante.id # esto creo que lleva un get() o algo en el medio
        idsolicitante = estudio.medico_solicitante.id # esto creo que lleva un get() o algo en el medio
        pago = {}
        
        pago[idactuante] = importe * porcentajes.actuante / 100
        if idsolicitante != idactuante:
            pago[idsolicitante] = importe * porcentajes.solicitante / 100


class ImpPCF(ImpCalcHonorarios):
    """
    Reglas de negocio cuando el estudio ES pago contra factura.
    """

    def gastos_administrativos(self, estudio):
        return 0
    
    def importe(self, estudio, gastos_administrativos):
        return estudio.pago_contra_factura
    
    @property
    def descuentos(self):
        return DescuentosVarios(DescuentoPorPolipectomia(), DescuentoColangios(), DescuentoStent(), DescuentoRadiofrecuencia())
            
            
    def correspondientes(self, estudio, importe):
        porcentajes = Porcentajes(estudio)
        porcentajes.actuante = 100 - porcentaje.actuante
        # Logica para hacerlo 0
        idactuante = estudio.medico_solicitante.id # esto creo que lleva un get() o algo en el medio
        idsolicitante = estudio.medico_solicitante.id # esto creo que lleva un get() o algo en el medio
        pago = {}
        
        pago[idactuante] = -(importe * porcentajes.actuante / 100 + self.descuentos.aplicar(estudio, importe))        
        if idsolicitante != idactuante:
            pago[idsolicitante] = importe * porcentajes.solicitante / 100


