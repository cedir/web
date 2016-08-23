import os
import sys
sys.path.append('/home/walter/Documents/cedir')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
import django
django.setup()

import argparse
from decimal import Decimal
from django.core import serializers
from comprobante.models import Comprobante
from presentacion.models import Presentacion


def anular_cobro_presentacion(id_presentacion, apply_changes):

    if not apply_changes:
        print u'Los cambios no se guardaran'
    
    presentacion = Presentacion.objects.get(pk=id_presentacion, estado=Presentacion.COBRADO)
    presentacion.estado = Presentacion.PENDIENTE
    presentacion.total = presentacion.total_facturado
    presentacion.comprobante.estado = Comprobante.NO_COBRADO
    presentacion.comprobante.total_cobrado = 0

    comprobante_relacionados = Comprobante.objects.filter(factura=presentacion.comprobante)
    assert len(comprobante_relacionados) <= 1, u'Mas de un comprobante relacionado'

    print u'presentacion {} comprobante {} comprobante relaionado {}'.format(presentacion.id, presentacion.comprobante.id,
                                                                             comprobante_relacionados.first())

    estudios = presentacion.estudios.all()
    for estudio in estudios:

        assert estudio.pago_medico_actuante == None, u'Error, pago medico actuante no es nulo'
        assert estudio.pago_medico_solicitante == None, u'Error, pago medico solicitante no es nulo'

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
    data = serializers.serialize("json", pagos)
    print data
    if apply_changes:
        pagos.delete()
        presentacion.save()
        presentacion.comprobante.save()

    print u'Fin.'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument(u'id_presentacion', help='')
    parser.add_argument(u'--apply-changes', dest=u'apply_changes', action=u'store_true', help=u'Apply Changes')
    args = parser.parse_args()
    
    anular_cobro_presentacion(args.id_presentacion, args.apply_changes)
