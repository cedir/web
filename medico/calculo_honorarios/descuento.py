from abc import abstractmethod

PARTICULAR = 2
PARTICULAR_ESPECIAL = 134
OSDE = 3
OSDE_CEDIR = 79
OS_UNR = 25
ACA_SALUD = 5
GALENO = 46
OSPAC = 19

ANALISIS_BIOQUIMICOS = 91
VIDEO_BAJA = 25
VIDEO_ALTA = 27
CONSULTA = 20
ELECTROCARDEOGRAMA = 46

DRENJUTO = 558

class Descuento(object):
    """
    Clase abstracta que representa un descuento al importe de un estudio.
    """
    @abstractmethod
    def aplicar(self, estudio, importe):
        """
        Calcula el nuevo importe luego de aplicar de un estudio luego de aplicar este descuento
        """
        pass
        
class DescuentoNulo(Descuento):
    """
    No se aplica ningun descuento al monto. Necesario para poder anular los descuentos con la menor modificacion posible
    al codigo de calculo de honorarios.
    """
    def aplicar(self, estudio, importe):
        return 0
        
class DescuentosVarios(Descuento):
    """
    Aplicar una lista de descuentos.
    """
    def __init__(self, *descuentos):
        self._descuentos = descuentos
        
    def aplicar(self, estudio, importe):
        return sum([des.aplicar(estudio, importe) for des in self._descuentos])
            
class DescuentosNoAcumulables(Descuento):
    """
    Se aplica solo el mayor descuento de una lista de posibles.
    """
    
    def __init__(self, *descuentos):
        self._descuentos = descuentos
        
    def aplicar(self, estudio, importe):
        return max([des.aplicar(estudio, importe) for des in self._descuentos])
        
        
class DescuentoColangios(Descuento):
    def aplicar(estudio, importe):
        if estudio.practica.id in (13, 14, 34):
            return 2000
        return 0


class DescuentoStent(Descuento):
    def aplicar(estudio, importe):
        if estudio.practica.id in (48, 49, 97):
            return 900
        return 0


class DescuentoRadiofrecuencia(Descuento):
    def aplicar(estudio, importe):
        if estudio.practica.id in (11, 17, 43):
            return 450
        return 0
        
        
class DescuentoPorPolipectomia(Descuento):
    def aplicar(estudio, importe):
        if estudio.practica.id not in []: # TODO: no se las ids estas o que criterio usar
            return 0
        
        if estudio.obra_social.id in (OSDE, OSDE_CEDIR):
            return 0
                    
        if estudio.obra_social.id in (OS_UNR, ACA_SALUD, GALENO, OSPAC):
            return 0
            
        return 300


class DescuentoEcografia(object):
    def aplicar(self, estudio, importe):
        if _es_ecografia(estudio):
            pass
        
    def _es_ecografia(self, estudio):
        # TODO
        pass
