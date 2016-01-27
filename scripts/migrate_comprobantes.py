import argparse
import os
import sys
import datetime
sys.path.append('/home/wbrunetti/Documents/cedir')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from comprobante.models import Comprobante, LineaDeComprobante, Gravado

import django
django.setup()


def migrate_comprobantes(apply_changes=False):
    print u'------------------Starting process at {}------------------'.format(datetime.datetime.now())

    if not apply_changes:
        print u'Los cambios no se guardaran'

    comprobantes = Comprobante.objects.all()

    for comprobante in comprobantes:

        lineas = comprobante.lineas.all()

        if len(lineas) > 2 or len(lineas) == 0:
            print u'[WARN] Comprobante #{} tiene mas de 2 lineas o ninguna: {} lineas'.format(comprobante.id, len(lineas))
            continue
        try:
            linea_iva, linea_descripcion = get_lineas_iva_descripcion(lineas)
        except AssertionError as e:
            print u'[ERR] {}'.format(e)

        linea_descripcion.importe_neto = linea_descripcion.sub_total
        if linea_iva:
            linea_descripcion.iva = linea_iva.sub_total
            linea_descripcion.sub_total = linea_descripcion.importe_neto + linea_descripcion.iva

        if apply_changes:
            linea_descripcion.save()
            if linea_iva:
                linea_iva.delete()

    print u'Done'


def get_lineas_iva_descripcion(lineas):
    if len(lineas) == 1:
        return None, lineas[0]

    ivas = (u'IVA', u'iva', u'Iva')
    if lineas[0].sub_total > lineas[1].sub_total:
        assert bool([iva for iva in ivas if iva in lineas[1].concepto]), u'IVA no esta en el concepto: {}'.format(lineas[1].comprobante.id)
        return lineas[1], lineas[0]

    assert bool([iva for iva in ivas if iva in lineas[0].concepto]), u'IVA no esta en el concepto: {}'.format(lineas[0].id)
    assert lineas[1].sub_total > lineas[0].sub_total, u'Ambas lineas son iguales: {}'.format(lineas[0].comprobante.id)

    return lineas[1], lineas[0]



if __name__ == u'__main__':
    parser = argparse.ArgumentParser(description=u'Migrar comprobantes')
    parser.add_argument(u'--apply-changes',  dest=u'apply_changes', action=u'store_true', help=u'Apply changes')
    args = parser.parse_args()

    migrate_comprobantes(args.apply_changes)

