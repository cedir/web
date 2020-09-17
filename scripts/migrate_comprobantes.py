import argparse
import os
import sys
import datetime
sys.path.append('C:/Users/jiaguilera/Documents/source/web')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from comprobante.models import Comprobante, LineaDeComprobante, Gravado

import django
django.setup()


def migrate_comprobantes(apply_changes=False):
    print('------------------Starting process at {}------------------'.format(datetime.datetime.now()))

    if not apply_changes:
        print('Los cambios no se guardaran')

    comprobantes = Comprobante.objects.all()

    for comprobante in comprobantes:
        gravado = comprobante.gravado.porcentaje if comprobante.gravado else 0
        lineas = comprobante.lineas.all()
        ivaTotal = 0

        for linea in lineas:
            if gravado:
                # gravado no es cero
                linea.importe_neto = round((linea.sub_total * 100) / (100 + gravado), 2) #calculo el importe neto, dado el subtotal y el gravado
                linea.importe_iva = linea.sub_total - linea.importe_neto
            else:
                #gravado es cero
                linea.importe_neto = linea.sub_total
                linea.importe_iva = 0
            ivaTotal += linea.importe_iva
            if apply_changes:
                linea.save()

        ivaTotalCalculado = (comprobante.total_facturado * gravado) / (100 + gravado)
        if abs(ivaTotalCalculado - ivaTotal) > 0.1:
            print(("En {0} IVA {1}% difiere. {2} {3}".format(comprobante.id, gravado, comprobante.total_facturado, [(l.sub_total, l.importe_iva, l.concepto) for l in lineas ])))

    print('Done')



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Migrar comprobantes')
    parser.add_argument('--apply-changes',  dest='apply_changes', action='store_true', help='Apply changes')
    args = parser.parse_args()

    migrate_comprobantes(args.apply_changes)
