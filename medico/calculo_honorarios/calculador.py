from abc import abstractmethod, abstractproperty
from decimal import Decimal
from .porcentajes import Porcentajes
from .descuento import DescuentosVarios, DescuentoColangios, DescuentoStent, DescuentoRadiofrecuencia, \
                       DescuentoPorPolipectomia, DescuentosPorPolicolangio


class CalculadorHonorarios(object):
    '''
    Clase abstracta.
    Dado un estudio, aplica todas las reglas de negocios correspondientes para calcular los honorarios de los medicos implicados en el mismo.
    Es responsabilidad del heredero de esta clase elegir implementar sus reglas especificas segun en que contexto se esta calculando.
    '''
    def __init__(self, estudio):
        self.estudio = estudio
        self.calcular()

    @abstractmethod
    def get_importe(self, estudio):
        raise NotImplementedError

    @abstractproperty
    def descuentos(self):
        raise NotImplementedError

    def porcentaje_GA(self, estudio):
        # TODO: Esto es un logica comun con CalculadorInforme y hay que moverlo a.... Obra Social?
        if estudio.obra_social.se_presenta_por_AMR == "1":
            return Decimal("32.00")
        return Decimal("25.00")

    def calcular(self):
        '''
        Logica principal comun para todos los casos.
        Los honorarios de un medico siempre se calculan de la siguiente forma:
        1) Se busca el importe adecuado del estudio y se calcula la retención.
        2) Se realizan los descuentos que correspondan.
        3) Se asignan los honorarios de cada medico segun los porcentajes que
          apliquen.
        '''
        estudio = self.estudio
        porcentaje_GA = self.porcentaje_GA(estudio)

        importe_estudio = self.get_importe()
        importe_descuentos = self.descuentos.aplicar(estudio, importe_estudio)
        self.total_honorarios = importe_estudio * (Decimal('100.00') - porcentaje_GA) / Decimal('100.00') - importe_descuentos


class CalculadorHonorariosInformeContadora(CalculadorHonorarios):
    '''
    En el informe de la contadora se utilizan siempre los valores facturados.
    Ademas, no nos interesa saber los honorarios de un medico particular,
    solo el total de honorarios.
    '''
    def get_importe(self):
        return self.estudio.importe_estudio - self.estudio.diferencia_paciente

    @property
    def descuentos(self):
        # Aca posta no hay mas descuentos? mmmmm...   (CalculadorHonorariosComprobantes.vb L79)
        return DescuentosPorPolicolangio()

    @property
    def total(self):
        porcentajes = Porcentajes(self.estudio)
        return self.total_honorarios * (porcentajes.actuante + porcentajes.solicitante) / Decimal('100.00')


class CalculadorHonorariosPagoMedico(CalculadorHonorarios):
    '''
    En el caso de un pago a un medico, las reglas a usar dependeran de como se
    facturo el estudio.
    Si la facturacion la realiza el cedir, se calcula a partir de los valores
    cobrados, cuanto recibe el medico en honorarios.
    Si el estudio es pago contra factura, se calcula cuanto debe pagar el
    medico al cedir.
    '''
    def get_importe(self):
        estudio = self.estudio
        if estudio.es_pago_contra_factura:
            return estudio.pago_contra_factura
        else:
            return estudio.importe_estudio_cobrado

    @property
    def descuentos(self):
        return DescuentosVarios(
            DescuentoPorPolipectomia(),
            DescuentoColangios(),
            DescuentoStent(),
            DescuentoRadiofrecuencia())

    @property
    def actuante(self):
        estudio = self.estudio
        importe = self.importe
        porcentajes = Porcentajes(estudio)
        if estudio.es_pago_contra_factura:
            return -(importe * porcentajes.actuante / Decimal('100.00') + self.descuentos.aplicar(estudio, importe))
        else:
            return importe * porcentajes.actuante / Decimal('100.00')

    @property
    def solicitante(self):
        estudio = self.estudio
        importe = self.importe
        porcentajes = Porcentajes(estudio)
        return importe * porcentajes.solicitante / Decimal('100.00')
