from abc import abstractmethod
from decimal import Decimal

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

COLANGIOS = (13, 14, 34)
STENT = (48, 49, 97)
RADIOFRECUENCIA = (11, 17, 43)
POLIPECTOMIA = (18, 19, 23, 24, 146, 147, 58)


class Descuento(object):
    """
    Clase abstracta que representa un descuento al importe de un estudio.
    La idea es que todos los descuentos implementen esta interfaz comun, de manera que si los descuentos cambiaran, estos cambios se puedan
    implementar de cambiando tan poco como se posible el codigo del calculador. Esto permite separar logica y no introducir (muchos) bugs.

    Los descuentos devuelven el monto a descontar. Toman el importe solo por si fuera necesario para el calculo del descuento.
    """
    @abstractmethod
    def aplicar(self, estudio, importe):
        """
        Calcula el monto que debe descontarse de un estudio.
        Esta funcion debe devolver 0 en los casos en los que el descuento no se aplica al estudio en cuestion.
        """
        pass


class DescuentoNulo(Descuento):
    """
    No se aplica ningun descuento al importe. Necesario para poder anular los descuentos con la menor modificacion posible
    al codigo de calculo de honorarios.
    """
    def aplicar(self, estudio, importe):
        return Decimal("0.00")


class DescuentosVarios(Descuento):
    """
    Calcular un descuento compuesto por la suma de una lista de descuentos.
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
    def aplicar(self, estudio, importe):
        if estudio.practica.id in COLANGIOS:
            return Decimal("2000.00")
        return Decimal("0.00")


class DescuentoStent(Descuento):
    def aplicar(self, estudio, importe):
        if estudio.practica.id in STENT:
            return Decimal("900.00")
        return Decimal("0.00")


class DescuentoRadiofrecuencia(Descuento):
    def aplicar(self, estudio, importe):
        if estudio.practica.id in RADIOFRECUENCIA:
            return Decimal("450.00")
        return Decimal("0.00")


class DescuentoPorPolipectomia(Descuento):
    def aplicar(self, estudio, importe):
        if estudio.practica.id not in POLIPECTOMIA:
            return Decimal("0.00")

        if estudio.obra_social.id in (OSDE, OSDE_CEDIR):
            return Decimal("0.00")

        if estudio.obra_social.id in (OS_UNR, ACA_SALUD, GALENO, OSPAC):
            return Decimal("0.00")

        return Decimal("300.00")
