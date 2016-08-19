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

    if not apply_changes:
        print u'Los cambios no se guardaran'
    
    presentacion = Presentacion.objects.get(pk=id_presentacion, estado=Presentacion.COBRADO)
    presentacion.estado = Presentacion.PENDIENTE
    # TODO: ver si hay que cambiar algo mas de presentacion, como total

    estudios = presentacion.estudios.all()
    for estudio in estudios:
        print '{}, {}, {}, {}, {}, {}'.format(estudio.id, estudio.fechaCobro, estudio.importeCobradoPension,
                                estudio.importeCobradoArancelAnestesia, estudio.importeEstudioCobrado,
                                estudio.importeMedicacionCobrado)
        estudio.fechaCobro = None
        estudio.importeCobradoPension = Decimal(0)
        estudio.importeCobradoArancelAnestesia = Decimal(0)
        estudio.importeEstudioCobrado = Decimal(0)
        estudio.importeMedicacionCobrado = Decimal(0)
        
        if apply_changes:
            estudio.save()

    pagos = presentacion.pago.all()
    assert pagos.count() == 1, u'Error, hay mas de un pago para esta presentacion'
    pago = pagos.first()
    print u'Eliminando pago {}'.format(pago.id)
    if apply_changes:
        pago.delete()

    print u'Fin.'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument(u'id_presentacion', help='')
    parser.add_argument(u'--apply-changes', dest=u'apply_changes', action=u'store_true', help=u'Apply Changes')
    args = parser.parse_args()
    
    anular_cobro_presentacion(args.id_presentacion, args.apply_changes)
