from datetime import date
from comprobante.models import Comprobante, TipoComprobante, LineaDeComprobante
from comprobante.afip import Afip, AfipError, AfipErrorRed, AfipErrorValidacion

from comprobante.models import ID_TIPO_COMPROBANTE_FACTURA, ID_TIPO_COMPROBANTE_FACTURA_CREDITO_ELECTRONICA, \
    ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO, ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO_ELECTRONICA, \
    ID_TIPO_COMPROBANTE_NOTA_DE_DEBITO, ID_TIPO_COMPROBANTE_NOTA_DE_DEBITO_ELECTRONICA, \
    ID_TIPO_COMPROBANTE_LIQUIDACION


class TipoComprobanteAsociadoNoValidoException(Exception):
    pass

def _obtener_tipo_comprobante_asociado(id_tipo):
    dict_comp_asociados = {
        ID_TIPO_COMPROBANTE_FACTURA: ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO,
        ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO: ID_TIPO_COMPROBANTE_NOTA_DE_DEBITO,
        ID_TIPO_COMPROBANTE_NOTA_DE_DEBITO: ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO,
        ID_TIPO_COMPROBANTE_FACTURA_CREDITO_ELECTRONICA: ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO_ELECTRONICA,
        ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO_ELECTRONICA: ID_TIPO_COMPROBANTE_NOTA_DE_DEBITO_ELECTRONICA,
        ID_TIPO_COMPROBANTE_NOTA_DE_DEBITO_ELECTRONICA: ID_TIPO_COMPROBANTE_NOTA_DE_CREDITO_ELECTRONICA
    }

    return dict_comp_asociados[id_tipo]

def _es_factura(id_tipo_comp):
    return id_tipo_comp == ID_TIPO_COMPROBANTE_FACTURA or id_tipo_comp == ID_TIPO_COMPROBANTE_FACTURA_CREDITO_ELECTRONICA

def _crear_comprobante_similar(comp, importe, id_tipo_comp, numero):
    return Comprobante(**{
        'nombre_cliente' : comp.nombre_cliente,
        'domicilio_cliente': comp.domicilio_cliente,
        'nro_cuit': comp.nro_cuit,
        'gravado_paciente': comp.gravado_paciente,
        'condicion_fiscal': comp.condicion_fiscal,
        'responsable': comp.responsable,
        'sub_tipo': comp.sub_tipo,
        'estado': Comprobante.NO_COBRADO,
        'numero': numero,
        'nro_terminal': comp.nro_terminal,
        'total_facturado': importe,
        'total_cobrado': '0.00',
        'fecha_emision': date.today(),
        'fecha_recepcion': date.today(),
        'tipo_comprobante': TipoComprobante.objects.get(pk = id_tipo_comp),
        'factura': comp,
        'gravado': comp.gravado,
    })

def _crear_linea(comp, importe, concepto):
    return [LineaDeComprobante(**{
        'comprobante': comp,
        'concepto': concepto if concepto != '' else 'AJUSTA FACTURA {} No {}-{} SEGUN DEBITO APLICADO'.format(comp.sub_tipo, comp.nro_terminal, comp.numero),
        'importe_neto': importe,
        'sub_total': importe,
        'iva': 0,
    })]


def crear_comprobante_asociado(id_comp, importe, concepto):

    comp = Comprobante.objects.get(pk = id_comp)

    if comp.tipo_comprobante.id == ID_TIPO_COMPROBANTE_LIQUIDACION:
        raise TipoComprobanteAsociadoNoValidoException

    id_new_comp =  _obtener_tipo_comprobante_asociado(comp.tipo_comprobante.id)

    afip = Afip()

    nro_siguiente = afip.consultar_proximo_numero(
        comp.responsable,
        comp.nro_terminal,
        TipoComprobante.objects.get(pk = id_new_comp),
        comp.sub_tipo
    )

    comprobante = _crear_comprobante_similar(comp, importe, id_new_comp, nro_siguiente)

    lineas = _crear_linea(comprobante, importe, concepto)

    afip.emitir_comprobante(comprobante, lineas)

    comprobante.save()

    lineas[0].comprobante = Comprobante.objects.get(pk=comprobante.id)

    lineas[0].save()

    return comprobante