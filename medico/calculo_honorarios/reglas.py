from abc import abstractmethod, abstractproperty

from .descuento import DescuentosVarios, DescuentoColangios, DescuentoStent, \
                       DescuentoRadiofrecuencia, DescuentoPorPolipectomia
from .porcentajes import Porcentajes


class Reglas(object):
    """
    Reglas de negocio de calculo de honorarios para un tipo de facturacion.
    CalcHonorarios usa un heredero concreto para implementar cada
    paso de su algoritmo.
    Strategy: cada heredero debe definir una propiedad instancia de Descuento.
    """

    @abstractmethod
    def get_gastos_administrativos(self, estudio):
        """
        Calcular los gastos administrativos del estudio.
        """
        pass

    @abstractmethod
    def get_importe(self, estudio, gastos_administrativos):
        """
        Determinar cual es el importe que debe considerarse del estudio.
        """
        pass

    @abstractproperty
    def descuentos(self):
        """
        Los Descuento que deben aplicarse en este caso.
        """
        pass

    @abstractmethod
    def get_honorarios_medicos(self, estudio, importe):
        """
        Calcular los honorarios de cada medico.
        """
        pass


class ReglasPorPresentacion(Reglas):
    """
    Reglas de negocio para calcular sobre los montos cobrados de un
    estudio por presentacion.
    """

    def get_gastos_administrativos(self, estudio):

        presentacion = estudio.presentacion

        if presentacion.estado != presentacion.COBRADO:
            return 0

        pago = presentacion.pago.get()

        return estudio.importe_estudio_cobrado * pago.gasto_administrativo / 100

    def get_importe(self, estudio, gastos_administrativos):
        # Esta bien usar importe_estudio_cobrado???
        importe = estudio.importe
        if presentacion.estado == presentacion.COBRADO:
            importe = estudio.importe_estudio_cobrado
        return importe - gastos_administrativos

    @property
    def descuentos(self):
        return DescuentosVarios(
            DescuentoPorPolipectomia(),
            DescuentoColangios(),
            DescuentoStent(),
            DescuentoRadiofrecuencia())

    def get_honorarios_medicos(self, estudio, importe):
        porcentajes = Porcentajes(estudio)
        idactuante = estudio.medico_solicitante.id  # esto creo que lleva un get() o algo en el medio
        idsolicitante = estudio.medico_solicitante.id  # esto creo que lleva un get() o algo en el medio
        pago = {}

        pago[idactuante] = importe * porcentajes.actuante / 100
        if idsolicitante != idactuante:
            pago[idsolicitante] = importe * porcentajes.solicitante / 100


class ReglasPorPagoContraFactura(Reglas):
    """
    Reglas de negocio cuando el estudio ES pago contra factura.
    """

    def get_gastos_administrativos(self, estudio):
        return 0

    def get_importe(self, estudio, gastos_administrativos):
        return estudio.pago_contra_factura

    @property
    def descuentos(self):
        return DescuentosVarios(
            DescuentoPorPolipectomia(),
            DescuentoColangios(),
            DescuentoStent(),
            DescuentoRadiofrecuencia())

    def get_honorarios_medicos(self, estudio, importe):
        porcentajes = Porcentajes(estudio)
        porcentajes.actuante = 100 - porcentajes.actuante
        # Logica para hacerlo 0
        idactuante = estudio.medico_solicitante.id  # esto creo que lleva un get() o algo en el medio
        idsolicitante = estudio.medico_solicitante.id  # esto creo que lleva un get() o algo en el medio
        pago = {}

        pago[idactuante] = -(importe * porcentajes.actuante / 100 + self.descuentos.aplicar(estudio, importe))
        if idsolicitante != idactuante:
            pago[idsolicitante] = importe * porcentajes.solicitante / 100


class ReglasPorFacturado(Reglas):
    """
    Reglas de negecio para calcular sobre los montos facturados de un estudio.
    """
    def get_gastos_administrativos(self, estudio):
        pass

    def get_importe(self, estudio, gastos_administrativos):
        pass

    @property
    def descuentos(self):
        pass

    def get_honorarios_medicos(self, estudio, importe):
        pass
