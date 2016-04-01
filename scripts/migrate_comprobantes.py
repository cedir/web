import argparse
import os
import sys
import datetime
sys.path.append('C:/Users/jiaguilera/Documents/source/web')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from comprobante.models import Comprobante, ComprobanteLinea, Gravado

import django
django.setup()


def migrate_comprobantes(apply_changes=False):
    print u'------------------Starting process at {}------------------'.format(datetime.datetime.now())

    if not apply_changes:
        print u'Los cambios no se guardaran'

    comprobantes = Comprobante.objects.all()

    for comprobante in comprobantes:
        gravado = comprobante.gravado.porcentajegravado if comprobante.gravado else 0
        lineas = comprobante.lineas.all()
        ivaTotal = 0

        for linea in lineas:
            if gravado:
                # gravado no es cero
                linea.importeneto = round((linea.subtotal * 100) / (100 + gravado), 2) #calculo el importe neto, dado el subtotal y el gravado
                linea.importeiva = linea.subtotal - linea.importeneto
            else:
                #gravado es cero
                linea.importeneto = linea.subtotal
                linea.importeiva = 0
            ivaTotal += linea.importeiva
            if apply_changes:
                linea.save()

        ivaTotalCalculado = (comprobante.totalfacturado * gravado) / (100 + gravado)
        if abs(ivaTotalCalculado - ivaTotal) > 0.1:
            print("En {0} IVA {1}% difiere. {2} {3}".format(comprobante.id, gravado, comprobante.totalfacturado, [(l.subtotal, l.importeiva, l.concepto) for l in lineas ]))

    print u'Done'



if __name__ == u'__main__':
    parser = argparse.ArgumentParser(description=u'Migrar comprobantes')
    parser.add_argument(u'--apply-changes',  dest=u'apply_changes', action=u'store_true', help=u'Apply changes')
    args = parser.parse_args()

    migrate_comprobantes(args.apply_changes)
