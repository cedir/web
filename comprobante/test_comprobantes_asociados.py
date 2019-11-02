from django.test import TestCase
from comprobante.models import Comprobante

HTTP_BAD_REQUEST = 400

class TestComprobantesAsociados(TestCase):

    fixtures = ['comprobantes.json']

    def test_crear_comprobante_asociado(self):
        pass

    def test_obtener_comprobante_con_id_valido(self):
        
        comprobantes_list = Comprobante.objects.all()

        for i in range(1,len(comprobantes_list)):
            assert comprobantes_list[i] == obtener_comprobante_id(i)

    def test_obtener_comprobante_con_id_invalido(self):
        assert obtener_comprobante_id(232) == HTTP_BAD_REQUEST 
        assert obtener_comprobante_id(1000) == HTTP_BAD_REQUEST 

    def test_crear_comprobante(self):
        pass

    def test_crear_comprobante_afip(self):
        pass
