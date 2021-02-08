import os
import sys
import django
sys.path.append(os.getcwd() + '/../../')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
django.setup()

import argparse
from datetime import datetime, date
from presentacion.models import PagoPresentacion
from estudio.models import Estudio

def actualizar_fechas_cobro_estudios(fecha, apply_changes):

    if not apply_changes:
        print('Los cambios no se guardaran')
    
    print(f'Se actualizaran los estudios de las presentaciones correspondientes entre las fechas {fecha} - {date.today()}')

    pago_presentaciones = list(PagoPresentacion.objects.filter(fecha__range=[fecha, date.today()]))

    if len(pago_presentaciones) > 0:
        assert pago_presentaciones[0].fecha >= datetime.strptime(fecha, '%Y-%m-%d').date()
    
    for pago_presentacion in pago_presentaciones:
        presentacion = pago_presentacion.presentacion
        estudios_cobrados = Estudio.objects.filter(fecha_cobro__isnull=True, presentacion=presentacion)

        if len(estudios_cobrados) > 0:
            print(f'Presentacion {presentacion.obra_social} - {presentacion.id}: Cantidad de estudios sin cobrar: {len(estudios_cobrados)}')            

        if apply_changes:
            estudios_actualizados = estudios_cobrados.update(fecha_cobro = presentacion.fecha)
            assert Estudio.objects.filter(fecha_cobro__isnull=True, presentacion=presentacion).count() == 0
    
    if apply_changes:
        print('Presentaciones actualizadas.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('fecha', help='')
    parser.add_argument('--apply-changes', dest='apply_changes', action='store_true', help='Apply Changes')
    args = parser.parse_args()
    
    actualizar_fechas_cobro_estudios(args.fecha, args.apply_changes)
