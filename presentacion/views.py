from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework.decorators import detail_route
from common.drf.views import StandardResultsSetPagination
from presentacion.models import Presentacion
from presentacion.serializers import PresentacionSerializer


class PresentacionViewSet(viewsets.ModelViewSet):
    queryset = Presentacion.objects.all().order_by('-fecha')
    serializer_class = PresentacionSerializer
    filter_fields = ('obra_social',)
    pagination_class = StandardResultsSetPagination
    page_size = 50

    @detail_route(methods=['get'])
    def get_detalle_osde(self, request, pk=None):

        presentacion = Presentacion.objects.get(pk=pk)

        csv_string = ''
        estudios = presentacion.estudios.all()

        for estudio in estudios:
            csv_string = '{}\n{}'.format(csv_string, _get_row_osde(estudio))

        response = HttpResponse(csv_string, content_type='text/csv')
        return response


def _get_row_osde(estudio):
    """
    espacios 0 1
    N Prestador	2	7
    N Afiliado	11	21
    Codigo Prestacion	25	30
    Tipo de Prestacion	31	31
    Cantidad de prestacion	43	45
    Fecha 	49	54
    Dlegacion Emisora	58	59
    N Orden	63	68
    Tipo de Orden	72	72
    Importe	76	90
    Letra Espec. Prescriptor	94	94
    N Matricula - Prescriptor	98	107
    Provincia de Matricula	111	111
    Letra Espec. Efector	115	115
    N Matricula - Efector	119	128
    Provincia de Matricula	132	132
    Transacion	136	141
    Prestador Prescriptor	145	150
    """
    nro_prestador_cedir = '051861'
    nro_afiliado = '{0:<11}'.format(estudio.paciente.nroAfiliado[:11])
    codigo_medico_osde = '{0:<6}'.format(estudio.practica.codigo_medico_osde[:6])
    tipo_prestacion = '1'  # ambulatorio
    cantidad = '001'
    fecha = estudio.fecha.strftime('%d%m%y')  # DDMMAA
    dlegacion_emisora = '00'
    nro_de_orden = '000000'
    tipo_orden = '0'
    importe = '{0:015}'.format(estudio.get_importe_total())
    letra_espec_efector = letra_espec_prescriptor = 'M'  #  El la letra que identifica la especialidad del profesional (M= medico, B= bioquimico, etc)
    nro_matricula_prescriptor = '{0:<10}'.format(estudio.medico_solicitante.matricula[:10])
    provincia_matricula = 'S'  # santa Fe
    nro_matricula_efector = '{0:<10}'.format(estudio.medico.matricula[:10])
    transacion = '{0:<6}'.format(estudio.nro_de_orden[:6])
    prestador_prescriptor = '000000'

    filas_1 = '{:<1}{}{:<3}{}{:<3}{}{}{:<11}{}{:<3}{}'.format('', nro_prestador_cedir, '', nro_afiliado, '',
                                                              codigo_medico_osde, tipo_prestacion, '', cantidad, '', fecha)
    filas_2 = '{:<3}{}{:<3}{}{:<3}{}{:<3}{}'.format('', dlegacion_emisora, '', nro_de_orden, '', tipo_orden, '', importe)
    filas_medico_solicitante = '{:<3}{}{:<3}{}{:<3}{}'.format('', letra_espec_prescriptor, '', nro_matricula_prescriptor, '', provincia_matricula)
    filas_medico_actuante = '{:<3}{}{:<3}{}{:<3}{}'.format('', letra_espec_efector, '', nro_matricula_efector, '', provincia_matricula)
    filas_final = '{:<3}{}{:<3}{}'.format('', transacion, '', prestador_prescriptor)

    return filas_1 + filas_2 + filas_medico_solicitante + filas_medico_actuante + filas_final
