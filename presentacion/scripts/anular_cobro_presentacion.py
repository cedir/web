import os
import sys
sys.path.append('/home/walter/Documents/cedir')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
import django
django.setup()

import argparse
from decimal import Decimal
from presentacion.models import Presentacion


def anular_cobro_presentacion(id_presentacion, apply_changes):
    
    presentacion = Presentacion.objects.get(pk=id_presentacion, estado=Presentacion.COBRADO)
    presentacion.estado = Presentacion.PENDIENTE
    # ver si hay que cambiar algo mas de presentacion

    estudios = presentacion.estudios.all()

    for estudio in estudios:
        estudio.fechaCobro = None
        estudio.importeCobradoPension = Decimal(0)
        estudio.importeCobradoArancelAnestesia = Decimal(0)
        estudio.importeEstudioCobrado = Decimal(0)
        estudio.importeMedicacionCobrado = Decimal(0)
        
        if apply_changes:
            estudio.save()


    if apply_changes:
        print u'Eliminando pago {}'.format(pago.id)
        pago.delete()

    print u'Fin.'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('id_presentacion', help='')
    parser.add_argument('--apply-changes', dest='apply_changes', action='store_true', help='Apply Changes')
    args = parser.parse_args()
    
    anular_cobro_presentacion(args.id_presentacion, args.apply_changes)

