from comprobante.models import Comprobante

HTTP_BAD_REQUEST = 400

def obtener_comprobante_id(id):
    try:
        return Comprobante.objects.get(pk = id)
    except:
        return HTTP_BAD_REQUEST
