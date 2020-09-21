import os
import sys
sys.path.append('/home/walter/Documents/cedir')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
import django
django.setup()

import argparse
from datetime import datetime
from decimal import Decimal
from medico.models import PagoMedico


def eliminar_pagos(fecha, apply_changes):
    fecha = datetime.strptime(fecha, '%d/%m/%Y')

    pagos = PagoMedico.objects.filter(fecha__gte=fecha)
    for pago in pagos:
        importe_total = 0
        print('Empezando con pago {} del {} {}'.format(pago.id, pago.fecha, pago.medico))
        estudios_actuantes = pago.estudios_actuantes.all()
        for estudio in estudios_actuantes:
            importe_total += estudio.importe_pago_medico
            print('{}, {}, {}'.format(estudio.id, estudio.pago_medico_actuante.id, estudio.importe_pago_medico))
            estudio.importe_pago_medico = Decimal(0)
            estudio.pago_medico_actuante = None
            if apply_changes:
                estudio.save()

        print('Pagos solicitantes')
        estudios_solicitantes = pago.estudios_solicitantes.all()
        for estudio in estudios_solicitantes:
            importe_total += estudio.importe_pago_medico_solicitante
            print('{}, {}, {}'.format(estudio.id, estudio.pago_medico_solicitante.id, estudio.importe_pago_medico_solicitante))
            estudio.importe_pago_medico_solicitante = Decimal(0)
            estudio.pago_medico_solicitante = None
            if apply_changes:
                estudio.save()

        print('Total pago: {}'.format(importe_total))
        if apply_changes:
            print('Eliminando pago {}'.format(pago.id))
            pago.delete()

    print('Fin.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('fecha', help='')
    parser.add_argument('--apply-changes',  
                        dest='apply_changes', 
                        action='store_true', 
                        help='Apply Changes')
    args = parser.parse_args()
    
    eliminar_pagos(args.fecha, args.apply_changes)
