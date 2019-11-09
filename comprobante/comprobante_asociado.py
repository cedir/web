from datetime import date
from comprobante.models import Comprobante, TipoComprobante, LineaDeComprobante
from comprobante.afip import Afip, AfipError, AfipErrorRed, AfipErrorValidacion

from comprobante.models import ID_TIPO_COMPROBANTE_FACTURA, ID_TIPO_COMPROBANTE_FACTURA_CREDITO_ELECTRONICA, \
    ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO, ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO_ELECTRONICA, \
    ID_TIPO_COMPROBANTE_NOTA_DE_DEBITO, ID_TIPO_COMPROBANTE_NOTA_DE_DEBITO_ELECTRONICA

from comprobante.models import HTTP_BAD_REQUEST, HTTP_OK, HTTP_SERVER_ERROR

def tipos_comprobante_validos(id_comp_old, id_comp_new):
    if id_comp_old == ID_TIPO_COMPROBANTE_FACTURA:
        return id_comp_new == ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO or id_comp_new == ID_TIPO_COMPROBANTE_NOTA_DE_DEBITO
    elif id_comp_old == ID_TIPO_COMPROBANTE_FACTURA_CREDITO_ELECTRONICA:
        return id_comp_new == ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO_ELECTRONICA or id_comp_new == ID_TIPO_COMPROBANTE_NOTA_DE_DEBITO_ELECTRONICA
    else:
        return False

def es_factura(id_comp):
    return id_comp == ID_TIPO_COMPROBANTE_FACTURA or id_comp == ID_TIPO_COMPROBANTE_FACTURA_CREDITO_ELECTRONICA

def copiar_comprobante(comp, importe, id_tipo_comp, numero):
    return Comprobante(**{
            'nombre_cliente' : comp.nombre_cliente,
            'domicilio_cliente': comp.domicilio_cliente,
            'nro_cuit': comp.nro_cuit,
            'gravado_paciente': comp.gravado_paciente,
            'condicion_fiscal': comp.condicion_fiscal,
            'responsable': comp.responsable,
            'sub_tipo': comp.sub_tipo,
            'estado': 'PENDIENTE',
            'numero': numero,
            'nro_terminal': 91,
            'total_facturado': importe,
            'total_cobrado': '0.00',
            'fecha_emision': date.today(),
            'fecha_recepcion': date.today(),
            'tipo_comprobante': TipoComprobante.objects.get(pk = id_tipo_comp),
            'factura': comp,
            'gravado': comp.gravado,
        })

def crear_linea(comp, importe):
    return [LineaDeComprobante(**{
        'comprobante': comp,
        'importe_neto': importe,
        'sub_total': importe,
        'iva': 0,
    })]


def crear_comprobante_asociado(comp, importe, id_tipo_comp):
    if es_factura(id_tipo_comp) or not tipos_comprobante_validos(comp.tipo_comprobante.id, id_tipo_comp):
        raise TiposNoValidos

    afip = Afip()
    nro_siguiente = afip.consultar_proximo_numero(comp.responsable, comp.nro_terminal,TipoComprobante.objects.get(pk = id_tipo_comp), comp.sub_tipo)

    comprobante = copiar_comprobante(comp, importe, id_tipo_comp, nro_siguiente)

    lineas = crear_linea(comprobante, importe)

    afip.emitir_comprobante(comprobante,lineas)

    comprobante.save()

    return comprobante