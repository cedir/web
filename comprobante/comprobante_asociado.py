from datetime import date
from comprobante.models import Comprobante, TipoComprobante, LineaDeComprobante
from comprobante.afip import Afip

from comprobante.models import ID_TIPO_COMPROBANTE_FACTURA, ID_TIPO_COMPROBANTE_FACTURA_CREDITO_ELECTRONICA, \
    ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO, ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO_ELECTRONICA, \
    ID_TIPO_COMPROBANTE_NOTA_DE_DEBITO, ID_TIPO_COMPROBANTE_NOTA_DE_DEBITO_ELECTRONICA

HTTP_BAD_REQUEST = 400

def obtener_comprobante_id(id):
    try:
        return Comprobante.objects.get(pk = id)
    except:
        return HTTP_BAD_REQUEST
