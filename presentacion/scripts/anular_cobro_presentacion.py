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
        print('Los cambios no se guardaran')
    
    presentacion = Presentacion.objects.get(pk=id_presentacion, estado=Presentacion.COBRADO)
    presentacion.estado = Presentacion.PENDIENTE
    presentacion.total = presentacion.total_facturado
    presentacion.comprobante.estado = Comprobante.NO_COBRADO
    presentacion.comprobante.total_cobrado = 0

    comprobante_relacionados = Comprobante.objects.filter(factura=presentacion.comprobante)
    assert len(comprobante_relacionados) <= 1, 'Mas de un comprobante relacionado'

    print('presentacion {} comprobante {} comprobante relaionado {}'.format(presentacion.id, presentacion.comprobante.id,
                                                                             comprobante_relacionados.first()))

    estudios = presentacion.estudios.all()
    for estudio in estudios:

        assert estudio.pago_medico_actuante == None, 'Error, pago medico actuante no es nulo'
        assert estudio.pago_medico_solicitante == None, 'Error, pago medico solicitante no es nulo'

        print('{}, {}, {}, {}, {}, {}'.format(estudio.id, estudio.fecha_cobro, estudio.importe_cobrado_pension,
                                estudio.importe_cobrado_arancel_anestesia, estudio.importe_estudio_cobrado,
                                estudio.importe_medicacion_cobrado))
        estudio.fecha_cobro = None
        estudio.importe_cobrado_pension = Decimal(0)
        estudio.importe_cobrado_arancel_anestesia = Decimal(0)
        estudio.importe_estudio_cobrado = Decimal(0)
        estudio.importe_medicacion_cobrado = Decimal(0)
        
        if apply_changes:
            estudio.save()

    pagos = presentacion.pago.all()
    assert pagos.count() == 1, 'Error, hay mas de un pago para esta presentacion'
    data = serializers.serialize("json", pagos)
    print(data)
    if apply_changes:
        pagos.delete()
        presentacion.save()
        presentacion.comprobante.save()

    print('Fin.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('id_presentacion', help='')
    parser.add_argument('--apply-changes', dest='apply_changes', action='store_true', help='Apply Changes')
    args = parser.parse_args()
    
    anular_cobro_presentacion(args.id_presentacion, args.apply_changes)
